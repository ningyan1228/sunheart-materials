# 阳光心材料

面向中国大陆企业客户的材料产品展示、资料申请与询盘系统。公开网站为 React + Vite 静态站点，API 为无状态 FastAPI 代理，业务数据、权限和文件均由 Supabase 承担。

## 本地启动

1. 复制 `.env.example` 为 `.env` 并按环境填写变量。
2. `pnpm install`，随后执行 `pnpm --filter @sunheart/web run build`。
3. 进入 `apps/api` 后执行 `python -m venv .venv`，激活环境并执行 `pip install -r requirements.txt`。
4. 在 Supabase SQL Editor 或 CLI 中按顺序运行 `supabase/migrations`，再运行 `supabase/seed.sql`。
5. 启动 API：`uvicorn app.main:app --reload --port 8000`；启动 Web：`npm run dev --workspace=@sunheart/web`。

详细上线、内容录入、SEO 与运维说明见 `docs/`。

## 安全边界

- 浏览器仅使用 Supabase URL/anon key；Service Role 只允许存在于 API 或受保护的 CI 环境。
- 公开页面只使用“阳光心材料”，面向中国大陆市场；不会显示出口交易条件、在线支付或未经审核的参数。
- 所有示例内容均为待审核结构示例，不能直接作为技术宣传或产品参数发布。
