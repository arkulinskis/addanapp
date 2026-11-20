"""Rows -> client-safe dicts. Clients never see other clients, emails of others, or internal notes."""
from .common import rid, initials, STATUS_LABEL, KIND_LABEL


def person(u, with_email=False):
  if u is None:
    return None
  d = {'id': rid(u), 'name': u['name'] or 'Unknown', 'initials': initials(u['name']), 'color': u['color'],
       'is_admin': bool(u['is_admin']), 'company': u['company'] or ''}
  if with_email:
    d['email'] = u['email']
  return d


def me(u):
  d = person(u, with_email=True)
  d.update({'phone': u['phone'] or '', 'email_notifications': u['email_notifications'] is not False,
            'role': u['role'] or 'client'})
  return d


def request(r, viewer_is_admin):
  return {
    'id': rid(r), 'ref': r['ref'], 'title': r['title'], 'kind': r['kind'], 'kind_label': KIND_LABEL.get(r['kind'], 'Request'),
    'priority': r['priority'] or 'normal', 'description': r['description'] or '', 'acceptance': r['acceptance'] or '',
    'project': r['project'] or '', 'budget': r['budget'] or '', 'desired_date': r['desired_date'],
    'status': r['status'], 'status_label': STATUS_LABEL.get(r['status'], r['status']),
    'progress': int(r['progress'] or 0), 'quote_amount': r['quote_amount'], 'quote_note': r['quote_note'] or '',
    'eta': r['eta'], 'created': r['created'], 'updated': r['updated'], 'last_activity': r['last_activity'],
    'accepted_at': r['accepted_at'],
    'unread': bool(r['admin_unread'] if viewer_is_admin else r['client_unread']),
    'client': person(r['client'], with_email=viewer_is_admin),
  }


def note(n, viewer):
  a = n['author']
  return {
    'id': rid(n), 'kind': n['kind'], 'body': n['body'] or '', 'internal': bool(n['internal']), 'created': n['created'],
    'author': person(a), 'mine': a is not None and viewer is not None and a == viewer,
    'status_from': n['status_from'], 'status_to': n['status_to'],
    'status_to_label': STATUS_LABEL.get(n['status_to'], n['status_to'] or ''), 'progress': n['progress'],
  }


def signoff(row):
  """A sign-off record (server_code/signoff.py) for the browser, or None."""
  if row is None:
    return None
  from . import signoff_data
  checks = row['checks'] or {}
  crit = [{'text': c.get('text') or '', 'ok': bool(c.get('ok'))} for c in (row['criteria'] or [])]
  client = row['client_criteria']
  return {
    'reviewer': person(row['reviewer']), 'checks': {k: bool(checks.get(k)) for k in signoff_data.CHECK_KEYS},
    'criteria': crit, 'tests': int(row['tests'] or 0), 'note': row['note'] or '', 'created': row['created'],
    'accepted': row['accepted'],
    'client_criteria': [{'text': c.get('text') or '', 'ok': bool(c.get('ok'))} for c in client] if client else None,
    'complete': signoff_data.is_complete(checks, crit),
  }
