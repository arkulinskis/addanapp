"""Demo data: three fictional clients with requests at every stage. Demo clients can't sign in."""
from datetime import timedelta

import anvil.server
from anvil.tables import app_tables

from .common import require_admin, now, next_ref

CLIENTS = [
  ('Marie Tremblay', 'Bistro Laurier', 'marie@demo.addanapp.com', '#D9487A'),
  ('David Chen', 'Northline Logistics', 'david@demo.addanapp.com', '#1F6B63'),
  ('Sofia Rossi', 'Atelier Rossi', 'sofia@demo.addanapp.com', '#B7791F'),
]

# (client index, title, kind, priority, status, progress, quote, days ago, description, acceptance, notes)
# notes: (days ago, 'admin'|'client', kind, body, internal)
REQUESTS = [
  (0, 'Deposits for large-party reservations', 'integration', 'high', 'in_progress', 72, 3800, 9,
   "Parties of 8+ should pay a 20% deposit when booking online. Deposits must be refundable up to 48h before the reservation.",
   "- Deposit required for 8+ guests\n- Stripe checkout on the booking page\n- Automatic refund if cancelled 48h+ before\n- Deposit shown in the manager's day view",
   [(8, 'admin', 'status', '', False),
    (7, 'admin', 'update', "Scoped with 6 acceptance criteria. Stripe Checkout with a webhook for refunds is the simplest robust option.", False),
    (5, 'admin', 'validated', "AI drafted the Stripe flow, webhooks and 38 tests. I reviewed every change: fixed two edge cases (partial refunds, timezone on the 48h cutoff) and ran the security checklist.", False),
    (4, 'client', 'comment', "Looks great so far. Can the deposit amount be configurable per restaurant?", False),
    (3, 'admin', 'update', "Yes. Added a per-restaurant deposit % setting (default 20%). No change to the quote, it fits the original scope.", False),
    (1, 'admin', 'internal', "Remember to switch the Stripe keys to live mode at handover.", True)]),
  (0, 'Gift card balance page', 'feature', 'normal', 'quoted', 0, 2400, 3,
   "Guests should be able to check their gift card balance online by entering the card code.",
   "- Public page, no login\n- Rate limited to prevent guessing\n- Shows balance and expiry date",
   [(2, 'admin', 'update', "Scoped. Includes rate limiting and a lookup log for your staff.", False)]),
  (0, 'Weekly covers report (PDF)', 'data', 'normal', 'delivered', 100, 1600, 30,
   "Every Monday, email managers a PDF with last week's covers per service and no-show rate.",
   "- PDF by email every Monday 7am\n- Covers per lunch/dinner service\n- No-show rate and top 5 busiest slots",
   [(26, 'admin', 'validated', "Report generator built and validated against 3 months of real data. Numbers match the POS export.", False)]),
  (1, 'Driver mobile check-in', 'new_app', 'high', 'in_progress', 40, 14500, 21,
   "Our 60 drivers need a mobile-first app to check in at each stop, take a photo of the delivery and capture a signature.",
   "- Works offline, syncs when back online\n- Photo + signature per stop\n- Dispatch dashboard updates live",
   [(19, 'admin', 'milestone', "Milestone 1 accepted: clickable prototype validated with two drivers.", False),
    (6, 'admin', 'update', "Offline sync is in. Testing on older Android phones this week.", False)]),
  (1, 'SSO with Google Workspace', 'integration', 'normal', 'scoping', 10, None, 2,
   "Staff should sign in to the dispatch dashboard with their company Google accounts.",
   "", [(1, 'admin', 'question', "Should drivers also use Google sign-in, or only office staff?", False)]),
  (1, 'Route optimisation v2', 'change', 'urgent', 'review', 95, 6200, 16,
   "Re-optimise routes when a delivery is added mid-day, keeping driver shift limits.",
   "- Re-optimise in under 10 seconds for 400 stops\n- Respect shift end times\n- Show changes to the driver",
   [(4, 'admin', 'validated', "Benchmarked at 3.2s for 400 stops. Reviewed and validated. Staging link sent by email.", False)]),
  (2, 'Inventory CSV import', 'feature', 'normal', 'new', 0, None, 0,
   "We'd like to upload our supplier's CSV every week and update stock levels automatically.",
   "- Map supplier columns once\n- Preview changes before applying\n- Keep an import history", []),
  (2, 'Fix: order emails going to spam', 'bug', 'high', 'delivered', 100, 450, 45,
   "Customers say order confirmations land in spam.", "- Pass SPF, DKIM and DMARC\n- Confirm with 3 inbox providers",
   [(43, 'admin', 'validated', "DNS records fixed and verified with Gmail, Outlook and Yahoo.", False)]),
]


@anvil.server.callable
def admin_seed_demo():
  me = require_admin()
  if app_tables.users.get(email=CLIENTS[0][2]) is not None:
    return "Demo data is already loaded."
  t = now()
  users = []
  for name, company, email, color in CLIENTS:
    users.append(app_tables.users.add_row(name=name, company=company, email=email, color=color, enabled=False,
                                          is_demo=True, role='client', is_admin=False, email_notifications=False,
                                          created=t - timedelta(days=60), last_seen=t - timedelta(hours=5)))
  for (ci, title, kind, prio, status, prog, quote, ago, desc, acc, notes) in REQUESTS:
    created = t - timedelta(days=ago, hours=3)
    eta = (t + timedelta(days=6 if status != 'delivered' else -ago + 10)).date() if quote else None
    r = app_tables.requests.add_row(
      ref=next_ref(), client=users[ci], title=title, kind=kind, priority=prio, status=status, progress=prog,
      quote_amount=quote, quote_note="Fixed price for the scope above, including review, tests and deployment." if quote else '',
      eta=eta, description=desc, acceptance=acc, project=CLIENTS[ci][1] + ' platform', budget='',
      created=created, updated=created, last_activity=created,
      admin_unread=status in ('new',), client_unread=status in ('quoted', 'review'),
      accepted_at=(t - timedelta(days=max(ago - 12, 1))) if status == 'delivered' else None)
    app_tables.notes.add_row(request=r, author=users[ci], kind='status', body='Request submitted by ' + users[ci]['name'], status_to='new',
                             internal=False, created=created)
    last = created
    for (d, who, nkind, body, internal) in notes:
      when = t - timedelta(days=d, hours=1)
      author = me if who == 'admin' else users[ci]
      if nkind == 'status':
        app_tables.notes.add_row(request=r, author=me, kind='status', body='', status_from='new', status_to='scoping',
                                 internal=False, created=when)
      else:
        app_tables.notes.add_row(request=r, author=author, kind=nkind, body=body, internal=internal, created=when)
      last = max(last, when)
    if status not in ('new',) and not any(n[2] == 'status' for n in notes):
      app_tables.notes.add_row(request=r, author=me, kind='status', body='', status_from='scoping', status_to=status,
                               internal=False, created=last + timedelta(minutes=5))
    r['last_activity'] = last
  return "Demo data loaded: 3 clients and %d requests." % len(REQUESTS)


@anvil.server.callable
def admin_clear_demo():
  require_admin()
  n = 0
  for u in app_tables.users.search(is_demo=True):
    for r in app_tables.requests.search(client=u):
      for note in app_tables.notes.search(request=r):
        note.delete()
      r.delete()
      n += 1
    u.delete()
  return "Removed demo data (%d requests)." % n
