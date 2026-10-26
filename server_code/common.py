"""Shared server helpers: users, ids, statuses, notifications."""
import random
from datetime import datetime

import anvil.server
import anvil.users
import anvil.email
import anvil.tz
from anvil.tables import app_tables

from .i18n_server import Tr, user_lang

# Anyone signing up with one of these emails becomes a consultant (admin) automatically.
ADMIN_EMAILS = {"arkulinskis@gmail.com"}

SITE_URL = "https://addanapp.com"
SITE_NAME = "Addanapp"

STATUS_LABEL = {
  'new': 'Submitted', 'scoping': 'Scoping', 'quoted': 'Quote ready', 'in_progress': 'In progress',
  'review': 'Ready for review', 'delivered': 'Delivered', 'on_hold': 'On hold', 'declined': 'Closed',
}
STATUSES = list(STATUS_LABEL.keys())
OPEN_STATUSES = ['new', 'scoping', 'quoted', 'in_progress', 'review', 'on_hold']
KINDS = ['feature', 'change', 'bug', 'new_app', 'integration', 'data', 'other']
KIND_LABEL = {'feature': 'New feature', 'change': 'Improvement', 'bug': 'Bug fix', 'new_app': 'New app',
              'integration': 'Integration / API', 'data': 'Data & reporting', 'other': 'Other'}
PRIORITIES = ['low', 'normal', 'high', 'urgent']
PRIORITY_LABEL = {'low': 'Low', 'normal': 'Normal', 'high': 'High', 'urgent': 'Urgent'}
ADMIN_NOTE_KINDS = ['update', 'milestone', 'validated', 'question', 'internal']
LEAD_STATUSES = ['new', 'contacted', 'won', 'lost', 'archived']

AVATAR_COLORS = ['#2F5BFF', '#7A5CFA', '#0E9F6E', '#B7791F', '#D9487A', '#1F6B63', '#3446D8', '#C2410C']


# ---------------------------------------------------------------- time & ids

def now():
  return datetime.now(anvil.tz.tzutc())


def rid(row):
  """Row id as a URL-safe token."""
  if row is None:
    return None
  return row.get_id().strip('[]').replace(',', '_')


def by_id(table, token):
  if not token:
    return None
  token = str(token)
  try:
    if '_' in token:
      return table.get_by_id('[' + token.replace('_', ',') + ']')
    return table.get_by_id(token)
  except Exception:
    return None


def clean(s, limit=5000):
  return (str(s) if s is not None else '').strip()[:limit]


def next_ref():
  n = len(app_tables.requests.search()) + 1001
  while app_tables.requests.get(ref=f"AA-{n}") is not None:
    n += 1
  return f"AA-{n}"


# ---------------------------------------------------------------- users

def initials(name):
  parts = [p for p in (name or '').replace('.', ' ').split() if p]
  if not parts:
    return '?'
  if len(parts) == 1:
    return parts[0][:2].upper()
  return (parts[0][0] + parts[-1][0]).upper()


def ensure_defaults(u):
  ch = {}
  if not u['name']:
    base = (u['email'] or 'Client').split('@')[0]
    ch['name'] = base.replace('.', ' ').replace('_', ' ').replace('-', ' ').title()[:60]
  if not u['color']:
    ch['color'] = random.choice(AVATAR_COLORS)
  if u['email_notifications'] is None:
    ch['email_notifications'] = True
  if u['created'] is None:
    ch['created'] = u['signed_up'] or now()
  is_listed = (u['email'] or '').strip().lower() in ADMIN_EMAILS
  if is_listed and not u['is_admin']:
    ch['is_admin'] = True
  if not u['role']:
    ch['role'] = 'admin' if (is_listed or u['is_admin']) else 'client'
  if ch:
    u.update(**ch)


def current_user(required=True):
  u = anvil.users.get_user()
  if u is None:
    if required:
      raise Exception("Please sign in first.")
    return None
  if u['enabled'] is False:
    raise Exception("This account is disabled. Contact hello@addanapp.com.")
  ensure_defaults(u)
  return u


def require_admin():
  u = current_user()
  if not u['is_admin']:
    raise Exception("Only Addanapp consultants can do that.")
  return u


def admins():
  return [a for a in app_tables.users.search(is_admin=True) if a['enabled'] is not False]


def touch(u):
  try:
    t = now()
    if u['last_seen'] is None or (t - u['last_seen']).total_seconds() > 300:
      u['last_seen'] = t
  except Exception:
    pass


# ---------------------------------------------------------------- notes

def add_note(request, author, kind, body='', internal=False, status_from=None, status_to=None, progress=None):
  return app_tables.notes.add_row(
    request=request, author=author, kind=kind, body=clean(body, 8000), internal=bool(internal),
    status_from=status_from, status_to=status_to, progress=progress, created=now())


# ---------------------------------------------------------------- email

def _email_html(title, lines, cta_text=None, cta_url=None, tr=None):
  tr = tr or Tr()
  body = ''.join(f'<p style="margin:0 0 12px;color:#3A4457;font-size:15px;line-height:1.6">{l}</p>' for l in lines)
  cta = ''
  if cta_text and cta_url:
    cta = (f'<p style="margin:22px 0 0"><a href="{cta_url}" style="background:#0B1220;color:#fff;text-decoration:none;'
           f'padding:12px 20px;border-radius:999px;font-weight:600;font-size:14px;display:inline-block">{cta_text}</a></p>')
  return f'''<div style="background:#FAF9F5;padding:32px 16px;font-family:Inter,Segoe UI,Arial,sans-serif">
  <div style="max-width:560px;margin:0 auto;background:#fff;border:1px solid #E6E3DA;border-radius:16px;padding:28px">
    <div style="font-weight:700;color:#0B1220;font-size:16px;margin-bottom:18px">add<span style="color:#8C94A3">an</span>app</div>
    <h1 style="font-size:20px;color:#0B1220;margin:0 0 14px">{title}</h1>{body}{cta}
    <p style="margin:26px 0 0;color:#8C94A3;font-size:12px">{tr('Addanapp · Custom software, Montréal · AI-accelerated, human-validated.')}</p>
  </div></div>'''


def send_email(to, subject, title, lines, cta_text=None, path='', tr=None):
  if not to:
    return
  try:
    anvil.email.send(to=to, from_name=SITE_NAME, subject=subject,
                     html=_email_html(title, lines, cta_text, SITE_URL + '/#' + path if cta_text else None, tr))
  except Exception as e:
    print("Email failed:", e)


# build(tr) returns (subject, title, lines) written with tr(), so each person gets the email in their language.

def notify_admins(build, path=''):
  for a in admins():
    if a['email_notifications'] is not False:
      tr = Tr(user_lang(a))
      subject, title, lines = build(tr)
      send_email(a['email'], subject, title, lines, tr('Open in console'), path, tr)


def notify_client(request, build):
  c = request['client']
  if c is None or c['is_demo'] or c['email_notifications'] is False:
    return
  tr = Tr(user_lang(c))
  subject, title, lines = build(tr)
  send_email(c['email'], subject, title, lines, tr('Open your workspace'), 'r/' + rid(request), tr)
