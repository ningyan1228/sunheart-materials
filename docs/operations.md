# 运维、备份与恢复

## 初始化

按文件名顺序执行 `supabase/migrations/*.sql`，然后执行 `supabase/seed.sql`。在 Auth 创建首位管理员后，向 `profiles` 写入对应 UUID、`owner` 角色和 `is_active=true`。

## 备份

- 每日备份 Supabase PostgreSQL；每周验证一次恢复到隔离项目。
- 导出 Storage 私有 Bucket 的对象清单与受控备份；私有文件不要通过公开 URL 备份。
- 保存 GitHub 仓库、Actions 配置和部署变量清单（不含明文密钥）。

## 恢复

先恢复数据库，再恢复 Storage 对象，最后验证 RLS、管理员权限、私有签名下载、表单 API 和静态站点。恢复完成后重新触发 Pages 构建并抽查 Sitemap。
