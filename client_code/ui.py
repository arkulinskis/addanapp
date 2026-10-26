"""UI toolkit: constants, HTML builders, formatting, forms, server calls."""
import datetime

import anvil
import anvil.js
import anvil.server
import anvil.tz
from anvil import HtmlTemplate, Notification, alert, confirm

from .icons import icon
from .i18n import t, tn
from . import i18n

FAIL = object()

# ------------------------------------------------------------------ domain constants (mirror server)

STATUS = {
  'new': (t('Submitted'), '', '#8C94A3'),
  'scoping': (t('Scoping'), 'amber', '#B7791F'),
  'quoted': (t('Quote ready'), 'accent', '#2F5BFF'),
  'in_progress': (t('In progress'), 'ai', '#7A5CFA'),
  'review': (t('Ready for review'), 'accent', '#2F5BFF'),
  'delivered': (t('Delivered'), 'human', '#0E9F6E'),
  'on_hold': (t('On hold'), 'outline', '#8C94A3'),
  'declined': (t('Closed'), 'outline', '#B4AEA0'),
}
STATUS_ORDER = ['new', 'scoping', 'quoted', 'in_progress', 'review', 'delivered', 'on_hold', 'declined']
PIPELINE = [('new', t('Submitted')), ('scoping', t('Scoping')), ('quoted', t('Quote')), ('in_progress', t('Build')),
            ('review', t('Review')), ('delivered', t('Delivered'))]
OPEN_STATUSES = ['new', 'scoping', 'quoted', 'in_progress', 'review', 'on_hold']
CLIENT_ACTION = ['quoted', 'review']

KINDS = [('feature', t('New feature')), ('change', t('Improvement')), ('bug', t('Bug fix')), ('new_app', t('New app')),
         ('integration', t('Integration / API')), ('data', t('Data & reporting')), ('other', t('Other'))]
KIND = dict(KINDS)
PRIORITIES = [('low', t('Low')), ('normal', t('Normal')), ('high', t('High')), ('urgent', t('Urgent'))]
PRIORITY = dict(PRIORITIES)
PRIORITY_CLS = {'low': 'outline', 'normal': '', 'high': 'amber', 'urgent': 'red'}
# Budgets are saved in English (the value) and shown translated (the label).
BUDGETS = [(b, t(b)) for b in ['Not sure yet', 'Under $2,500', '$2,500 – $10,000', '$10,000 – $25,000',
                               '$25,000 – $75,000', '$75,000+']]
NOTE_KINDS = [('update', t('Progress update')), ('milestone', t('Milestone reached')),
              ('validated', t('Human-validated delivery')), ('question', t('Question for client')),
              ('internal', t('Internal note (hidden from client)'))]
NOTE_CHIP = {
  'update': (t('Update'), 'accent', 'activity'),
  'milestone': (t('Milestone'), 'ink', 'flag'),
  'validated': (t('AI-built · human-validated'), 'human', 'shield'),
  'question': (t('Question'), 'amber', 'help'),
  'internal': (t('Internal'), 'amber', 'lock'),
}


# ------------------------------------------------------------------ html basics

def esc(s):
  if s is None:
    return ''
  return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
          .replace('"', '&quot;').replace("'", '&#39;'))


def dom(component):
  return anvil.js.get_dom_node(component)


def H(markup='', actions=None):
  """An HtmlTemplate with delegated click actions: <button data-act="x" data-arg="y">."""
  h = HtmlTemplate(html=markup)
  if actions:
    bind(h, actions)
  return h


def bind(h, actions):
  node = dom(h)

  def handler(e):
    el = e.target.closest('[data-act]')
    if el is None or not node.contains(el):
      return
    fn = actions.get(el.getAttribute('data-act'))
    if fn is None:
      return
    if el.tagName == 'A' and not el.getAttribute('href'):
      e.preventDefault()
    fn(el.getAttribute('data-arg'))

  node.addEventListener('click', handler)
  return h


def q(component_or_node, sel):
  node = component_or_node if hasattr(component_or_node, 'querySelector') else dom(component_or_node)
  return node.querySelector(sel)


def qa(component_or_node, sel):
  node = component_or_node if hasattr(component_or_node, 'querySelector') else dom(component_or_node)
  res = node.querySelectorAll(sel)
  return [res.item(i) for i in range(res.length)]


def show(el, on=True):
  if el is None:
    return
  if on:
    el.classList.remove('hidden')
  else:
    el.classList.add('hidden')


def chip(text, cls='', ico=None, raw=False):
  i = icon(ico, 'width="13" height="13"') if ico else ''
  return f'<span class="chip {cls}">{i}{text if raw else esc(text)}</span>'


def status_chip(status):
  label, cls, _c = STATUS.get(status, (status or '?', '', '#999'))
  return f'<span class="chip {cls}"><span class="d"></span>{esc(label)}</span>'


def kind_chip(kind):
  return chip(KIND.get(kind, kind or t('Request')), 'outline')


def priority_chip(p):
  if not p or p == 'normal':
    return ''
  return chip(t('{level} priority', level=PRIORITY.get(p, p)), PRIORITY_CLS.get(p, ''))


def progress_bar(pct, done=False):
  pct = max(0, min(100, int(pct or 0)))
  return f'<div class="progress {"done" if done or pct >= 100 else ""}"><i style="width:{pct}%"></i></div>'


def avatar(person, size=32):
  if not person:
    return ''
  fs = max(10, int(size * 0.38))
  cls = 'av admin' if person.get('is_admin') else 'av'
  color = '' if person.get('is_admin') else f"background:{esc(person.get('color') or '#1D2840')};"
  return (f'<span class="{cls}" style="width:{size}px;height:{size}px;font-size:{fs}px;{color}" '
          f'title="{esc(person.get("name"))}">{esc(person.get("initials") or "?")}</span>')


def empty(ico, title, text='', button=''):
  return (f'<div class="empty"><div class="ico">{icon(ico)}</div><h3>{esc(title)}</h3>'
          f'<p>{esc(text)}</p>{button}</div>')


def options(items, selected=None, placeholder=None):
  out = f'<option value="">{esc(placeholder)}</option>' if placeholder is not None else ''
  for it in items:
    val, label = (it, it) if not isinstance(it, (list, tuple)) else (it[0], it[1])
    sel = ' selected' if selected is not None and str(val) == str(selected) else ''
    out += f'<option value="{esc(val)}"{sel}>{esc(label)}</option>'
  return out


def seg(name, items, selected=None, dots=None):
  out = f'<div class="seg" data-name="{name}" role="radiogroup">'
  for val, label in items:
    on = ' on' if val == selected else ''
    d = f'<span class="d" style="background:{dots[val]}"></span>' if dots and val in dots else ''
    out += f'<button type="button" class="{on.strip()}" data-val="{esc(val)}" role="radio">{d}{esc(label)}</button>'
  return out + '</div>'


def wire_segs(component):
  node = dom(component)

  def handler(e):
    b = e.target.closest('.seg button')
    if b is None or not node.contains(b):
      return
    group = b.closest('.seg')
    for other in qa(group, 'button'):
      other.classList.remove('on')
    b.classList.add('on')

  node.addEventListener('click', handler)


def vals(component):
  """Read every [name] input/select/textarea and .seg[data-name] group inside a component."""
  out = {}
  for el in qa(component, '[name]'):
    name = el.getAttribute('name')
    if el.type == 'checkbox':
      out[name] = bool(el.checked)
    else:
      out[name] = (el.value or '').strip()
  for g in qa(component, '.seg[data-name]'):
    b = g.querySelector('button.on')
    out[g.getAttribute('data-name')] = b.getAttribute('data-val') if b else None
  return out


def busy(btn_el, on=True, text=None):
  if btn_el is None:
    return
  if on:
    btn_el.classList.add('busy')
    if text:
      btn_el.setAttribute('data-label', btn_el.innerHTML)
      btn_el.textContent = text
  else:
    btn_el.classList.remove('busy')
    lbl = btn_el.getAttribute('data-label')
    if lbl:
      btn_el.innerHTML = lbl
      btn_el.removeAttribute('data-label')


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
    return t('just now')
  if secs < 3600:
    return t('{n} min ago', n=int(secs // 60))
  if secs < 86400:
    return t('{n} h ago', n=int(secs // 3600))
  if secs < 86400 * 7:
    n = int(secs // 86400)
    return t('yesterday') if n == 1 else tn(n, '{n} day ago', '{n} days ago')
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
    return t('Good morning')
  if h < 18:
    return t('Good afternoon')
  return t('Good evening')


# ------------------------------------------------------------------ feedback

def toast(msg, style='success', timeout=3.5):
  try:
    Notification(msg, style=style, timeout=timeout).show()
  except Exception:
    print(msg)


def modal(content, title=None, large=False, dismissible=True):
  return alert(content=content, title=title, large=large, buttons=[], dismissible=dismissible)


def close_modal(component, value=None):
  component.raise_event('x-close-alert', value=value)


def ask(text, title=None, yes=None, no=None):
  return confirm(text, title=title, buttons=[(no or t('Cancel'), False), (yes or t('Confirm'), True)])


def set_meta(title, description=None, private=False):
  try:
    anvil.js.window.aa.setMeta(title, description or '', 'private' if private else 'public')
  except Exception:
    pass


def reveal(component=None):
  try:
    anvil.js.window.aa.reveal(dom(component) if component is not None else None)
  except Exception:
    pass


def scroll_to(section_id):
  try:
    return anvil.js.window.aa.scrollTo(section_id)
  except Exception:
    return False


def call(fn_name, *args, **kwargs):
  """Server call with friendly errors. Returns FAIL on error."""
  quiet = kwargs.pop('_quiet', False)
  try:
    if quiet:
      return anvil.server.call_s(fn_name, *args, **kwargs)
    return anvil.server.call(fn_name, *args, **kwargs)
  except Exception as e:
    msg = str(e)
    if 'Please sign in' in msg:
      from . import state
      state.after_login = state.current_route()
      state.go('login')
      return FAIL
    for prefix in ('Exception: ', 'anvil.server.InternalError: '):
      if msg.startswith(prefix):
        msg = msg[len(prefix):]
    if not quiet:
      toast(i18n.server_text(msg) or t("Something went wrong. Please try again."), 'danger', 5)
    return FAIL
