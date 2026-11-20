"""The 60-second ballpark estimator (#estimate): the questions, the result and the share code.

Pure Python (no anvil imports): the Estimate page uses it in the browser, and the server uses the same module to write
the estimate into a lead (api_public.submit_lead), so both always agree and the browser can't send its own price.

Prices come ONLY from the published pricing page (tools/seo_pages/pricing.json, addanapp.com/pricing):
  Launch $30,000 · Operate +$45,000 = $75,000 · Scale +$75,000 = $150,000 · Complete +$150,000 = $300,000
  A change to an app we run: a fixed quote per request, usually within 2 business days (sample: $2,400, 6 days).
  Taking over an app: a short fixed-price audit first (no published price, so none is shown).
Change a price there first, then here. Texts are English: the page translates them (tp), the lead keeps English.

    answers = decode('a0110000')      # {question key: value}; a bad code gives the defaults
    res = result(answers)             # {'key', 'name', 'price', 'level', 'path', 'included', 'why', 'notes'}
    encode(answers) -> 'a0110000'     # #estimate/<code> reopens the same result
"""

# (key, question, [(value, label)]): the first choice is the default (the smallest version of each answer)
QUESTIONS = [
  ('need', 'What do you need?',
   [('new', 'A new product'), ('change', 'A change to an app we run'), ('takeover', 'Take over or fix an app')]),
  ('flows', 'How many workflows?',
   [('1', 'One'), ('2-3', 'Two or three'), ('4+', 'Four or more')]),
  ('users', 'Who will use it?',
   [('team', 'Your team'), ('customers', 'Your team + customers or partners'), ('groups', 'Several groups of people')]),
  ('connect', 'Connections to other tools?',
   [('none', 'None'), ('few', 'One or two (e.g. Stripe, QuickBooks)'), ('many', 'Many')]),
  ('data', 'Data to bring in?',
   [('none', 'None'), ('sheets', 'Spreadsheets'), ('legacy', 'An old system')]),
  ('formal', 'Formal requirements?',
   [('no', 'None'), ('yes', 'Security review, Law 25 or WCAG')]),
  ('after', 'After launch?',
   [('own', 'Our team takes over'), ('support', '12 months of support + an installable app')]),
]
KEYS = [q[0] for q in QUESTIONS]

# (key, name, cumulative price, this milestone's own price, what it adds): from pricing.json, word for word in spirit
MILESTONES = [
  ('launch', 'Launch', 30000, 30000,
   ['A discovery workshop on scope, users and the workflow that matters most', 'That workflow built end to end',
    'Accounts and roles', 'A basic admin panel', 'Live in production, with code review and tests']),
  ('operate', 'Operate', 75000, 45000,
   ['The next workflows on your roadmap', 'Integrations with payments, accounting, CRM and email',
    'Notifications to staff and customers', 'First reports']),
  ('scale', 'Scale', 150000, 75000,
   ['A second user group: a client or partner portal, or a staff app', 'A data platform and dashboards',
    'Automation of repetitive work', 'Performance work', 'A security review', 'A Québec Law 25 privacy file',
    'WCAG 2.2 AA accessibility']),
  ('complete', 'Complete', 300000, 150000,
   ['The remaining roadmap', 'A mobile-first installable app', 'Migration of data from old systems',
    'Staff training and documentation', 'Monitoring', '12 months of support and maintenance']),
]

# (question, value): (the milestone it needs, why in a few words)
TRIGGERS = {
  ('flows', '2-3'): (1, 'Two or three workflows'),
  ('flows', '4+'): (2, 'Four or more workflows'),
  ('users', 'customers'): (2, 'Customers or partners use it too'),
  ('users', 'groups'): (2, 'Several groups of people use it'),
  ('connect', 'few'): (1, 'One or two connections to other tools'),
  ('connect', 'many'): (1, 'Many connections to other tools'),
  ('data', 'legacy'): (3, 'Data moves over from an old system'),
  ('formal', 'yes'): (2, 'A security review, Law 25 file or WCAG'),
  ('after', 'support'): (3, '12 months of support and an installable app'),
}
BASE_WHY = 'One workflow for your team, live in production'
SHEETS_WHY = 'Spreadsheets are imported as part of the first workflow'

REQUEST_NOTES = ['A fixed quote per request, usually within 2 business days',
                 'Sample quote: $2,400, delivered in 6 days',
                 'You pay only when you accept the delivery']
AUDIT_NOTES = ['A short fixed-price audit of the code comes first',
               'We document the risks, then quote improvements request by request',
               'New product work after that follows the same milestones']

# What goes into the lead (api_public): the brief form's English choices
LEAD_KIND = {'new': 'A new app or product', 'change': 'A feature for an existing app', 'takeover': 'Taking over an existing app'}
LEAD_BUDGET = {'launch': '$30k – $75k', 'operate': '$75k – $150k', 'scale': '$150k – $300k', 'complete': '$300k+',
               'request': 'Under $30k', 'audit': 'Not sure yet'}


def defaults():
  return {k: choices[0][0] for k, _q, choices in QUESTIONS}


def clean(answers):
  """Only known questions and values; anything else becomes the default."""
  out = defaults()
  for k, _q, choices in QUESTIONS:
    v = (answers or {}).get(k)
    if v in [c[0] for c in choices]:
      out[k] = v
  return out


def encode(answers):
  a = clean(answers)
  code = 'a'
  for k, _q, choices in QUESTIONS:
    code += str([c[0] for c in choices].index(a[k]))
  return code


def decode(code):
  code = str(code or '')
  if len(code) != len(QUESTIONS) + 1 or code[0] != 'a':
    return defaults()
  out = {}
  for i, (k, _q, choices) in enumerate(QUESTIONS):
    ch = code[i + 1]
    n = int(ch) if ch.isdigit() else 0
    out[k] = choices[n][0] if n < len(choices) else choices[0][0]
  return out


def label(key, value):
  for k, _q, choices in QUESTIONS:
    if k == key:
      for v, lbl in choices:
        if v == value:
          return lbl
  return value


def money_en(n):
  return '${:,}'.format(int(n))


def result(answers):
  a = clean(answers)
  path = [{'key': k, 'name': nm, 'price': price, 'step': step, 'on': False} for k, nm, price, step, _inc in MILESTONES]
  if a['need'] == 'change':
    return {'key': 'request', 'name': 'Per request', 'price': None, 'level': -1, 'path': path, 'included': [],
            'why': [], 'notes': list(REQUEST_NOTES)}
  if a['need'] == 'takeover':
    return {'key': 'audit', 'name': 'Audit first', 'price': None, 'level': -1, 'path': path, 'included': [],
            'why': [], 'notes': list(AUDIT_NOTES)}
  level, why = 0, []
  for k in KEYS:
    hit = TRIGGERS.get((k, a[k]))
    if hit:
      level = max(level, hit[0])
      why.append({'text': hit[1], 'milestone': MILESTONES[hit[0]][1], 'level': hit[0]})
  why.sort(key=lambda w: -w['level'])
  for w in why:
    w['decides'] = w['level'] == level
  if not why:
    why = [{'text': BASE_WHY, 'milestone': 'Launch', 'level': 0, 'decides': True}]
  if a['data'] == 'sheets':
    why.append({'text': SHEETS_WHY, 'milestone': 'Launch', 'level': 0, 'decides': level == 0})
  for i, p in enumerate(path):
    p['on'] = i <= level
  key, name, price, _step, _inc = MILESTONES[level]
  included = [{'milestone': MILESTONES[i][1], 'items': list(MILESTONES[i][4])} for i in range(level + 1)]
  return {'key': key, 'name': name, 'price': price, 'level': level, 'path': path, 'included': included, 'why': why,
          'notes': []}


def summary(answers):
  """The answers in plain English, for the lead the estimate is sent with."""
  a = clean(answers)
  keys = KEYS if a['need'] == 'new' else ['need']
  return '; '.join(q + ' ' + label(k, a[k]) for k, q, _c in QUESTIONS if k in keys)


def headline(res):
  """'Operate (~$75,000)' / 'Per request' / 'Audit first' in English, for the lead."""
  if res.get('price'):
    return '%s (~%s)' % (res['name'], money_en(res['price']))
  return res['name']
