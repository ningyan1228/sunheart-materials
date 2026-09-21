import { z } from 'zod';

export const inquirySchema = z.object({
  name: z.string().trim().min(1, '请填写姓名').max(50),
  company: z.string().trim().min(1, '请填写公司名称').max(120),
  phone: z.string().trim().regex(/^1\d{10}$/, '请输入有效的中国大陆手机号'),
  wechat: z.string().trim().max(80).optional(),
  email: z.string().trim().email('请输入有效邮箱').optional().or(z.literal('')),
  provinceCity: z.string().trim().min(1, '请填写所在省市').max(80),
  productOrApplication: z.string().trim().min(1, '请选择产品或应用').max(160),
  substrate: z.string().trim().min(1, '请填写基材').max(120),
  currentProblem: z.string().trim().min(1, '请填写当前问题').max(2000),
  targetPerformance: z.string().trim().min(1, '请填写目标性能').max(1000),
  monthlyUsage: z.string().trim().max(100).optional(),
  services: z.array(z.string()).min(1, '请选择所需服务'),
  privacyAccepted: z.boolean().refine(value => value, { message: '请先同意隐私政策' }),
  website: z.string().max(0).optional()
});
export type InquiryForm = z.infer<typeof inquirySchema>;
export const apiBase = import.meta.env.VITE_API_BASE_URL || '';
