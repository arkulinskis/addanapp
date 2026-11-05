"""Shared constants (mirroring the server), formatting, chips and the server-call wrapper.

    ui.call(fn, *args)          anvil.server.call with friendly errors: the server raises Exception("message") for
                                normal problems; that message is shown (translated) and FAIL is returned
    ui.chip(label, text, cls)   set a Label up as a chip (roles chip + chip-<cls>); ui.status_chip(label, status)
    ui.fmt_date / fmt_dt / ago / money / greeting    dates and amounts in the visitor's language
"""
import datetime

import anvil.js
import anvil.server
import anvil.tz

from .i18n import t, tn, tp
from . import i18n

FAIL = object()

# ------------------------------------------------------------------ domain constants (mirror server)

STATUS = {
  'new': (tp('Submitted'), '', '#8C94A3'),
  'scoping': (tp('Scoping'), 'amber', '#B7791F'),
  'quoted': (tp('Quote ready'), 'accent', '#2F5BFF'),
  'in_progress': (tp('In progress'), 'ai', '#7A5CFA'),
  'review': (tp('Ready for review'), 'accent', '#2F5BFF'),
  'delivered': (tp('Delivered'), 'human', '#0E9F6E'),
  'on_hold': (tp('On hold'), 'outline', '#8C94A3'),
  'declined': (tp('Closed'), 'outline', '#B4AEA0'),
}
STATUS_ORDER = ['new', 'scoping', 'quoted', 'in_progress', 'review', 'delivered', 'on_hold', 'declined']
PIPELINE = [('new', tp('Submitted')), ('scoping', tp('Scoping')), ('quoted', tp('Quote')), ('in_progress', tp('Build')),
            ('review', tp('Review')), ('delivered', tp('Delivered'))]
OPEN_STATUSES = ['new', 'scoping', 'quoted', 'in_progress', 'review', 'on_hold']
CLIENT_ACTION = ['quoted', 'review']

KINDS = [('feature', tp('New feature')), ('change', tp('Improvement')), ('bug', tp('Bug fix')), ('new_app', tp('New app')),
         ('integration', tp('Integration / API')), ('data', tp('Data & reporting')), ('other', tp('Other'))]
KIND = dict(KINDS)
PRIORITIES = [('low', tp('Low')), ('normal', tp('Normal')), ('high', tp('High')), ('urgent', tp('Urgent'))]
PRIORITY = dict(PRIORITIES)
PRIORITY_CLS = {'low': 'outline', 'normal': '', 'high': 'amber', 'urgent': 'red'}
# Budgets are saved in English (the value) and shown translated (the label).
BUDGETS = [(b, tp(b)) for b in ['Not sure yet', 'Under $2,500', '$2,500 – $10,000', '$10,000 – $25,000',
                                '$25,000 – $75,000', '$75,000+']]
NOTE_KINDS = [('update', tp('Progress update')), ('milestone', tp('Milestone reached')),
              ('validated', tp('Human-validated delivery')), ('question', tp('Question for client')),
              ('internal', tp('Internal note (hidden from client)'))]
NOTE_CHIP = {
  'update': (tp('Update'), 'accent', 'activity'),
  'milestone': (tp('Milestone'), 'ink', 'flag'),
  'validated': (tp('AI-built · human-validated'), 'human', 'shield'),
  'question': (tp('Question'), 'amber', 'help'),
  'internal': (tp('Internal'), 'amber', 'lock'),
}


def dd_items(pairs):
  """[(value, label)] -> a DropDown's items [(label, value)]."""
  return [(label, value) for value, label in pairs]


# ------------------------------------------------------------------ chips (Labels with roles)

def chip_roles(cls='', dot=False, ico=None):
  roles = ['chip'] + ['chip-' + c for c in cls.split() if c]
  if dot:
    roles.append('chip-dot')
  if ico:
    roles += ['chip-ic', 'ic-' + ico]
  return roles


def chip(label, text, cls='', dot=False, ico=None):
  label.text = text
  label.role = chip_roles(cls, dot, ico)
  label.visible = bool(text)


def status_chip(label, status):
  text, cls, _c = STATUS.get(status, (status or '?', '', '#999'))
  chip(label, text, cls, dot=True)


def priority_chip(label, p):
  if not p or p == 'normal':
    label.visible = False
    return
  chip(label, tp('{level} priority', level=PRIORITY.get(p, p)), PRIORITY_CLS.get(p, ''))


def first_name(person):
  return ((person or {}).get('name') or '').split(' ')[0]


# ------------------------------------------------------------------ formatting

def local(d):
  if d is None:
    return None
  try:
    if isinstance(d, datetime.datetime) and d.tzinfo is not None:
      return d.astimezone(anvil.tz.tzlocal())
  except Exception:
    pass
  return d


def now_local():
  return datetime.datetime.now(anvil.tz.tzlocal())


def fmt_date(d, year=None):
  if d is None:
    return ''
  d = local(d)
  return i18n.date_text(d, year or (year is None and d.year != now_local().year))


def fmt_dt(d):
  if d is None:
    return ''
  d = local(d)
  return f"{fmt_date(d)} · {d.hour:02d}:{d.minute:02d}"


def ago(d):
  if d is None:
    return ''
  try:
    secs = (now_local() - local(d)).total_seconds()
  except Exception:
    return fmt_date(d)
  if secs < 60:
    return tp('just now')
  if secs < 3600:
    return tp('{n} min ago', n=int(secs // 60))
  if secs < 86400:
    return tp('{n} h ago', n=int(secs // 3600))
  if secs < 86400 * 7:
    n = int(secs // 86400)
    return tp('yesterday') if n == 1 else tn(n, '{n} day ago', '{n} days ago')
  return fmt_date(d)


def money(v):
  if v is None or v == '':
    return '—'
  return i18n.money(int(round(float(v))))


def date_iso(d):
  if d is None:
    return ''
  return f"{d.year:04d}-{d.month:02d}-{d.day:02d}"


def parse_date(s):
  if not s:
    return None
  try:
    y, m, d = s.split('-')
    return datetime.date(int(y), int(m), int(d))
  except Exception:
    return None


def greeting():
  h = now_local().hour
  if h < 12:
    return tp('Good morning')
  if h < 18:
    return tp('Good afternoon')
  return tp('Good evening')


# ------------------------------------------------------------------ page effects (theme/assets/aa.js)

def set_meta(title, description=None, private=False):
  try:
    anvil.js.window.aa.setMeta(title, description or '', 'private' if private else 'public')
  except Exception:
    pass


def reveal(component=None):
  """Scroll-reveal (.rv elements fade in as they come into view)."""
  try:
    anvil.js.window.aa.reveal(anvil.js.get_dom_node(component) if component is not None else None)
  except Exception:
    pass


def spy():
  """Light up the header link of the home-page section in view (sections carry data-ch)."""
  try:
    anvil.js.window.aa.spy()
  except Exception:
    pass


def scroll_to(section_id):
  try:
    return anvil.js.window.aa.scrollTo(section_id)
  except Exception:
    return False


def scroll_into_view(component, block='center'):
  try:
    anvil.js.get_dom_node(component).scrollIntoView({'behavior': 'smooth', 'block': block})
  except Exception:
    pass


# ------------------------------------------------------------------ server calls

def call(fn_name, *args, **kwargs):
  """Server call with friendly errors. Returns FAIL on error (the message is already shown)."""
  from . import state
  quiet = kwargs.pop('_quiet', False)
  try:
    if quiet:
      return anvil.server.call_s(fn_name, *args, **kwargs)
    return anvil.server.call(fn_name, *args, **kwargs)
  except Exception as e:
    msg = str(e)
    if 'Please sign in' in msg:
      state.need_sign_in()
      return FAIL
    for prefix in ('Exception: ', 'anvil.server.InternalError: '):
      if msg.startswith(prefix):
        msg = msg[len(prefix):]
    if not quiet:
      state.toast(i18n.plain(i18n.server_text(msg) or t("Something went wrong. Please try again.")), 'error')
    return FAIL
