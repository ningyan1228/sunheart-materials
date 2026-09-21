import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))
from fastapi.testclient import TestClient
from app.main import app


class ApiContractTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_is_public(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertIn("X-Request-Id", response.headers)

    def test_invalid_lead_is_rejected_before_any_upstream_write(self):
        response = self.client.post("/api/inquiries", json={
            "name": "张三", "company": "示例公司", "phone": "123", "provinceCity": "上海",
            "productOrApplication": "示例产品", "substrate": "织物", "currentProblem": "需要资料",
            "targetPerformance": "待确认", "services": ["TDS/SDS"], "privacyAccepted": False,
        })
        self.assertEqual(response.status_code, 422)

    def test_private_admin_endpoints_require_token(self):
        self.assertEqual(self.client.post("/api/admin/rebuild", json={}).status_code, 401)
        self.assertEqual(self.client.post("/api/documents/5aab0dfa-03f8-4cd5-b03f-972b2c203202/signed-url").status_code, 401)

    def test_upload_rejects_disallowed_type(self):
        response = self.client.post("/api/uploads/presign", json={"file_name": "unsafe.exe", "mime_type": "application/octet-stream", "bytes": 10})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
