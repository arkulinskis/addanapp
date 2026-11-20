"""Sign-off records: a senior engineer's signed record of a delivery (the 10 checks from free guide 03, the automated
tests, each acceptance criterion ticked, a reviewer note), required before a client request can be marked Ready for
review, and the client's own tick per criterion when they accept the delivery (or ask for changes).

Table `signoffs` (one row per request, server-only). It is new: until the user accepts the Schema Mismatch in the
Anvil editor it doesn't exist, so every read here is guarded (no record, and no "sign off first" guard) and the rest
of the app keeps working in between.

App Board requests (a client with an app portfolio, apps_core.has_portfolio) don't need one: Claude's "Changes for
Claude" flow (apps_sync.a_done) moves them to review directly.
"""
import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables

from . import apps_core, signoff_data
from .common import require_admin, by_id, clean, now, add_note, notify_client

CHECK_KEYS = signoff_data.CHECK_KEYS


def table():
  try:
    return app_tables.signoffs
  except Exception:
    return None


def row_of(r):
  t = table()
  if t is None or r is None:
    return None
  try:
    return t.get(request=r)
  except Exception:
    return None


def needs(r):
  """Client requests need a sign-off before review; App Board requests (portfolio clients) don't."""
  return table() is not None and not apps_core.has_portfolio(r['client'])


def complete(row):
  return row is not None and signoff_data.is_complete(row['checks'], row['criteria'] or [])


def _changes_requested_at(r):
  try:
    for n in app_tables.notes.search(tables.order_by('created', ascending=False), request=r, kind='status',
                                     status_from='review'):
      if n['status_to'] == 'in_progress':
        return n['created']
  except Exception:
    pass
  return None


def ready(r, row=None):
  """A complete sign-off, saved after the client last asked for changes (a changed delivery is signed off again)."""
  row = row if row is not None else row_of(r)
  if not complete(row):
    return False
  asked = _changes_requested_at(r)
  return asked is None or (row['created'] is not None and row['created'] > asked)


def _signature(row):
  if row is None:
    return None
  return (repr(sorted((row['checks'] or {}).items())), repr(row['criteria']), row['tests'], row['note'])


@anvil.server.callable
def admin_save_signoff(request_id, data):
  """Save the sign-off record (consultants). A complete one (10/10 checks, every criterion) posts a client-visible
  'validated' note and emails the client; an incomplete one is kept as a draft."""
  u = require_admin()
  r = by_id(app_tables.requests, request_id)
  if r is None:
    raise Exception("Request not found.")
  t = table()
  if t is None:
    raise Exception("Sign-off records need a database update first: accept the schema change in the Anvil editor.")
  row = row_of(r)
  if row is not None and row['accepted'] is not None:
    raise Exception("The client accepted this delivery: its sign-off record is final.")
  data = data or {}
  given = data.get('checks') or {}
  checks = {k: bool(given.get(k)) for k in CHECK_KEYS}
  criteria = []
  for c in (data.get('criteria') or [])[:30]:
    text = clean((c or {}).get('text'), 300)
    if text:
      criteria.append({'text': text, 'ok': bool(c.get('ok'))})
  if not criteria:
    criteria = [{'text': x, 'ok': False} for x in signoff_data.criteria_of(r['acceptance'])]
  try:
    tests = int(data.get('tests') or 0)
  except (TypeError, ValueError):
    raise Exception("Tests: enter how many automated tests pass (a whole number).")
  if tests < 0 or tests > 1000000:
    raise Exception("Tests: enter how many automated tests pass (a whole number).")
  note = clean(data.get('note'), 2000)
  was_ready = ready(r, row) if row is not None else False
  before = _signature(row)
  stamp = now()
  fields = dict(reviewer=u, checks=checks, criteria=criteria, tests=tests, note=note, created=stamp)
  if row is None:
    row = t.add_row(request=r, client_criteria=None, accepted=None, **fields)
  else:
    row.update(client_criteria=None, **fields)  # a new round: the client ticks the criteria again
  if complete(row) and (not was_ready or _signature(row) != before):
    name = u['name']
    n = len(CHECK_KEYS)
    add_note(r, u, 'validated', "Signed off by %s: %d/%d checks · %d tests" % (name, n, n, tests))
    r.update(last_activity=stamp, updated=stamp, client_unread=True)
    notify_client(r, lambda tr: (
      tr("{ref}: progress update", ref=r['ref']), tr("Update on {title}", title=r['title']),
      [tr("Signed off by {name}: {n}/{total} checks · {tests} tests", name=name, n=n, total=n, tests=tests),
       tr("Each acceptance criterion was tested. The full sign-off record is in your workspace.")]))
  from .api_client import payload
  return payload(r, u)


def client_result(row, ticks):
  """The client's ticks (list of bools, in the order of the record's criteria) -> [{text, ok}]."""
  crit = row['criteria'] or []
  ticks = list(ticks or [])
  return [{'text': c.get('text'), 'ok': bool(ticks[i]) if i < len(ticks) else False} for i, c in enumerate(crit)]
