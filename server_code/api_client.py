"""Client workspace API: profile, requests, comments, approvals."""
import datetime

import anvil.server
import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables

from . import serial
from .common import (current_user, rid, by_id, clean, now, next_ref, add_note, touch, notify_admins,
                     KINDS, PRIORITIES, OPEN_STATUSES)


# ---------------------------------------------------------------- profile

@anvil.server.callable
def get_me():
  u = current_user()
  touch(u)
  return serial.me(u)


@anvil.server.callable
def update_me(changes):
  u = current_user()
  ch = {}
  if 'name' in changes:
    name = clean(changes.get('name'), 80)
    if len(name) < 2:
      raise Exception("Please enter your name.")
    ch['name'] = name
  if 'company' in changes:
    ch['company'] = clean(changes.get('company'), 120)
  if 'phone' in changes:
    ch['phone'] = clean(changes.get('phone'), 40)
  if 'email_notifications' in changes:
    ch['email_notifications'] = bool(changes.get('email_notifications'))
  if ch:
    u.update(**ch)
  return serial.me(u)


@anvil.server.callable
def poll_counts():
  u = current_user(required=False)
  if u is None:
    return {}
  touch(u)
  if u['is_admin']:
    return {'unread': len(app_tables.requests.search(admin_unread=True)),
            'leads': len(app_tables.leads.search(status='new'))}
  return {'unread': len(app_tables.requests.search(client=u, client_unread=True))}


# ---------------------------------------------------------------- requests

def _load(request_id, u):
  r = by_id(app_tables.requests, request_id)
  if r is None:
    raise Exception("That request doesn't exist (or was removed).")
  if not u['is_admin'] and r['client'] != u:
    raise Exception("That request belongs to another workspace.")
  return r


def payload(r, u):
  admin = bool(u['is_admin'])
  notes = app_tables.notes.search(tables.order_by('created', ascending=True), request=r)
  out = [serial.note(n, u) for n in notes if admin or not n['internal']]
  return {'request': serial.request(r, admin), 'notes': out, 'is_admin': admin}


@anvil.server.callable
def my_requests():
  u = current_user()
  rows = app_tables.requests.search(tables.order_by('last_activity', ascending=False), client=u)
  reqs = [serial.request(r, False) for r in rows]
  stats = {
    'open': len([r for r in reqs if r['status'] in OPEN_STATUSES]),
    'action': len([r for r in reqs if r['status'] in ('quoted', 'review')]),
    'in_progress': len([r for r in reqs if r['status'] == 'in_progress']),
    'delivered': len([r for r in reqs if r['status'] == 'delivered']),
    'total': len(reqs),
  }
  return {'requests': reqs, 'stats': stats}


def _validate_request(data):
  title = clean(data.get('title'), 140)
  desc = clean(data.get('description'), 8000)
  if len(title) < 4:
    raise Exception("Give your request a short title (4+ characters).")
  if len(desc) < 10:
    raise Exception("Describe what you need in a sentence or two.")
  kind = data.get('kind') if data.get('kind') in KINDS else 'feature'
  priority = data.get('priority') if data.get('priority') in PRIORITIES else 'normal'
  desired = data.get('desired_date')
  if desired is not None and not isinstance(desired, datetime.date):
    desired = None
  return {
    'title': title, 'description': desc, 'kind': kind, 'priority': priority, 'desired_date': desired,
    'acceptance': clean(data.get('acceptance'), 6000), 'project': clean(data.get('project'), 120),
    'budget': clean(data.get('budget'), 60),
  }


def create_request_row(client, data, created_by):
  fields = _validate_request(data)
  t = now()
  r = app_tables.requests.add_row(
    ref=next_ref(), client=client, status='new', progress=0, created=t, updated=t, last_activity=t,
    admin_unread=not created_by['is_admin'], client_unread=bool(created_by['is_admin']), **fields)
  who = client['name'] if created_by == client else f"{created_by['name']} for {client['name']}"
  add_note(r, created_by, 'status', f"Request submitted by {who}", status_to='new')
  return r


@anvil.server.callable
def create_request(data):
  u = current_user()
  r = create_request_row(u, data, u)
  notify_admins(f"New request {r['ref']}: {r['title']}", f"New request from {u['name']}",
                [f"<b>{r['title']}</b>", (u['company'] or u['email']) + f" · {r['kind']} · {r['priority']} priority",
                 r['description'][:600].replace('\n', '<br>')], 'r/' + rid(r))
  return rid(r)


@anvil.server.callable
def get_request(request_id):
  u = current_user()
  r = _load(request_id, u)
  if u['is_admin'] and r['admin_unread']:
    r['admin_unread'] = False
  elif not u['is_admin'] and r['client_unread']:
    r['client_unread'] = False
  return payload(r, u)


def _set_status(r, u, status, body=''):
  old = r['status']
  if old == status:
    return
  ch = {'status': status, 'updated': now(), 'last_activity': now()}
  if status == 'delivered':
    ch['progress'] = 100
    ch['accepted_at'] = now()
  r.update(**ch)
  add_note(r, u, 'status', body, status_from=old, status_to=status)


@anvil.server.callable
def client_action(request_id, action, comment=''):
  u = current_user()
  r = _load(request_id, u)
  comment = clean(comment, 8000)
  name = u['name']
  path = 'r/' + rid(r)

  if action == 'comment':
    if len(comment) < 1:
      raise Exception("Write a message first.")
    add_note(r, u, 'comment', comment)
    r.update(last_activity=now(), admin_unread=not u['is_admin'], client_unread=bool(u['is_admin']))
    if not u['is_admin']:
      notify_admins(f"{r['ref']}: new comment from {name}", f"{name} commented on {r['ref']}",
                    [f"<b>{r['title']}</b>", comment[:800].replace('\n', '<br>')], path)
  elif action == 'approve_quote':
    if r['status'] != 'quoted':
      raise Exception("There's no quote waiting for approval on this request.")
    _set_status(r, u, 'in_progress', f"Quote approved by {name}" + (f": {comment}" if comment else ''))
    r['admin_unread'] = True
    notify_admins(f"{r['ref']}: quote approved", f"{name} approved the quote for {r['ref']}",
                  [f"<b>{r['title']}</b>", "The request moved to In progress. Time to build."], path)
  elif action == 'accept':
    if r['status'] != 'review':
      raise Exception("This request isn't ready for review yet.")
    _set_status(r, u, 'delivered', f"Delivery accepted by {name}" + (f": {comment}" if comment else ''))
    r['admin_unread'] = True
    notify_admins(f"{r['ref']}: delivery accepted", f"{name} accepted {r['ref']}",
                  [f"<b>{r['title']}</b>", "Accepted. It can be invoiced now."], path)
  elif action == 'request_changes':
    if r['status'] != 'review':
      raise Exception("This request isn't in review.")
    if len(comment) < 3:
      raise Exception("Tell us what should change.")
    _set_status(r, u, 'in_progress', "Changes requested")
    add_note(r, u, 'comment', comment)
    r['admin_unread'] = True
    notify_admins(f"{r['ref']}: changes requested", f"{name} requested changes on {r['ref']}",
                  [f"<b>{r['title']}</b>", comment[:800].replace('\n', '<br>')], path)
  elif action == 'withdraw':
    if r['status'] not in ('new', 'scoping', 'quoted', 'on_hold'):
      raise Exception("Work has already started on this request. Leave a comment and we'll sort it out together.")
    _set_status(r, u, 'declined', f"Withdrawn by {name}" + (f": {comment}" if comment else ''))
    r['admin_unread'] = True
    notify_admins(f"{r['ref']}: withdrawn", f"{name} withdrew {r['ref']}", [f"<b>{r['title']}</b>", comment], path)
  else:
    raise Exception("Unknown action.")
  return payload(r, u)
