import { describe, expect, it } from 'vitest';
import { applications, articles, products } from './content';
import { inquirySchema } from './lib';

describe('content guardrails', () => {
  it('keeps all seed product content explicitly pending review', () => {
    expect(products.length).toBeGreaterThan(0);
    expect(products.every(product => product.status === '待审核')).toBe(true);
    expect(applications.every(application => application.status === '待审核')).toBe(true);
    expect(articles.every(article => article.status === '待审核')).toBe(true);
  });
  it('rejects an inquiry without privacy consent or a valid mainland mobile number', () => {
    const base = { name:'张三',company:'示例公司',phone:'123',provinceCity:'上海',productOrApplication:'示例产品',substrate:'织物',currentProblem:'需要资料',targetPerformance:'待确认',services:['TDS/SDS'],privacyAccepted:false };
    expect(inquirySchema.safeParse(base).success).toBe(false);
  });
});
