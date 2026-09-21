import { apiBase } from './lib';

export function track(event_name: 'page_view'|'product_view'|'application_view'|'search'|'document_request'|'sample_request'|'quote_inquiry'|'wechat_open'|'phone_click', entity_path = window.location.pathname, search_term?: string) {
  if (!apiBase) return;
  const payload = JSON.stringify({ event_name, entity_path, search_term });
  const url = `${apiBase}/api/events${window.location.search}`;
  if (navigator.sendBeacon) navigator.sendBeacon(url, new Blob([payload], { type: 'application/json' }));
  else void fetch(url, { method: 'POST', headers: { 'content-type': 'application/json' }, body: payload, keepalive: true });
}
