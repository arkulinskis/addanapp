"""Email translations. Each user's language is saved on their row (users.lang) when they open the app,
and notification emails are written in that language. English is the source text.

The texts live in email_text.py (EMAIL_TEXT = {lang: {english: translation}}).
"""
from .email_text import EMAIL_TEXT

LANGS = ('en', 'fr', 'ru', 'lv')
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def user_lang(u):
  try:
    v = u['lang']
  except Exception:  # column not created yet (schema not applied)
    return 'en'
  return v if v in LANGS else 'en'


def set_user_lang(u, lang):
  if lang not in LANGS:
    return
  try:
    if u['lang'] != lang:
      u['lang'] = lang
  except Exception:
    pass


class Tr(object):
  """tr('English {x}', x=1) in one language, plus localized money and dates."""

  def __init__(self, lang='en'):
    self.lang = lang if lang in LANGS else 'en'
    self.table = EMAIL_TEXT.get(self.lang, {})

  def __call__(self, s, **kw):
    r = self.table.get(s, s)
    if kw:
      for k, v in kw.items():  # '{date}.' with date '14 nov.' would end in '..'
        if isinstance(v, str) and v.endswith('.') and ('{' + k + '}.') in r:
          r = r.replace('{' + k + '}.', '{' + k + '}')
      try:
        return r.format(**kw)
      except Exception:
        return s.format(**kw)
    return r

  def money(self, v):
    if v is None:
      return '—'
    n = int(round(float(v)))
    if self.lang == 'en':
      return '${:,}'.format(n)
    return '{:,}'.format(n).replace(',', ' ') + ' $'

  def date(self, d, year=True):
    if d is None:
      return ''
    month = self(MONTHS[d.month - 1])
    if year:
      return self('{month} {day}, {year}', month=month, day=d.day, year=d.year)
    return self('{month} {day}', month=month, day=d.day)
