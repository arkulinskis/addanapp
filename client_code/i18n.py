"""Translations: English (built in), French, Russian and Latvian.

English is the source text and needs no download. The other languages are JSON packs in the theme
assets (theme/assets/lang-fr.json, lang-ru.json, lang-lv.json) keyed by the English text. A pack is
only fetched when the visitor picked that language: the choice is saved in localStorage ('aa.lang'),
a small script in the page head (anvil.yaml -> native_deps) starts the download early, and this
module waits for it before any page is built. Changing language saves the choice and reloads.

  t("Hello {name}", name=x)              translated text; {placeholders} are filled in
  tp("Save &amp; notify client")         the same as plain text (for a Button/Label: no HTML entities)
  tn(n, "{n} request", "{n} requests")   plural-aware (French, Russian and Latvian rules)
  apply(form, products=53)               translates a form's template: every element marked data-t (its inner
                                         HTML is the English key; data-tv="n:products" fills {n}), data-ta
                                         attributes, and the text/placeholder/tooltip of its Buttons, Labels,
                                         Links and boxes. Call it at the end of every form's __init__.

A missing translation falls back to English, so new strings never break a page.
When you bump VERSION here, bump ?v= in the head script too (it busts the browser cache).
"""
import json
import re

import anvil.js
from anvil.js import window

LANGS = [('en', 'English'), ('fr', 'Français'), ('ru', 'Русский'), ('lv', 'Latviešu')]
CODES = [c for c, _n in LANGS]
NAMES = dict(LANGS)
STORAGE_KEY = 'aa.lang'
VERSION = '18'


def _stored():
  try:
    v = window.localStorage.getItem(STORAGE_KEY)
  except Exception:
    return 'en'
  return v if v in CODES else 'en'


lang = _stored()
_pack = {}


def _load():
  global lang, _pack
  if lang == 'en':
    return
  try:
    p = None
    try:
      p = window.aaLangPack
    except Exception:
      p = None
    if p:
      text = anvil.js.await_promise(p)  # started by the head script
    else:
      resp = window.fetch(f'_/theme/lang-{lang}.json?v={VERSION}')  # Anvil waits for JS promises
      if not getattr(resp, 'ok'):
        raise Exception(f"HTTP {getattr(resp, 'status')}")
      text = getattr(resp, 'text')()
    _pack = json.loads(text)
    if not window.get('AA_PACK'):
      window.AA_PACK = window.JSON.parse(text)  # the template translator (app-kit.js UI.tr) reads it there
  except Exception as e:
    print("Language pack failed to load, using English:", e)
    _pack = {}
    lang = 'en'


_load()


# ------------------------------------------------------------------ lookups

def _no_double_dot(template, kw):
  """'{date}.' with date '14 nov.' would end in '..': drop the template's dot."""
  for k, v in kw.items():
    if isinstance(v, str) and v.endswith('.') and ('{' + k + '}.') in template:
      template = template.replace('{' + k + '}.', '{' + k + '}')
  return template


def t(s, **kw):
  """Translate English text s. Keyword arguments fill {placeholders}."""
  r = _pack.get(s, s) if _pack else s
  if isinstance(r, list):
    r = r[-1]
  if kw:
    r = _no_double_dot(r, kw)
    try:
      return r.format(**kw)
    except Exception:
      return s.format(**kw)
  return r


def _form(n):
  """Index into a plural list for the current language."""
  n = abs(int(n))
  if lang == 'fr':
    return 0 if n <= 1 else 1
  if lang == 'ru':
    if n % 10 == 1 and n % 100 != 11:
      return 0
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
      return 1
    return 2
  if lang == 'lv':
    return 0 if (n % 10 == 1 and n % 100 != 11) else 1
  return 0 if n == 1 else 1


def tn(n, one, many, **kw):
  """Plural-aware translation. The pack stores a list of forms under the English singular:
  fr [one, many], ru [one, few, many], lv [one, other]."""
  kw['n'] = n
  forms = _pack.get(one) if _pack else None
  if isinstance(forms, list) and forms:
    r = forms[min(_form(n), len(forms) - 1)]
  elif isinstance(forms, str):
    r = forms
  else:
    r = one if n == 1 else many
  try:
    return r.format(**kw)
  except Exception:
    return (one if n == 1 else many).format(**kw)


# ------------------------------------------------------------------ dates & money

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def month(m):
  return t(MONTHS[m - 1])


def date_text(d, with_year):
  if with_year:
    return t('{month} {day}, {year}', month=month(d.month), day=d.day, year=d.year)
  return t('{month} {day}', month=month(d.month), day=d.day)


def money(n):
  """n: a whole number. '$2,400' in English, '2 400 $' elsewhere."""
  s = str(abs(n))
  parts = []
  while len(s) > 3:
    parts.insert(0, s[-3:])
    s = s[:-3]
  parts.insert(0, s)
  sign = '-' if n < 0 else ''
  if lang == 'en':
    return sign + '$' + ','.join(parts)
  return sign + ' '.join(parts) + ' $'


# ------------------------------------------------------------------ text stored by the server in English

# Status notes and some server messages are saved/sent in English; these patterns translate them for display.
# (regex, English key, placeholder names). A trailing ': comment' group, when present, is kept as typed.
_PATTERNS = [
  (r'^Request submitted by (.+) for (.+)$', 'Request submitted by {who} for {client}', ['who', 'client']),
  (r'^Request submitted by (.+)$', 'Request submitted by {who}', ['who']),
  (r'^Quote approved by (.+?)(: [\s\S]*)?$', 'Quote approved by {name}', ['name']),
  (r'^Delivery accepted by (.+?)(: [\s\S]*)?$', 'Delivery accepted by {name}', ['name']),
  (r'^Withdrawn by (.+?)(: [\s\S]*)?$', 'Withdrawn by {name}', ['name']),
  (r'^Demo data loaded: 3 clients and (\d+) requests\.$', 'Demo data loaded: 3 clients and {n} requests.', ['n']),
  (r'^Removed demo data \((\d+) requests\)\.$', 'Removed demo data ({n} requests).', ['n']),
]
_QUOTE = r'^Fixed quote: \$([\d,]+)(?: · ETA ([A-Z][a-z]{2}) (\d{1,2}))?$'


def server_text(msg):
  """Translate a message or note body that the server wrote in English."""
  if not msg or lang == 'en':
    return msg
  if msg in _pack:
    return t(msg)
  m = re.match(_QUOTE, msg)
  if m:
    out = t('Fixed quote: {amount}', amount=money(int(m.group(1).replace(',', ''))))
    if m.group(2) and m.group(2) in MONTHS:
      out += ' · ' + t('ETA {date}', date=t('{month} {day}', month=month(MONTHS.index(m.group(2)) + 1),
                                               day=int(m.group(3))))
    return out
  for pat, key, names in _PATTERNS:
    m = re.match(pat, msg)
    if m:
      g = m.groups()
      kw = {}
      for i, name in enumerate(names):
        kw[name] = g[i]
      rest = g[len(names)] if len(g) > len(names) else ''
      return t(key, **kw) + (rest or '')
  return msg


# ------------------------------------------------------------------ switching

def set_lang(code):
  """Save the choice and reload so every page is rebuilt in the new language."""
  if code not in CODES or code == lang:
    return
  try:
    if code == 'en':
      window.localStorage.removeItem(STORAGE_KEY)
    else:
      window.localStorage.setItem(STORAGE_KEY, code)
  except Exception:
    pass
  window.location.reload()


# ------------------------------------------------------------------ plain text + form templates

_ENTITIES = [('&nbsp;', chr(160)), ('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"'), ('&#39;', "'"), ('&amp;', '&')]


def plain(s):
  """HTML entities -> characters (a Button or Label shows its text as typed)."""
  for ent, ch in _ENTITIES:
    s = s.replace(ent, ch)
  return s


def tp(s, **kw):
  """t() for a Button, Label or placeholder: the key may be stored with &amp; (it came from HTML), the result is plain."""
  if _pack and s not in _pack and '&' in s:
    alt = s.replace('&', '&amp;')
    if alt in _pack:
      return plain(t(alt, **kw))
  return plain(t(s, **kw))


_PROPS = ('text', 'placeholder', 'tooltip')


def _components(form):
  """The components a form's template declares. A templated form isn't a container (no get_components()): its
  components are attributes named after them (self.save_button ...), so look through those."""
  from anvil import Component
  try:
    names = list(form.__dict__.keys())
  except Exception:  # the browser's Python may not offer it: dir() below
    names = []
  out = [getattr(form, n, None) for n in names if not n.startswith('_')]
  out = [c for c in out if isinstance(c, Component)]
  if not out:
    for n in dir(form):
      if n.startswith('_') or n in ('item', 'parent', 'layout', 'dom_nodes'):
        continue
      try:
        c = getattr(form, n, None)
      except Exception:
        continue
      if isinstance(c, Component):
        out.append(c)
  return out


def _props(form):
  from anvil import Button, Label, Link, CheckBox, TextBox, TextArea
  for c in _components(form):
    if not isinstance(c, (Button, Label, Link, CheckBox, TextBox, TextArea)):
      continue
    for name in _PROPS:
      if name == 'text' and isinstance(c, (TextBox, TextArea)):
        continue  # that's what the person typed
      v = getattr(c, name, None)
      if isinstance(v, str) and v.strip():
        setattr(c, name, tp(v))


def apply(form, **vars):
  """Translate a form's template text (data-t / data-ta elements) and its components' text, then fill {vars}."""
  window.UI.tr(anvil.js.get_dom_node(form), vars)
  if _pack:
    _props(form)
