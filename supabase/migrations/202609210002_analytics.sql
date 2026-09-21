create table public.analytics_events (
  id uuid primary key default gen_random_uuid(),
  event_name text not null check(event_name in ('page_view','product_view','application_view','search','document_request','sample_request','quote_inquiry','wechat_open','phone_click')),
  entity_path text not null default '',
  search_term text,
  source_path text,
  utm jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index analytics_events_name_created_idx on public.analytics_events(event_name,created_at desc);
alter table public.analytics_events enable row level security;
create policy "owner reads analytics" on public.analytics_events for select using(public.is_owner());
