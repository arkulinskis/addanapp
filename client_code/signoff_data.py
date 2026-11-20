"""Sign-off records: the 10 checks (from free guide 03, "AI-Built, Human-Signed": the sign-off checklist), how a
request's acceptance criteria become tick boxes, and the public sample (#signoff/sample).

Pure Python (no anvil imports): the browser (SignoffCard, the SignOff and AcceptDelivery dialogs) and the server
(server_code/signoff.py) both use it. Texts are English; the browser translates them (tp).
"""
import re

# (key, what the engineer confirms): the 10 things guide 03 tells buyers to demand from any AI-assisted vendor
CHECKS = [
  ('engineer', 'A named engineer is accountable for this change'),
  ('review', 'Every change was reviewed line by line'),
  ('tests', 'Automated tests run on every change, and they pass'),
  ('security', 'Security checked on purpose: inputs, server-side permissions, no secrets in the code'),
  ('packages', 'Every third-party package verified as real, maintained and needed'),
  ('data', 'Your data stayed out of public AI tools'),
  ('staging', 'Tested on a staging version before going live'),
  ('criteria', 'Each acceptance criterion tested'),
  ('repo', 'Readable, documented code in your repository'),
  ('rollback', 'A rollback plan: the previous version can be restored quickly'),
]
CHECK_KEYS = [k for k, _l in CHECKS]
DEFAULT_CRITERION = 'Works as described'
_BULLET = re.compile(r'^\s*(?:[-*•·–—]+|\d{1,2}[.)]|\[[ xX]?\])\s*')


def criteria_of(acceptance):
  """A request's acceptance criteria (free text) -> a list of criteria: one per line, bullets and numbers stripped.
  An empty field gives one criterion, 'Works as described'."""
  out = []
  for line in str(acceptance or '').replace('\r', '').split('\n'):
    s = line
    for _i in range(3):  # "- [ ] 1. text"
      s2 = _BULLET.sub('', s)
      if s2 == s:
        break
      s = s2
    s = s.strip()
    if s and s not in out:
      out.append(s[:300])
  return out[:30] or [DEFAULT_CRITERION]


def is_complete(checks, criteria):
  checks = checks or {}
  return all(bool(checks.get(k)) for k in CHECK_KEYS) and bool(criteria) and all(bool(c.get('ok')) for c in criteria)


# The public sample: the hero's AA-1042 from the demo workspace. The reviewer is shown by role, not by an invented
# name: a real record shows the consultant's own name from their account.
SAMPLE = {
  'ref': 'AA-1042',
  'title': 'Deposits for large-party reservations',
  'kind': 'Integration / API',
  'client': 'Bistro Laurier',
  'reviewer': 'Senior engineer, Addanapp',
  'date': (2026, 10, 23),
  'tests': 38,
  'criteria': ['Deposit required for 8+ guests', 'Stripe checkout on the booking page',
               'Automatic refund if cancelled 48h+ before', "Deposit shown in the manager's day view",
               'Deposit % configurable per restaurant (default 20%)',
               "Partial refunds and the 48h cutoff in the restaurant's time zone"],
  'note': ("AI drafted the Stripe flow, webhooks and 38 tests. I reviewed every change, fixed two edge cases "
           "(partial refunds, the time zone on the 48h cutoff) and ran the security checklist."),
}


def sample_record():
  """The sample in the same shape as serial.signoff() gives the browser."""
  y, m, d = SAMPLE['date']
  return {
    'reviewer': {'name': SAMPLE['reviewer'], 'initials': 'AA', 'is_admin': True, 'color': None},
    'checks': {k: True for k in CHECK_KEYS},
    'criteria': [{'text': c, 'ok': True} for c in SAMPLE['criteria']],
    'tests': SAMPLE['tests'], 'note': SAMPLE['note'], 'date': (y, m, d),
    'accepted': None, 'client_criteria': None, 'complete': True, 'sample': True,
  }
