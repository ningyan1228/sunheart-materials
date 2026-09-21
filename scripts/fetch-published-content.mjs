import fs from 'node:fs';
import path from 'node:path';

const root = fs.existsSync(path.join(process.cwd(), 'apps', 'web')) ? process.cwd() : path.resolve(process.cwd(), '../..');
const output = path.join(root, 'scripts', 'build-content.json');
const runtimeOutput = path.join(root, 'apps', 'web', 'src', 'generated-content.json');
const url = (process.env.VITE_SUPABASE_URL || process.env.SUPABASE_URL || '').replace(/\/$/, '');
const key = process.env.VITE_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY || '';
if (!url || !key) {
  const fallback = { source: 'local-safe-fallback', products: [], applications: [], articles: [] };
  fs.writeFileSync(output, JSON.stringify(fallback, null, 2));
  fs.writeFileSync(runtimeOutput, JSON.stringify(fallback, null, 2));
  console.log('Supabase build credentials absent; retained safe local draft fallback.');
  process.exit(0);
}
const headers = { apikey: key, Authorization: `Bearer ${key}` };
const get = async (table, select) => { const response = await fetch(`${url}/rest/v1/${table}?status=eq.published&select=${encodeURIComponent(select)}&order=published_at.desc`, { headers }); if (!response.ok) throw new Error(`${table} fetch failed (${response.status})`); return response.json(); };
const [products, applications, articles] = await Promise.all([get('products','slug,display_name,origin_type,summary,updated_at'), get('applications','slug,name,summary,customer_problem,updated_at'), get('articles','slug,title,excerpt,updated_at')]);
const published = { generated_at: new Date().toISOString(), source: 'supabase-published-only', products, applications, articles };
fs.writeFileSync(output, JSON.stringify(published, null, 2));
fs.writeFileSync(runtimeOutput, JSON.stringify(published, null, 2));
