"""Consultant console API: every request, progress notes, status, quotes, clients, leads."""
import datetime

import anvil
import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables

from . import serial, quotes, signoff
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
  new_status = (changes or {}).get('status')
  if new_status == 'review' and r['status'] != 'review' and signoff.needs(r) and not signoff.ready(r):
    # "Signed off by senior engineers" is a record, not a promise: no sign-off, no review (App Board requests skip it)
    raise Exception("Sign off the delivery first: tick the 10 checks and every acceptance criterion, then mark it ready.")
  update_request_as(u, r, changes, note)
  return payload(r, u)


def update_request_as(u, r, changes=None, note=None):
  """The work of admin_update_request, as consultant u (the Apps API uses it for Claude's notes)."""
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
    same = (qa is None and r['quote_amount'] is None) or (
      qa is not None and r['quote_amount'] is not None and int(round(qa)) == int(round(r['quote_amount'])))
    if not same:
      if quotes.locked(r):
        raise Exception("The client approved this quote, so it's locked. Send a change order to change the price.")
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
  if new_status in ('new', 'scoping', 'quoted') and new_status != r['status'] and quotes.locked(r):
    raise Exception("The client approved this quote. To change scope or price, send a change order.")
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
  return r


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
  for tab in (quotes.table(), signoff.table()):
    if tab is not None:
      for x in tab.search(request=r):
        x.delete()
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
                'status': l['status'] or 'new', 'created': l['created'], 'source': l['source'] or ''})
  return out


@anvil.server.callable
def admin_newsletter_csv():
  """Everyone who ticked the tips box on the guides page, with their consent record, as a CSV file."""
  require_admin()
  import csv
  import io
  import re
  buf = io.StringIO()
  w = csv.writer(buf)
  w.writerow(['email', 'name', 'situation', 'first_request_utc', 'consent_record'])
  for l in app_tables.leads.search(tables.order_by('created', ascending=True), source='guide+news'):
    m = re.search(r'Newsletter: yes\. Ticked ".*?" on [^(]*\([^)]*\)\.', l['message'] or '')
    w.writerow([l['email'], l['name'] or '', l['kind'] or '',
                l['created'].strftime('%Y-%m-%d %H:%M') if l['created'] else '', m.group(0) if m else ''])
  return anvil.BlobMedia('text/csv', buf.getvalue().encode('utf-8-sig'), name='addanapp-tips-subscribers.csv')


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


# ---------------------------------------------------------------- change orders (quotes.py)

@anvil.server.callable
def admin_send_change_order(request_id, amount, eta=None, reason=''):
  """After the client approved a quote, a change of price or ETA is a change order the client approves first."""
  u = require_admin()
  r = by_id(app_tables.requests, request_id)
  if r is None:
    raise Exception("Request not found.")
  t = quotes.table()
  if t is None:
    raise Exception("Change orders need a database update first: accept the schema change in the Anvil editor.")
  if r['status'] in ('delivered', 'declined'):
    raise Exception("This request is closed. New work goes in a new request.")
  if not quotes.locked(r):
    raise Exception("There's no approved quote to change yet. Until the client approves it, edit the quote itself.")
  if quotes.pending_of(r) is not None:
    raise Exception("A change order is already waiting for the client. Withdraw it first to send a different one.")
  try:
    amount = float(amount)
  except (TypeError, ValueError):
    raise Exception("Enter the new total price.")
  if amount < 0:
    raise Exception("Quotes can't be negative.")
  if eta is not None and not isinstance(eta, datetime.date):
    eta = None
  reason = clean(reason, 2000)
  if len(reason) < 10:
    raise Exception("Explain the change in a sentence (10 characters or more): the client approves it on that basis.")
  same_price = int(round(amount)) == int(round(r['quote_amount'] or 0))
  if same_price and (eta is None or eta == r['eta']):
    raise Exception("Change the price or the ETA: otherwise there's nothing for the client to approve.")
  stamp = now()
  co = t.add_row(request=r, by=u, amount_before=r['quote_amount'], amount_after=amount, eta_before=r['eta'],
                 eta_after=eta or r['eta'], reason=reason, status='pending', created=stamp, decided=None, decided_by=None)
  add_note(r, u, 'change', quotes.sent_line(co))
  r.update(last_activity=stamp, updated=stamp, client_unread=True)
  delta = amount - (r['quote_amount'] or 0)
  new_eta = co['eta_after'] if co['eta_after'] != co['eta_before'] else None

  def build(tr):
    lines = []
    if not same_price:
      lines.append(tr("Your engineer proposes a change order: {delta} (new total {total}).",
                      delta=('+' if delta >= 0 else '-') + tr.money(abs(delta)), total=tr.money(amount)))
    if new_eta:
      lines.append(tr("New ETA: {date}.", date=tr.date(new_eta)))
    lines.append(tr("Why: {reason}", reason=reason[:800].replace('<', '&lt;').replace('\n', '<br>')))
    lines.append(tr("Nothing changes unless you approve it in your workspace. If you keep the original scope, the approved price and ETA stay."))
    return (tr("{ref}: a change order needs your OK", ref=r['ref']), r['title'], lines)
  notify_client(r, build)
  return payload(r, u)


@anvil.server.callable
def admin_cancel_change_order(request_id):
  """Withdraw a change order the client hasn't decided on yet (a typo, or the scope worked out after all)."""
  u = require_admin()
  r = by_id(app_tables.requests, request_id)
  if r is None:
    raise Exception("Request not found.")
  co = quotes.pending_of(r)
  if co is None:
    raise Exception("There's no change order waiting on this request.")
  stamp = now()
  co.update(status='withdrawn', decided=stamp, decided_by=u)
  add_note(r, u, 'status', quotes.withdrawn_line(u['name']))
  r.update(last_activity=stamp, updated=stamp, client_unread=True)
  notify_client(r, lambda tr: (tr("{ref}: progress update", ref=r['ref']), tr("Update on {title}", title=r['title']),
                               [tr("The change order was withdrawn. The approved price and ETA stay as they were.")]))
  return payload(r, u)
