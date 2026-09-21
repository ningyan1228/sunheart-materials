import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(process.cwd(),'../..'); const dist=path.join(root,'apps/web/dist'); const site=(process.env.VITE_SITE_URL||'https://example.com').replace(/\/$/,'');
const files=[]; const walk=(dir)=>fs.readdirSync(dir,{withFileTypes:true}).forEach(e=>e.isDirectory()?walk(path.join(dir,e.name)):e.name==='index.html'&&files.push(path.join(dir,e.name))); walk(dist);
const urls=files.map(file=>{let rel=path.relative(dist,file).replaceAll('\\','/').replace(/index\.html$/,''); if(rel==='404/')return ''; return `<url><loc>${site}/${rel}</loc><changefreq>weekly</changefreq></url>`}).filter(Boolean).join('');
fs.writeFileSync(path.join(dist,'sitemap.xml'),`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls}</urlset>`); fs.writeFileSync(path.join(dist,'robots.txt'),`User-agent: *\nAllow: /\nSitemap: ${site}/sitemap.xml\n`);
