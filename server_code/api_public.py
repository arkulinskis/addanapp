"""Public endpoints: project briefs (leads) and the sitemap."""
from datetime import timedelta

import anvil.server
from anvil.tables import app_tables

from .common import clean, now, notify_admins, SITE_URL


@anvil.server.callable
def submit_lead(data):
  data = data or {}
  if clean(data.get('website')):
    return True  # honeypot filled: silently ignore bots
  name = clean(data.get('name'), 100)
  email = clean(data.get('email'), 160).lower()
  message = clean(data.get('message'), 5000)
  if len(name) < 2:
    raise Exception("Please tell us your name.")
  if '@' not in email or '.' not in email.split('@')[-1]:
    raise Exception("Please enter a valid email address.")
  if len(message) < 10:
    raise Exception("Please describe what you need in a sentence or two.")
  if not data.get('consent'):
    raise Exception("Please confirm we may contact you about this request.")
  recent = [l for l in app_tables.leads.search(email=email) if l['created'] and now() - l['created'] < timedelta(hours=1)]
  if len(recent) >= 3:
    raise Exception("We've received your briefs. An engineer will be in touch shortly.")
  app_tables.leads.add_row(name=name, email=email, company=clean(data.get('company'), 120), kind=clean(data.get('kind'), 80),
                           budget=clean(data.get('budget'), 40), message=message, status='new', created=now(),
                           source='website')
  notify_admins(f"New project brief from {name}", "New project brief",
                [f"<b>{name}</b> · {email} · {clean(data.get('company')) or 'no company'}",
                 f"{clean(data.get('kind'))} · Budget: {clean(data.get('budget'))}",
                 message[:1500].replace('\n', '<br>')], 'admin/leads')
  return True


@anvil.server.http_endpoint('/sitemap.xml')
def sitemap(**kw):
  today = now().strftime('%Y-%m-%d')
  body = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>'''
  return anvil.server.HttpResponse(200, body, headers={'Content-Type': 'application/xml; charset=utf-8'})

