"""No-state API gateway: validation, rate control, Supabase forwarding and protected rebuilds."""
from __future__ import annotations

import asyncio
import html
import logging
import os
import re
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated, Literal

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, field_validator

logger = logging.getLogger("sunheart.api")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s")

SAFE_TEXT = re.compile(r"[<>]")
PHONE = re.compile(r"^1\d{10}$")
ALLOWED_UPLOAD_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class Settings:
    supabase_url: str = os.getenv("SUPABASE_URL", "").rstrip("/")
    service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_owner: str = os.getenv("GITHUB_OWNER", "")
    github_repo: str = os.getenv("GITHUB_REPO", "")
    workflow_id: str = os.getenv("GITHUB_WORKFLOW_ID", "deploy-pages.yml")
    allowed_origins: tuple[str, ...] = tuple(x.strip() for x in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if x.strip())


settings = Settings()


class RateLimiter:
    """Short-lived in-memory guard. It intentionally stores no form body or contact data."""
    def __init__(self, max_requests: int = 5, period_seconds: int = 600) -> None:
        self.max_requests, self.period = max_requests, period_seconds
        self.events: dict[str, deque[float]] = defaultdict(deque)
        self.lock = asyncio.Lock()

    async def check(self, key: str) -> None:
        now = time.monotonic()
        async with self.lock:
            bucket = self.events[key]
            while bucket and bucket[0] <= now - self.period:
                bucket.popleft()
            if len(bucket) >= self.max_requests:
                raise HTTPException(status_code=429, detail={"code": "RATE_LIMITED", "message": "提交过于频繁，请稍后再试。"})
            bucket.append(now)


rate_limiter = RateLimiter()


class LeadPayload(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    company: str = Field(min_length=1, max_length=120)
    phone: str
    wechat: str | None = Field(default=None, max_length=80)
    email: EmailStr | None = None
    provinceCity: str = Field(min_length=1, max_length=80)
    productOrApplication: str = Field(min_length=1, max_length=160)
    substrate: str = Field(min_length=1, max_length=120)
    currentProblem: str = Field(min_length=1, max_length=2000)
    targetPerformance: str = Field(min_length=1, max_length=1000)
    monthlyUsage: str | None = Field(default=None, max_length=100)
    services: list[Literal["TDS/SDS", "样品", "报价", "技术咨询"]] = Field(min_length=1)
    privacyAccepted: Literal[True]
    website: str | None = Field(default=None, max_length=0)  # Honeypot; never persisted.

    @field_validator("phone")
    @classmethod
    def mainland_phone(cls, value: str) -> str:
        if not PHONE.fullmatch(value.strip()):
            raise ValueError("请输入有效的中国大陆手机号")
        return value.strip()

    @field_validator("name", "company", "provinceCity", "productOrApplication", "substrate", "currentProblem", "targetPerformance", "wechat", "monthlyUsage", mode="before")
    @classmethod
    def clean_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = html.unescape(str(value)).strip()
        if SAFE_TEXT.search(cleaned):
            raise ValueError("文本不能包含 HTML 标签")
        return cleaned


class UploadRequest(BaseModel):
    file_name: str = Field(min_length=1, max_length=180)
    mime_type: str
    bytes: int = Field(gt=0, le=MAX_UPLOAD_BYTES)

    @field_validator("mime_type")
    @classmethod
    def allow_mime(cls, value: str) -> str:
        if value not in ALLOWED_UPLOAD_TYPES:
            raise ValueError("不支持的文件类型")
        return value


class DocumentRequest(BaseModel):
    document_id: uuid.UUID | None = None
    lead: LeadPayload


class RebuildRequest(BaseModel):
    reason: str = Field(default="content_publish", max_length=80)


class AnalyticsEvent(BaseModel):
    event_name: Literal["page_view", "product_view", "application_view", "search", "document_request", "sample_request", "quote_inquiry", "wechat_open", "phone_click"]
    entity_path: str = Field(default="", max_length=300)
    search_term: str | None = Field(default=None, max_length=100)

    @field_validator("entity_path", "search_term", mode="before")
    @classmethod
    def clean_event_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return html.unescape(str(value)).strip().replace("<", "").replace(">", "")


class SupabaseGateway:
    def _headers(self) -> dict[str, str]:
        if not settings.supabase_url or not settings.service_role_key:
            raise HTTPException(status_code=503, detail={"code": "SUPABASE_NOT_CONFIGURED", "message": "服务暂未配置，请通过联系方式咨询。"})
        return {"apikey": settings.service_role_key, "Authorization": f"Bearer {settings.service_role_key}", "Content-Type": "application/json"}

    async def insert(self, table: str, row: dict) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(f"{settings.supabase_url}/rest/v1/{table}", headers={**self._headers(), "Prefer": "return=representation"}, json=row)
        if response.is_error:
            logger.warning("supabase_write_failed table=%s status=%s", table, response.status_code)
            raise HTTPException(status_code=502, detail={"code": "UPSTREAM_WRITE_FAILED", "message": "提交暂未成功，请稍后再试。"})
        return response.json()[0]

    async def lookup_document(self, document_id: uuid.UUID) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{settings.supabase_url}/rest/v1/documents", headers=self._headers(), params={"id": f"eq.{document_id}", "select": "id,bucket,object_path,access_level"})
        if response.is_error or not response.json():
            raise HTTPException(status_code=404, detail={"code": "DOCUMENT_NOT_FOUND", "message": "未找到资料。"})
        return response.json()[0]

    async def signed_upload(self, object_path: str) -> str:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(f"{settings.supabase_url}/storage/v1/object/upload/sign/private-attachments/{object_path}", headers=self._headers())
        if response.is_error:
            raise HTTPException(status_code=502, detail={"code": "UPLOAD_SIGN_FAILED", "message": "暂时无法创建上传地址。"})
        return response.json()["url"]

    async def signed_download(self, bucket: str, object_path: str) -> str:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(f"{settings.supabase_url}/storage/v1/object/sign/{bucket}/{object_path}", headers=self._headers(), json={"expiresIn": 300})
        if response.is_error:
            raise HTTPException(status_code=502, detail={"code": "DOWNLOAD_SIGN_FAILED", "message": "暂时无法创建下载地址。"})
        return response.json()["signedURL"]


gateway = SupabaseGateway()


def request_key(request: Request, device_id: str | None) -> str:
    client_ip = request.client.host if request.client else "unknown"
    return f"{client_ip}:{(device_id or 'none')[:80]}"


def lead_row(payload: LeadPayload, request: Request) -> dict:
    # Only explicitly expected values are forwarded; honeypot, request headers and raw body are not stored.
    return {"name": payload.name, "company": payload.company, "phone": payload.phone, "wechat": payload.wechat or None, "email": str(payload.email) if payload.email else None, "province_city": payload.provinceCity, "product_or_application": payload.productOrApplication, "substrate": payload.substrate, "current_problem": payload.currentProblem, "target_performance": payload.targetPerformance, "monthly_usage": payload.monthlyUsage or None, "services": payload.services, "source_path": request.headers.get("referer", "")[:300], "utm": {key: request.query_params.get(key) for key in ("utm_source", "utm_medium", "utm_campaign") if request.query_params.get(key)}}


async def submit_lead(payload: LeadPayload, request: Request, device_id: str | None) -> dict:
    if payload.website:
        # Pretend success to avoid helping bots tune around the honeypot.
        return {"inquiry_id": "accepted", "request_id": "accepted"}
    await rate_limiter.check(request_key(request, device_id))
    return await gateway.insert("inquiries", lead_row(payload, request))


async def admin_claims(authorization: Annotated[str | None, Header()] = None) -> dict:
    """Delegate token verification to Supabase so current JWT signing keys (including ECC) work."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "需要管理员登录。"})
    headers = gateway._headers()
    async with httpx.AsyncClient(timeout=10) as client:
        auth_response = await client.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={"apikey": settings.service_role_key, "Authorization": authorization},
        )
        if auth_response.is_error:
            raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "登录状态无效。"})
        user_id = auth_response.json().get("id")
        profile_response = await client.get(
            f"{settings.supabase_url}/rest/v1/profiles",
            headers=headers,
            params={"id": f"eq.{user_id}", "is_active": "eq.true", "select": "role"},
        )
    if profile_response.is_error or not profile_response.json():
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "没有后台访问权限。"})
    role = profile_response.json()[0]["role"]
    if role not in {"owner", "editor", "sales", "viewer"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "没有此操作权限。"})
    return {"sub": user_id, "role": role}


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(title="阳光心材料 API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=list(settings.allowed_origins), allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type", "X-Device-Id", "X-Request-Id"])


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))[:64]
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed id=%s type=unhandled", request_id)
        return __import__("fastapi").responses.JSONResponse(status_code=500, content={"detail": {"code": "INTERNAL_ERROR", "message": "服务暂时不可用。"}}, headers={"X-Request-Id": request_id})
    logger.info("request_complete id=%s status=%s", request_id, response.status_code)
    response.headers["X-Request-Id"] = request_id
    return response


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/inquiries", status_code=status.HTTP_201_CREATED)
async def create_inquiry(payload: LeadPayload, request: Request, x_device_id: Annotated[str | None, Header()] = None):
    row = await submit_lead(payload, request, x_device_id)
    return {"inquiry_id": row.get("id", "accepted"), "request_id": row.get("request_number", "accepted")}


@app.post("/api/events", status_code=status.HTTP_202_ACCEPTED)
async def create_analytics_event(payload: AnalyticsEvent, request: Request, x_device_id: Annotated[str | None, Header()] = None):
    await rate_limiter.check(f"event:{request_key(request, x_device_id)}")
    await gateway.insert("analytics_events", {"event_name": payload.event_name, "entity_path": payload.entity_path, "search_term": payload.search_term, "source_path": request.headers.get("referer", "")[:300], "utm": {key: request.query_params.get(key) for key in ("utm_source", "utm_medium", "utm_campaign") if request.query_params.get(key)}})
    return {"status": "accepted"}


@app.post("/api/sample-requests", status_code=status.HTTP_201_CREATED)
async def create_sample_request(payload: LeadPayload, request: Request, x_device_id: Annotated[str | None, Header()] = None):
    lead = await submit_lead(payload, request, x_device_id)
    sample = await gateway.insert("sample_requests", {"inquiry_id": lead.get("id")}) if lead.get("id") else {"request_number": "accepted"}
    return {"inquiry_id": lead.get("id", "accepted"), "request_id": sample.get("request_number", "accepted")}


@app.post("/api/document-requests", status_code=status.HTTP_201_CREATED)
async def create_document_request(payload: LeadPayload, request: Request, x_device_id: Annotated[str | None, Header()] = None):
    lead = await submit_lead(payload, request, x_device_id)
    document = await gateway.insert("document_requests", {"inquiry_id": lead.get("id")}) if lead.get("id") else {"request_number": "accepted"}
    return {"inquiry_id": lead.get("id", "accepted"), "request_id": document.get("request_number", "accepted")}


@app.post("/api/uploads/presign")
async def create_upload_url(payload: UploadRequest, request: Request, x_device_id: Annotated[str | None, Header()] = None):
    await rate_limiter.check(request_key(request, x_device_id))
    extension = payload.file_name.rsplit(".", 1)[-1].lower() if "." in payload.file_name else "bin"
    if extension not in {"pdf", "jpg", "jpeg", "png", "webp"}:
        raise HTTPException(status_code=400, detail={"code": "FILE_EXTENSION_INVALID", "message": "不支持的文件扩展名。"})
    object_path = f"incoming/{uuid.uuid4()}.{extension}"
    return {"object_path": object_path, "signed_url": await gateway.signed_upload(object_path), "expires_in": 300}


@app.post("/api/documents/{document_id}/signed-url")
async def create_document_url(document_id: uuid.UUID, _: dict = Depends(admin_claims)):
    document = await gateway.lookup_document(document_id)
    if document["access_level"] == "internal":
        raise HTTPException(status_code=403, detail={"code": "DOCUMENT_PRIVATE", "message": "该资料仅限内部访问。"})
    return {"signed_url": await gateway.signed_download(document["bucket"], document["object_path"]), "expires_in": 300}


@app.post("/api/admin/rebuild", status_code=status.HTTP_202_ACCEPTED)
async def rebuild(_: RebuildRequest, claims: dict = Depends(admin_claims)):
    if claims["role"] not in {"owner", "editor"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "没有发布权限。"})
    if not all((settings.github_token, settings.github_owner, settings.github_repo)):
        raise HTTPException(status_code=503, detail={"code": "GITHUB_NOT_CONFIGURED", "message": "发布服务尚未配置。"})
    url = f"https://api.github.com/repos/{settings.github_owner}/{settings.github_repo}/actions/workflows/{settings.workflow_id}/dispatches"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(url, headers={"Authorization": f"Bearer {settings.github_token}", "Accept": "application/vnd.github+json"}, json={"ref": "main", "inputs": {"reason": "content_publish"}})
    if response.status_code != 204:
        logger.warning("github_dispatch_failed status=%s", response.status_code)
        raise HTTPException(status_code=502, detail={"code": "REBUILD_FAILED", "message": "未能触发重建。"})
    return {"status": "queued"}
