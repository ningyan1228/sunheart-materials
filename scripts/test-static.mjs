import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(process.cwd(),'../..'); const dist=path.join(root,'apps/web/dist');
for(const route of ['index.html','products/index.html','products/fluorine-free-textile-water-repellent/index.html','applications/index.html','applications/knitted-upper-water-repellent/index.html','knowledge/index.html','knowledge/how-to-verify-water-repellent-fabric/index.html','sitemap.xml','robots.txt','search-index.json']) assert.ok(fs.existsSync(path.join(dist,route)),`missing static output: ${route}`);
const product=fs.readFileSync(path.join(dist,'products/fluorine-free-textile-water-repellent/index.html'),'utf8');
assert.match(product,/<h1>无氟织物防泼水材料/); assert.match(product,/application\/ld\+json/); assert.match(product,/请联系获取/);
assert.match(fs.readFileSync(path.join(dist,'sitemap.xml'),'utf8'),/products\/fluorine-free-textile-water-repellent/);
