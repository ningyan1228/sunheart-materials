# 部署说明

## GitHub Pages

1. 创建仓库后，在 GitHub Pages 的 Source 选择 **GitHub Actions**。
2. 将 `SITE_URL`、`SITE_BASE_PATH`、`SUPABASE_URL`、`SUPABASE_ANON_KEY`、`API_BASE_URL` 配置为仓库 Variables。自定义域名使用 `/`；项目页使用 `/仓库名/`。
3. 推送 `main` 后，`deploy-pages.yml` 只上传 `apps/web/dist`。构建会先读取 Supabase 中 `published` 状态的内容，再输出独立 HTML、搜索索引、Sitemap 和 Robots。
4. 配置自定义域名的 DNS 后，在 GitHub Pages 中验证 HTTPS；将 `VITE_SITE_URL` / `SITE_URL` 更新为最终 HTTPS 域名。

## API 服务器

1. 在轻量服务器克隆仓库，仅复制 `.env.example` 为 `.env` 并填写 API 私密变量。
2. 用 `docker compose up -d --build` 启动。反向代理将 HTTPS 域名转发到本机 `8000` 端口。
3. `ALLOWED_ORIGINS` 只填写正式域名和本地开发域名。不要将 Service Role、GitHub Token 或 JWT Secret 放进前端 Variables。
4. API 不使用本地业务数据库或持久文件；附件通过 Supabase Storage 的短时签名地址传输。管理员 Token 由 Supabase Auth 验证，兼容当前 ECC JWT Signing Key，无需配置旧版 JWT Secret。
