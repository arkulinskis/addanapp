"""Consultant console API: every request, progress notes, status, quotes, clients, leads."""
import datetime

import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables

from . import serial
from .common import (require_admin, rid, by_id, clean, now, add_note, notify_client, ensure_defaults,
                     STATUSES, STATUS_LABEL, PRIORITIES, ADMIN_NOTE_KINDS, LEAD_STATUSES, OPEN_STATUSES)
from .api_client import payload, create_request_row


@anvil.server.callable
def admin_overview():
  require_admin()
  rows = app_tables.requests.search(tables.order_by('last_activity', ascending=False))
  reqs = [serial.request(r, True) for r in rows]
  clients = {}
  for r in reqs:
    c = r['client']
    if c and c['id'] not in clients:
      clients[c['id']] = c
  return {'requests': reqs, 'clients': sorted(clients.values(), key=lambda c: (c['company'] or c['name']).lower())}


def _money(v):
  if v is None:
    return '—'
  return '${:,.0f}'.format(v)


@anvil.server.callable
def admin_update_request(request_id, changes=None, note=None):
  """Update status / progress / quote / ETA / priority and optionally post a note, in one go."""
  u = require_admin()
  r = by_id(app_tables.requests, request_id)
  if r is None:
    raise Exception("Request not found.")
  changes = changes or {}
  t = now()
  ch = {}
  client_visible = []  # functions tr -> line, so the email is written in the client's language

  if 'priority' in changes and changes['priority'] in PRIORITIES and changes['priority'] != r['priority']:
    ch['priority'] = changes['priority']
  if 'progress' in changes and changes['progress'] is not None:
    p = max(0, min(100, int(changes['progress'])))
    if p != (r['progress'] or 0):
      ch['progress'] = p
      client_visible.append(lambda tr, p=p: tr("Progress is now {p}%.", p=p))
  if 'quote_amount' in changes:
    qa = changes['quote_amount']
    qa = float(qa) if qa not in (None, '') else None
    if qa is not None and qa < 0:
      raise Exception("Quotes can't be negative.")
    if qa != r['quote_amount']:
      ch['quote_amount'] = qa
  if 'quote_note' in changes:
    qn = clean(changes['quote_note'], 4000)
    if qn != (r['quote_note'] or ''):
      ch['quote_note'] = qn
  if 'eta' in changes:
    eta = changes['eta']
    if eta is not None and not isinstance(eta, datetime.date):
      eta = None
    if eta != r['eta']:
      ch['eta'] = eta
      if eta:
        client_visible.append(lambda tr, eta=eta: tr("Expected delivery: {date}.", date=tr.date(eta)))

  new_status = changes.get('status')
  if new_status and new_status not in STATUSES:
    raise Exception("Unknown status.")
  if new_status == 'quoted' and (ch.get('quote_amount', r['quote_amount']) is None):
    raise Exception("Add the fixed quote amount before sending the quote.")

  if ch:
    ch['updated'] = t
    r.update(**ch)

  status_changed = bool(new_status) and new_status != r['status']
  if status_changed:
    old = r['status']
    upd = {'status': new_status, 'updated': t}
    if new_status == 'delivered':
      upd['progress'] = 100
      upd['accepted_at'] = r['accepted_at'] or t
    if new_status == 'review' and (r['progress'] or 0) < 95:
      upd['progress'] = 95
    r.update(**upd)
    body = ''
    if new_status == 'quoted':
      body = f"Fixed quote: {_money(r['quote_amount'])}" + (f" · ETA {r['eta'].strftime('%b %d')}" if r['eta'] else '')
    add_note(r, u, 'status', body, status_from=old, status_to=new_status)

  posted = None
  if note and clean(note.get('body')):
    kind = note.get('kind') if note.get('kind') in ADMIN_NOTE_KINDS else 'update'
    internal = bool(note.get('internal')) or kind == 'internal'
    posted = add_note(r, u, kind, note.get('body'), internal=internal, progress=ch.get('progress'))
    if not internal:
      body_html = clean(note.get('body'))[:900].replace('\n', '<br>')
      client_visible.insert(0, lambda tr, b=body_html: b)

  if status_changed or (posted is not None and not posted['internal']) or 'progress' in ch or 'eta' in ch:
    r.update(last_activity=t, client_unread=True)
    if status_changed:
      def build(tr):
        lines = {
          'scoping': [tr("An engineer is scoping your request now. Expect a fixed quote soon.")],
          'quoted': [tr("Your fixed quote is ready: <b>{amount}</b>.", amount=tr.money(r['quote_amount'])),
                     tr("Approve it in your workspace to start the build.")],
          'in_progress': [tr("The build is underway.")],
          'review': [tr("It's ready for your review. Test it, then accept the delivery or request changes.")],
          'delivered': [tr("Marked as delivered. Thank you!")],
          'on_hold': [tr("This request is on hold for now. We'll explain in the notes.")],
          'declined': [tr("This request has been closed.")],
        }.get(new_status, [])
        return (f"{r['ref']}: {tr(STATUS_LABEL[new_status])}", f"{r['title']}", lines + [f(tr) for f in client_visible])
      notify_client(r, build)
    elif client_visible:
      notify_client(r, lambda tr: (tr("{ref}: progress update", ref=r['ref']), tr("Update on {title}", title=r['title']),
                                   [f(tr) for f in client_visible]))
  return payload(r, u)


@anvil.server.callable
def admin_create_request(client_id, data):
  u = require_admin()
  client = by_id(app_tables.users, client_id)
  if client is None:
    raise Exception("Pick a client.")
  r = create_request_row(client, data, u)
  notify_client(r, lambda tr: (tr("{ref}: new request logged", ref=r['ref']), r['title'],
                               [tr("We logged this request in your workspace on your behalf. You can follow it there.")]))
  return rid(r)


@anvil.server.callable
def admin_delete_request(request_id):
  require_admin()
  r = by_id(app_tables.requests, request_id)
  if r is None:
    return False
  for n in app_tables.notes.search(request=r):
    n.delete()
  r.delete()
  return True


# ---------------------------------------------------------------- clients

@anvil.server.callable
def admin_clients():
  require_admin()
  reqs = list(app_tables.requests.search())
  out = []
  for u in app_tables.users.search(tables.order_by('name')):
    ensure_defaults(u)
    mine = [r for r in reqs if r['client'] == u]
    d = serial.person(u, with_email=True)
    d.update({
      'enabled': u['enabled'] is not False, 'is_demo': bool(u['is_demo']), 'last_seen': u['last_seen'] or u['last_login'],
      'created': u['created'], 'open': len([r for r in mine if r['status'] in OPEN_STATUSES]), 'total': len(mine),
      'delivered': len([r for r in mine if r['status'] == 'delivered']),
      'value': sum([(r['quote_amount'] or 0) for r in mine if r['status'] == 'delivered']),
    })
    out.append(d)
  out.sort(key=lambda d: (d['is_admin'], -d['open'], (d['company'] or d['name']).lower()))
  return out


@anvil.server.callable
def admin_set_user(user_id, changes):
  me = require_admin()
  u = by_id(app_tables.users, user_id)
  if u is None:
    raise Exception("User not found.")
  if u == me and ('is_admin' in changes or 'enabled' in changes):
    raise Exception("You can't change your own access.")
  ch = {}
  if 'is_admin' in changes:
    ch['is_admin'] = bool(changes['is_admin'])
    ch['role'] = 'admin' if ch['is_admin'] else 'client'
  if 'enabled' in changes:
    ch['enabled'] = bool(changes['enabled'])
  if 'company' in changes:
    ch['company'] = clean(changes['company'], 120)
  if ch:
    u.update(**ch)
  return True


# ---------------------------------------------------------------- leads

@anvil.server.callable
def admin_leads():
  require_admin()
  out = []
  for l in app_tables.leads.search(tables.order_by('created', ascending=False)):
    out.append({'id': rid(l), 'name': l['name'], 'email': l['email'], 'company': l['company'] or '',
                'kind': l['kind'] or '', 'budget': l['budget'] or '', 'message': l['message'] or '',
                'status': l['status'] or 'new', 'created': l['created']})
  return out


@anvil.server.callable
def admin_update_lead(lead_id, status=None, delete=False):
  require_admin()
  l = by_id(app_tables.leads, lead_id)
  if l is None:
    return False
  if delete:
    l.delete()
    return True
  if status in LEAD_STATUSES:
    l['status'] = status
  return True
