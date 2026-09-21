-- Safe seed: only draft examples. Do not publish until a qualified reviewer attaches evidence.
insert into public.site_settings(key,value,is_public) values
('contact', '{"wechat":"待配置","phone":"待配置","email":"待配置","service_hours":"工作日 09:00–18:00"}', true),
('search_synonyms', '{"防泼水":["防水整理","疏水"],"析出":["渗出","迁移"]}', false)
on conflict(key) do update set value=excluded.value;
insert into public.products(slug,status,origin_type,display_name,summary,substrates,processing_methods) values
('fluorine-free-textile-water-repellent','draft','imported','无氟织物防泼水材料｜飞织鞋面与户外面料应用','待审核示例：具体适用性和性能须以审核资料为准。',array['待确认'],array['待确认']),
('pha-waterborne-paper-barrier','draft','domestic','纸杯纸碗用 PHA 水性阻隔材料｜食品包装纸涂层','待审核示例：公开技术数据与合规依据待审核后发布。',array['待确认'],array['待确认'])
on conflict(slug) do nothing;
