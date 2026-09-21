import fs from 'node:fs';
import path from 'node:path';

// GitHub Pages needs physical entry files for deep links, but these entries
// must remain the Vite/React application rather than replacing it with a
// second, simplified HTML site.
const root = path.resolve(process.cwd(), '../..');
const dist = path.join(root, 'apps', 'web', 'dist');
const appEntry = path.join(dist, 'index.html');

if (!fs.existsSync(appEntry)) throw new Error('Vite entry was not generated before prerendering.');

const contentFile = path.join(root, 'scripts', 'build-content.json');
const content = fs.existsSync(contentFile) ? JSON.parse(fs.readFileSync(contentFile, 'utf8')) : {};
const productSlugs = content.products?.length
  ? content.products.map((product) => product.slug)
  : ['fluorine-free-textile-water-repellent', 'pha-waterborne-paper-barrier', 'pvc-low-migration-plasticizer', 'controlled-release-fertilizer-coating'];
const applicationSlugs = content.applications?.length
  ? content.applications.map((application) => application.slug)
  : ['knitted-upper-water-repellent', 'food-paper-barrier', 'pvc-low-migration', 'fertilizer-drum-coating'];
const articleSlugs = content.articles?.length
  ? content.articles.map((article) => article.slug)
  : ['how-to-verify-water-repellent-fabric', 'paper-barrier-material-selection'];

const routes = [
  'products',
  ...productSlugs.map((slug) => `products/${slug}`),
  'applications',
  ...applicationSlugs.map((slug) => `applications/${slug}`),
  'knowledge',
  ...articleSlugs.map((slug) => `knowledge/${slug}`),
  'documents', 'sample', 'inquiry', 'about', 'contact', 'privacy', 'terms', 'disclaimer', 'search',
];

for (const route of routes) {
  const directory = path.join(dist, route);
  fs.mkdirSync(directory, { recursive: true });
  fs.copyFileSync(appEntry, path.join(directory, 'index.html'));
}

// GitHub Pages serves this file for unknown routes. The app renders its own 404.
fs.copyFileSync(appEntry, path.join(dist, '404.html'));
