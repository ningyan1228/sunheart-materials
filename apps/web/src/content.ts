import generated from './generated-content.json';

export type Product = { slug: string; name: string; origin: '进口产品' | '国产产品'; summary: string; applications: string[]; status: '待审核'; tags: string[] };
export type Application = { slug: string; name: string; question: string; summary: string; relatedProduct: string; status: '待审核' };
export type Article = { slug: string; title: string; excerpt: string; productSlug: string; status: '待审核' };

const sampleProducts: Product[] = [
  { slug: 'fluorine-free-textile-water-repellent', name: '无氟织物防泼水材料｜飞织鞋面与户外面料应用', origin: '进口产品', summary: '用于需要表面疏水处理的织物应用；具体适用性、加工窗口和性能须以已审核资料与测试为准。', applications: ['飞织鞋面防泼水处理', '户外面料无氟防水整理'], status: '待审核', tags: ['无氟防泼水', '织物', '鞋面'] },
  { slug: 'pha-waterborne-paper-barrier', name: '纸杯纸碗用 PHA 水性阻隔材料｜食品包装纸涂层', origin: '国产产品', summary: '面向纸基包装阻隔应用的材料方案结构示例，公开技术数据与合规依据待审核后发布。', applications: ['食品包装纸阻隔涂层'], status: '待审核', tags: ['PHA', '纸基包装', '阻隔'] },
  { slug: 'pvc-low-migration-plasticizer', name: 'PVC 低迁移功能增塑剂｜耐热低析出应用', origin: '进口产品', summary: '面向 PVC 制品应用的选材入口；迁移、析出与雾化等结论需基于具体配方和已审核资料。', applications: ['PVC 制品低迁移选材'], status: '待审核', tags: ['PVC', '低迁移', '增塑剂'] },
  { slug: 'controlled-release-fertilizer-coating', name: '控释肥用聚氨酯包衣剂｜滚筒包衣应用', origin: '国产产品', summary: '面向颗粒肥料包衣工艺的材料方案结构示例，实际工艺与性能需要结合现场验证。', applications: ['控释尿素滚筒包衣'], status: '待审核', tags: ['控释肥', '聚氨酯', '包衣'] }
];

const sampleApplications: Application[] = [
  { slug: 'knitted-upper-water-repellent', name: '飞织鞋面防泼水处理', question: '飞织鞋面如何实现表面防泼水？', summary: '围绕基材、整理方式、目标性能与验证项目建立的待审核应用页示例。', relatedProduct: sampleProducts[0].slug, status: '待审核' },
  { slug: 'food-paper-barrier', name: '食品包装纸阻隔涂层', question: '食品包装纸如何减少传统塑料淋膜？', summary: '围绕纸基、涂布方式及阻隔需求建立的待审核应用页示例。', relatedProduct: sampleProducts[1].slug, status: '待审核' },
  { slug: 'pvc-low-migration', name: 'PVC 制品低迁移选材', question: 'PVC 如何降低迁移、析出和雾化？', summary: '围绕配方、加工与验证项目建立的待审核应用页示例。', relatedProduct: sampleProducts[2].slug, status: '待审核' },
  { slug: 'fertilizer-drum-coating', name: '控释尿素滚筒包衣', question: '控释肥如何提高包衣均匀性？', summary: '围绕颗粒状态、工艺条件与性能验证建立的待审核应用页示例。', relatedProduct: sampleProducts[3].slug, status: '待审核' }
];

const sampleArticles: Article[] = [
  { slug: 'how-to-verify-water-repellent-fabric', title: '面料防泼水方案如何规划验证项目？', excerpt: '从基材、加工方式、目标性能和测试条件四个维度建立资料确认清单。', productSlug: sampleProducts[0].slug, status: '待审核' },
  { slug: 'paper-barrier-material-selection', title: '纸基包装阻隔材料选型前需要确认什么？', excerpt: '先明确制品结构、使用场景、涂布工艺和法规适用范围，再进入样品测试。', productSlug: sampleProducts[1].slug, status: '待审核' }
];

type BuildProduct = { slug:string; display_name:string; origin_type:'imported'|'domestic'; summary?:string };
type BuildApplication = { slug:string; name:string; summary?:string; customer_problem?:string };
type BuildArticle = { slug:string; title:string; excerpt?:string };
const build = generated as { products?:BuildProduct[]; applications?:BuildApplication[]; articles?:BuildArticle[] };
export const products: Product[] = build.products?.length ? build.products.map(item => ({ slug:item.slug, name:item.display_name, origin:item.origin_type==='imported'?'进口产品':'国产产品', summary:item.summary || '请联系获取已审核资料。', applications:[], status:'待审核', tags:[] })) : sampleProducts;
export const applications: Application[] = build.applications?.length ? build.applications.map(item => ({ slug:item.slug, name:item.name, question:item.customer_problem || item.summary || '请联系获取已审核应用资料。', summary:item.summary || '请联系获取已审核应用资料。', relatedProduct:products[0]?.slug || '', status:'待审核' })) : sampleApplications;
export const articles: Article[] = build.articles?.length ? build.articles.map(item => ({ slug:item.slug, title:item.title, excerpt:item.excerpt || '请联系获取已审核文章资料。', productSlug:products[0]?.slug || '', status:'待审核' })) : sampleArticles;

export const settings = { phone: '待配置', wechat: '待配置', email: '待配置', serviceHours: '工作日 09:00–18:00' };
