"""Locked quotes and change orders.

A fixed price only protects a client if it can't drift silently. Once the client approves a quote (the request moves
from Quote ready to In progress, which writes a status note "Quote approved by <name> · $2,400 · ETA Nov 14"), the
quote is LOCKED: admin_update_request refuses a new amount. A consultant who needs to change scope, price or ETA sends
a change order (table `change_orders`, one pending per request); nothing changes until the client approves it, and a
declined (or withdrawn) order leaves price and ETA untouched. Every step is a note in the request's timeline with
before and after.

`change_orders` is a new table: until the user accepts the Schema Mismatch in the Anvil editor it doesn't exist, so
reads here are guarded (no orders) and sending one explains what to do.
"""
import anvil.tables as tables
from anvil.tables import app_tables

from .common import rid

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
LIVE = ('in_progress', 'review', 'on_hold')  # approved work that isn't delivered yet


def money(v):
  return '—' if v is None else '${:,.0f}'.format(v)


def signed(v):
  v = int(round(v or 0))
  return ('+' if v >= 0 else '-') + '${:,}'.format(abs(v))


def day(d):
  return '' if d is None else '%s %d' % (MONTHS[d.month - 1], d.day)


def table():
  try:
    return app_tables.change_orders
  except Exception:
    return None


def approval_note(r):
  """The note that records the client's approval of the quote (or the consultant starting work on it), or None."""
  try:
    for n in app_tables.notes.search(tables.order_by('created', ascending=True), request=r, kind='status',
                                     status_from='quoted'):
      if n['status_to'] == 'in_progress':
        return n
  except Exception:
    pass
  return None


def locked(r):
  """True once the client approved the quote: from then on only an approved change order changes the price."""
  return r['quote_amount'] is not None and approval_note(r) is not None


def orders_of(r):
  t = table()
  if t is None:
    return []
  try:
    return list(t.search(tables.order_by('created', ascending=True), request=r))
  except Exception:
    return []


def pending_of(r):
  for c in orders_of(r):
    if c['status'] == 'pending':
      return c
  return None


def pending_map(rows):
  """{request id: serial order} for the requests among rows that have a pending change order (one search)."""
  t = table()
  if t is None:
    return {}
  ids = {rid(r) for r in rows}
  out = {}
  try:
    for c in t.search(status='pending'):
      req = c['request']
      if req is not None and rid(req) in ids:
        out[rid(req)] = order(c)
  except Exception:
    return {}
  return out


def order(c):
  """A change order as a plain dict for the browser."""
  before, after = c['amount_before'], c['amount_after']
  by, dec = c['by'], c['decided_by']
  return {
    'id': rid(c), 'status': c['status'] or 'pending', 'reason': c['reason'] or '',
    'amount_before': before, 'amount_after': after, 'delta': (after or 0) - (before or 0),
    'eta_before': c['eta_before'], 'eta_after': c['eta_after'],
    'eta_changed': c['eta_after'] is not None and c['eta_after'] != c['eta_before'],
    'created': c['created'], 'decided': c['decided'],
    'by': by['name'] if by is not None else '', 'decided_by': dec['name'] if dec is not None else '',
  }


# ---------------------------------------------------------------- timeline lines (English; i18n.server_text translates)

def sent_line(c):
  """'Change order: +$600, new total $3,000, new ETA Nov 20: <reason>'"""
  parts = []
  if int(round(c['amount_after'] or 0)) != int(round(c['amount_before'] or 0)):
    parts.append('%s, new total %s' % (signed((c['amount_after'] or 0) - (c['amount_before'] or 0)), money(c['amount_after'])))
  if c['eta_after'] is not None and c['eta_after'] != c['eta_before']:
    parts.append('new ETA ' + day(c['eta_after']))
  return 'Change order: ' + ', '.join(parts) + (': ' + c['reason'] if c['reason'] else '')


def approved_line(name, c):
  """'Change order approved by Ana: $2,400 → $3,000 · ETA Nov 14 → Nov 20'"""
  parts = []
  if int(round(c['amount_after'] or 0)) != int(round(c['amount_before'] or 0)):
    parts.append('%s → %s' % (money(c['amount_before']), money(c['amount_after'])))
  if c['eta_after'] is not None and c['eta_after'] != c['eta_before']:
    parts.append('ETA %s → %s' % (day(c['eta_before']) or '—', day(c['eta_after'])))
  return 'Change order approved by %s: %s' % (name, ' · '.join(parts))


def declined_line(name):
  return 'Change order declined by %s: the original scope stays' % name


def withdrawn_line(name):
  return 'Change order withdrawn by %s' % name


def approval_line(name, r):
  """'Quote approved by Ana · $2,400 · ETA Nov 14': the approval records the amount (and ETA) the client agreed to."""
  return 'Quote approved by %s · %s' % (name, money(r['quote_amount'])) + (' · ETA ' + day(r['eta']) if r['eta'] else '')


# ---------------------------------------------------------------- the client's "no surprises" strip

def budget(rows):
  """Sums over a client's requests: approved & in progress, accepted, waiting for their OK (quotes + change orders)."""
  pend = pending_map(rows)
  approved = accepted = waiting = 0
  n_wait = 0
  for r in rows:
    q = r['quote_amount']
    st = r['status']
    if q is not None and st == 'delivered':
      accepted += q
    elif q is not None and st in LIVE and locked(r):
      approved += q
    elif q is not None and st == 'quoted':
      waiting += q
      n_wait += 1
    p = pend.get(rid(r))
    if p:
      waiting += p['delta']
      n_wait += 1
  return {'approved': approved, 'accepted': accepted, 'waiting': waiting, 'waiting_n': n_wait, 'hours': 0}
