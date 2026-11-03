"""Public endpoints: project briefs (leads), free-guide requests and the sitemap."""
from datetime import timedelta

import anvil.server
from anvil.tables import app_tables

from .common import clean, now, notify_admins, send_email, SITE_URL
from .i18n_server import Tr


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
  company, kind, budget = clean(data.get('company')), clean(data.get('kind')), clean(data.get('budget'))
  notify_admins(lambda tr: (
    tr("New project brief from {name}", name=name), tr("New project brief"),
    [f"<b>{name}</b> · {email} · {company or tr('no company')}",
     f"{tr(kind)} · " + tr("Budget: {budget}", budget=tr(budget)),
     message[:1500].replace('\n', '<br>')]), 'admin/leads')
  return True


# ---------------------------------------------------------------- free guides
# A guide request is a lead with source 'guide' (or 'guide+news' when the person ticked the tips box) and the
# situation they picked as its kind. The newsletter consent record (exact wording, time, language) is kept in
# the message, which CASL asks us to be able to show.

GUIDES = {  # slug: title (same list as client_code/content.py GUIDES)
  'spreadsheet-escape-plan': 'Your Spreadsheet Is Already an App',
  'one-page-app-brief': 'The One-Page App Brief',
  'ai-built-human-signed': 'AI-Built, Human-Signed',
  'build-buy-or-bolt-on': 'Build, Buy or Bolt On',
  'law-25-app-checklist': 'Law 25 for Your Next App',
}
GUIDE_SITUATIONS = ['We run on spreadsheets', 'We pay for too many tools', 'Just curious', 'I have an app idea',
                    "We're building something now"]
HOT_SITUATIONS = {'I have an app idea', "We're building something now"}
NEWSLETTER_WORDING = "Yes, also send me occasional tips from Addanapp. I can unsubscribe at any time."


def guide_url(slug):
  return f"_/theme/guides/{slug}.pdf"


def is_quiet_guide_lead(row):
  """A guide download without a buying signal: listed in the console, but not counted as a new lead."""
  return (row['source'] or '').startswith('guide') and (row['kind'] or '') not in HOT_SITUATIONS


@anvil.server.callable
def request_guides(data):
  data = data or {}
  links = [[slug, guide_url(slug)] for slug in GUIDES]
  if clean(data.get('website')):
    return {'links': links, 'emailed': False}  # honeypot filled: nothing stored or sent
  email = clean(data.get('email'), 160).lower()
  if '@' not in email or '.' not in email.split('@')[-1] or ' ' in email:
    raise Exception("Please enter a valid email address.")
  name = clean(data.get('name'), 60)
  situation = clean(data.get('situation'), 60)
  situation = situation if situation in GUIDE_SITUATIONS else ''
  guide = clean(data.get('guide'), 60)
  lang = clean(data.get('lang'), 5)
  lang = lang if lang in ('en', 'fr', 'ru', 'lv') else 'en'
  wants_news = bool(data.get('newsletter'))
  stamp = now()
  today = stamp.strftime('%Y-%m-%d')
  consent = (f'Newsletter: yes. Ticked "{NEWSLETTER_WORDING}" on {stamp.strftime("%Y-%m-%d %H:%M")} UTC '
             f'(guides page, language {lang}).' if wants_news else 'Newsletter: no.')
  sent_note = f'Emailed the links on {today}.'

  row = None
  for l in app_tables.leads.search(email=email):
    if (l['source'] or '').startswith('guide'):
      row = l
      break
  if row is None:
    first = f' First asked for: {GUIDES[guide]}.' if guide in GUIDES else ''
    emailed = True
    app_tables.leads.add_row(
      name=name or email.split('@')[0], email=email, company='', kind=situation, budget='',
      message=f'Asked for the free guides.{first} {consent} {sent_note}', status='new', created=stamp,
      source='guide+news' if wants_news else 'guide')
  else:
    # The same person again: keep one row, and email the links at most once a day (no inbox flooding).
    msg = row['message'] or ''
    emailed = sent_note not in msg
    add = f'\nAsked again on {today}.'
    if wants_news and row['source'] != 'guide+news':
      add += ' ' + consent
    if emailed:
      add += ' ' + sent_note
    ch = {'message': (msg + add)[-4000:]}
    if wants_news:
      ch['source'] = 'guide+news'
    if situation:
      ch['kind'] = situation
    if name and (not row['name'] or row['name'] == email.split('@')[0]):
      ch['name'] = name
    row.update(**ch)

  if emailed:
    _email_guides(email, name, lang, wants_news)
    if situation in HOT_SITUATIONS:
      who = name or email
      notify_admins(lambda tr: (
        tr("{name} downloaded the free guides", name=who), tr("A guide reader with a project"),
        [f"<b>{who}</b> · {email}", tr(situation)] + ([tr("They also asked for tips by email.")] if wants_news else [])),
        'admin/leads')
  return {'links': links, 'emailed': emailed}


def _email_guides(email, name, lang, wants_news):
  tr = Tr(lang)
  items = ''.join(f'<li style="margin:0 0 8px"><a href="{SITE_URL}/{guide_url(slug)}" style="color:#2F5BFF;font-weight:600">'
                  f'{title}</a></li>' for slug, title in GUIDES.items())
  lines = [tr("Hi {name},", name=name) if name else tr("Hello,"),
           tr("Thanks for asking for the Addanapp guides. Here are your five PDFs:"),
           f'<ul style="margin:0 0 4px;padding-left:18px">{items}</ul>']
  if lang != 'en':
    lines.append(tr("The guides are written in English."))
  lines.append(tr("If one of them sounds like your business, send us a short brief: an engineer will reply with questions or a fixed quote."))
  lines.append('<span style="font-size:12px;color:#8C94A3">' + (
    tr("You also asked for occasional tips. Every tips email will have an unsubscribe link.") if wants_news else
    tr("You're getting this one email because you asked for the guides on addanapp.com. We won't send you anything else.")) + '</span>')
  send_email(email, tr("Your free Addanapp guides"), tr("Your guides are ready"), lines, tr("Send a project brief"),
             'home/contact', tr)


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

