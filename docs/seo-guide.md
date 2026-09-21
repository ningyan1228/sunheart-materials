# SEO 与搜索平台

构建脚本为首页、产品、应用、文章和固定公开页生成静态 HTML；每页带唯一标题、描述、Canonical、JSON-LD 与可读正文。`sitemap.xml`、`robots.txt`、`search-index.json` 同时生成。

在 Supabase 设置中保存百度/360/Bing 验证码和统计 ID；未配置时不加载统计脚本。将最终 Sitemap 提交至百度搜索资源平台、Bing Webmaster 和其他实际使用的平台。内容变更后由后台调用 API 的重建接口触发 Pages workflow。
