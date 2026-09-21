# 开发验收报告

## 已完成并验证

- 前端 TypeScript 类型检查通过。
- Vite 生产构建通过，输出首页、产品、应用、文章、固定页的静态 HTML、`sitemap.xml`、`robots.txt` 和 `search-index.json`。
- Vitest 内容与表单约束测试通过，静态产物检查通过。
- FastAPI 健康检查、非法表单拒绝、管理员接口认证、文件类型拒绝测试通过；Python 编译通过。
- Supabase schema、索引、审核约束、RLS、私有 Storage 策略与安全 Seed 均以 migration 文件交付。

## 上线前待配置

- Supabase 项目、真实联系信息、已审核产品资料、管理员账号、私有 Storage Bucket 配置。
- API 域名、CORS 白名单、通知邮件服务、验证码与 GitHub Actions Variables/Secrets。
- GitHub 仓库、Pages、自定义域名和搜索平台站长验证。

## 已知限制

- 当前产品、应用、文章仅为明确标注的待审核示例，不含可对外使用的技术参数或认证结论。
- 生产环境的通知渠道、验证码供应商和 GitHub Token 需由部署方提供；代码不会生成或存储这些密钥。
- 后台管理页面已接入认证与 RLS 权限边界；完整真实内容管理需在 Supabase 初始化并填入真实已审核内容后使用。
