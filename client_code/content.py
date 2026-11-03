"""Landing page markup. Buttons use data-act (handled in the Landing form).
Everything a search engine should read lives here, on the indexable home page.
Visible text goes through t() so it can be shown in French, Russian or Latvian (see i18n.py)."""
from .icons import icon
from .i18n import t
from . import i18n, portfolio

# Blank until the official address is ready; every spot that shows it hides itself while empty.
CONTACT_EMAIL = ''

# The Addanapp YouTube channel and the film about Addanapp itself, one per language (APP_MAKER/youtube/manifest.json:
# addanapp, addanapp-fr/ru/lv). Visitors get the film in their language, with links to the others.
# The film is a click-to-play embed: nothing loads from YouTube until the visitor presses play (Landing._play).
YT_CHANNEL = 'https://www.youtube.com/@addanapp'
YT_FILMS = {  # lang: (video id, length, cover in theme/assets)
  'en': ('wzCMxAdyrHo', '1:06', 'yt-addanapp.jpg'),
  'fr': ('MKOIck45xWQ', '1:19', 'yt-addanapp-fr.jpg'),
  'ru': ('awzVxnVHrco', '1:24', 'yt-addanapp-ru-2.jpg'),
  'lv': ('yzDUcUaH2q0', '1:24', 'yt-addanapp-lv.jpg'),
}
YT_FILM, YT_FILM_LENGTH, YT_COVER = YT_FILMS.get(i18n.lang, YT_FILMS['en'])
# A second film shows another kind of work: Parapeet, a live 2023 app we rebuilt (before/after, English only).
# Its card plays it in the same frame (Landing._play).
YT_REBUILD, YT_REBUILD_LENGTH, YT_REBUILD_COVER = 'FW-j_xL_DWo', '1:29', 'yt-parapeet.jpg'
YT_LOGO = ('<svg class="yt-logo" viewBox="0 0 28 20" width="22" height="16" aria-hidden="true"><rect width="28" height="20" rx="5" fill="#FF0033"/>'
           '<path d="M11.2 5.8v8.4l7.3-4.2z" fill="#fff"/></svg>')
YT_PLAY = ('<svg viewBox="0 0 68 48" width="68" height="48"><path d="M66.5 7.7a8.5 8.5 0 0 0-6-6C55.3.3 34 .3 34 .3s-21.3 0-26.5 1.4a8.5 8.5 0 0 0-6 6'
           'C.1 13 .1 24 .1 24s0 11 1.4 16.3a8.5 8.5 0 0 0 6 6c5.2 1.4 26.5 1.4 26.5 1.4s21.3 0 26.5-1.4a8.5 8.5 0 0 0 6-6'
           'C67.9 35 67.9 24 67.9 24s0-11-1.4-16.3z" fill="#FF0033"/><path d="M45 24 27 14v20z" fill="#fff"/></svg>')

# The partner deck, one PDF per language (rendered by .claude/skills/addanapp/scripts/deck_pdf.py from the
# "Addanapp Partner Deck" Slides artifact; its firms slide names firms only as examples).
# The visitor's language is the main download; the other three are linked under it.
DECKS = {  # lang: (pdf, cover, size)
  'en': ('addanapp-partner-deck.pdf', 'partner-deck-cover.jpg', '3 MB'),
  'fr': ('addanapp-partner-deck-fr.pdf', 'partner-deck-cover-fr.jpg', '3 MB'),
  'ru': ('addanapp-partner-deck-ru.pdf', 'partner-deck-cover-ru.jpg', '3 MB'),
  'lv': ('addanapp-partner-deck-lv.pdf', 'partner-deck-cover-lv.jpg', '3 MB'),
}
DECK_SLIDES = 20
DECK_LANG = i18n.lang if i18n.lang in DECKS else 'en'
DECK_URL = '_/theme/' + DECKS[DECK_LANG][0]
DECK_COVER = '_/theme/' + DECKS[DECK_LANG][1]


def deck_attrs(code=None):
  """href + download attributes for the partner deck in one language (default: the visitor's)."""
  code = code if code in DECKS else DECK_LANG
  name = 'Addanapp-partner-deck' + ('' if code == 'en' else '-' + code.upper()) + '.pdf'
  return f'href="_/theme/{DECKS[code][0]}" target="_blank" rel="noopener" download="{name}" hreflang="{code}"'


# Free guides (lead magnets, made in Documents/CLAUDE/addanapp-guides). PDFs and covers live in theme/assets/guides/.
# The #guides page asks for an email before showing the download links (api_public.request_guides).
# (slug, number, title, hook, what's inside, pages)
GUIDES = [
  ('spreadsheet-escape-plan', '01', 'Your Spreadsheet Is Already an App',
   'Is your business running on a spreadsheet only one person understands?',
   ['The 10-sign test', 'A calculator for what "it works fine" really costs', 'A five-move plan to graduate safely'], 10),
  ('one-page-app-brief', '02', 'The One-Page App Brief',
   'Got an app idea but no idea what it should cost?',
   ['The 7 boxes of a good brief', 'A fill-in template and a worked example', '12 questions to ask any developer'], 10),
  ('ai-built-human-signed', '03', 'AI-Built, Human-Signed',
   'Your next developer will use AI. Who checks the code?',
   ['What AI is great at, and where it trips', 'The 10-point sign-off checklist', 'Green flags and red flags'], 9),
  ('build-buy-or-bolt-on', '04', 'Build, Buy or Bolt On',
   'Paying for six tools to do one job?',
   ['An 8-question decision test', 'A 3-year cost worksheet', 'Five small add-ons that pay off fast'], 9),
  ('law-25-app-checklist', '05', 'Law 25 for Your Next App',
   'Collecting names and emails in Québec? Read this first.',
   ['A 15-point privacy checklist', 'Requirements to paste into your developer brief', 'Bonus: email lists and CASL'], 9),
]
GUIDE_SLUGS = [g[0] for g in GUIDES]
# Same English labels as api_public.GUIDE_SITUATIONS; the last two count as buying signals there.
GUIDE_SITUATIONS = ['We run on spreadsheets', 'We pay for too many tools', 'Just curious', 'I have an app idea',
                    "We're building something now"]


def guide_cover(slug):
  return f'_/theme/guides/{slug}.jpg'


def other_languages(link):
  """'Other languages: English · Русский · Latviešu', each language's link made by link(code)."""
  others = [c for c in i18n.CODES if c != i18n.lang]
  return (f'<span class="lbl">{t("Other languages:")}</span> '
          + ' <span class="sep" aria-hidden="true">·</span> '.join(link(c) for c in others))


def _deck_lang_link(code):
  return f'<a {deck_attrs(code)} lang="{code}">{i18n.NAMES[code]}</a>'


def _film_lang_link(code):
  return (f'<a href="https://www.youtube.com/watch?v={YT_FILMS[code][0]}" target="_blank" rel="noopener" '
          f'hreflang="{code}" lang="{code}">{i18n.NAMES[code]}</a>')


def _ev(cls, ico, title, text, when):
  return (f'<div class="ev"><div class="ic {cls}">{icon(ico)}</div>'
          f'<div class="t"><b>{title}</b>{text} <span class="when">· {when}</span></div></div>')


# rolling cover: the line above the headline rolls through what we build; the request in the mock changes with it (12 s loop)
_ROLL = [t('web apps.'), t('client portals.'), t('admin panels.'), t('data platforms.')]
ROLL = ''.join(f'<span>{w}</span>' for w in _ROLL + _ROLL[:1])
_REQS = ''.join(
  f'<div class="req"><span class="chip mono">{k}</span> <span class="chip outline">{c}</span><h4>{h}</h4></div>'
  for k, c, h in [('AA-1042', t('Integration / API'), t('Deposits for large-party reservations')),
                  ('AA-1057', t('Client portal'), t('Invoice history in the client portal')),
                  ('AA-1063', t('Admin panel'), t('Refund approvals for the support team')),
                  ('AA-1071', t('Data platform'), t('Live sales dashboard for 12 stores'))])

HERO_MOCK = f'''
<div class="lp-mock rv d2" role="img" aria-label="{t('Example: a feature request tracked in the Addanapp client workspace, from fixed quote to AI draft, human validation and client review.')}">
  <div class="win">
    <div class="bar"><i></i><i></i><i></i><span class="url">addanapp.com · workspace</span></div>
    <div class="body">
      <div class="top">
        <div class="lp-reqs">{_REQS}</div>
        <span class="chip ai"><span class="d"></span>{t('In progress')}</span>
      </div>
      <div class="progress"><i style="width:72%"></i></div>
      <div class="meta"><span>{t('Fixed quote approved · ETA Nov 14')}</span><b style="color:var(--ink)">72%</b></div>
      <div class="tl">
        {_ev('slate', 'check', t('Scoped &amp; quoted'), t('6 acceptance criteria, fixed price approved.'), t('Oct 21'))}
        {_ev('ai', 'sparkle', t('AI draft generated'), t('Stripe flow, webhooks and 38 tests drafted.'), t('Oct 22'))}
        {_ev('human', 'shield', t('Human-validated'), t('Engineer review: 2 edge cases fixed, security checks passed.'), t('Oct 23'))}
        {_ev('accent', 'eye', t('Ready for your review'), t('Try it on staging, then accept or request changes.'), t('Today'))}
      </div>
      <div class="cta-row"><span></span>
        <span style="display:flex;gap:6px"><span class="aa-btn sm ghost" style="pointer-events:none">{t('Request changes')}</span><span class="aa-btn sm green" style="pointer-events:none">{t('Accept delivery')}</span></span></div>
    </div>
  </div>
  <div class="stamp"><div class="seal">{icon('shield')}</div><div><b>{t('100% human-reviewed')}</b>{t('Every AI draft is signed off by a senior engineer.')}</div></div>
</div>'''


def _proof():
  items = ''
  for p in portfolio.PROJECTS:
    items += f'<a href="{portfolio.url(p)}" target="_blank" rel="noopener"><i style="background:{p["color"]}"></i>{p["name"]}</a>'
  dup = items.replace('<a ', '<a aria-hidden="true" tabindex="-1" ')
  return '<div class="track">' + items + dup + '</div>'


def _cmp(ico, title, text):
  return f'<li>{icon(ico)}<span><b>{t(title)}</b>{t(text)}</span></li>'


COMPARE = f'''
<div class="lp-compare rv">
  <div class="col them">
    <h3><span class="chip outline">{t('The usual agency')}</span></h3>
    <ul>
      {_cmp('minus-circle', 'Billed by the hour', 'Estimates drift and the meter keeps running.')}
      {_cmp('minus-circle', 'Status when you chase it', "Updates live in someone's inbox, not in front of you.")}
      {_cmp('minus-circle', 'Opaque staffing', 'You meet a senior in the pitch and juniors on the project.')}
      {_cmp('minus-circle', 'AI used quietly, or not at all', 'Either slower than it should be, or unreviewed code reaches production.')}
      {_cmp('minus-circle', 'Invoice first, questions later', 'You pay for effort, whether or not it worked.')}
    </ul>
  </div>
  <div class="col us">
    <h3><span class="chip ink">Addanapp</span></h3>
    <ul>
      {_cmp('check-circle', 'A fixed quote for every request', 'Scope, price and ETA are agreed before any work starts.')}
      {_cmp('check-circle', 'A live client workspace', 'Every request has a status, a progress bar and notes written by your engineer.')}
      {_cmp('check-circle', 'One senior engineer, accountable end to end', 'The person who scopes your request is the person who signs it off.')}
      {_cmp('check-circle', 'AI in the open, humans in charge', 'AI speeds up the build. Every output is reviewed, tested and approved by a person.')}
      {_cmp('check-circle', 'You pay for accepted results', 'Test it on staging. Accept it, and only then are you invoiced.')}
    </ul>
  </div>
</div>'''


def _step(n, ico, who_cls, who, title, text, hl=False, d=0):
  return f'''<div class="lp-step rv d{d}{' hl' if hl else ''}">
    <div class="num"><span>{n}</span><span class="who {who_cls}">{t(who)}</span></div>
    <div class="ico">{icon(ico)}</div><h3>{t(title)}</h3><p>{t(text)}</p></div>'''


STEPS = ''.join([
  _step('01', 'message', 'c', 'You', 'Brief', 'Describe the outcome you need in your workspace, in plain language. Screenshots and links welcome.', d=0),
  _step('02', 'target', 'h', 'Human', 'Scope &amp; fixed quote', 'An engineer writes acceptance criteria, flags risks and sends a fixed price with an ETA. Nothing starts until you approve.', d=1),
  _step('03', 'sparkle', 'a', 'AI + engineer', 'Accelerated build', 'AI agents draft code, tests, migrations and docs under an engineer\'s direction. Days, not months.', d=2),
  _step('04', 'shield', 'h', 'Human', 'Validation', 'Line-by-line review, security and privacy checks, and tests against your acceptance criteria on real devices.', d=3),
  _step('05', 'badge', 'c', 'You', 'Accept, then pay', 'Try it on staging. Accept it, or ask for changes within scope at no extra cost. Then you\'re invoiced.', hl=True, d=4),
])


def _svc(ico, title, text, tags, d=0):
  tg = ''.join(f'<span>{t(x)}</span>' for x in tags)
  return f'<div class="s rv d{d}"><div class="ico">{icon(ico)}</div><h3>{t(title)}</h3><p>{t(text)}</p><div class="tags">{tg}</div></div>'


SERVICES = ''.join([
  _svc('layout', 'Admin panels &amp; back-offices', 'Role-based access, audit trails, bulk actions, approvals and exports. The control room your team actually wants to use.', ['RBAC', 'Audit log', 'CSV / PDF'], 0),
  _svc('users', 'Client &amp; partner portals', 'Self-service spaces with secure logins, permissions, notifications and the documents your customers keep asking for.', ['Auth', 'Notifications', 'Self-serve'], 1),
  _svc('plug', 'APIs &amp; integrations', 'REST APIs, webhooks and clean connections to Stripe, Google, QuickBooks, CRMs and whatever else you already run.', ['REST', 'Webhooks', 'Stripe'], 2),
  _svc('database', 'High-throughput data', 'Ingestion pipelines, scheduled jobs, search and reporting dashboards that stay fast as your data grows.', ['ETL', 'Dashboards', 'Search'], 0),
  _svc('sliders', 'Configurable SaaS', 'Multi-tenant products with per-customer settings, feature flags, white-labelling and usage-based billing.', ['Multi-tenant', 'Flags', 'Billing'], 1),
  _svc('phone', 'Mobile-first web apps', 'Installable apps that feel native: offline mode, voice, camera, sensors and push notifications, with no app store required.', ['PWA', 'Offline', 'Voice'], 2),
  _svc('bot', 'AI features, done responsibly', 'Assistants, document extraction, classification and smart search, with human-in-the-loop review where it matters.', ['LLMs', 'RAG', 'Review queues'], 0),
  _svc('game', 'Games &amp; engagement', 'Progress systems, collections, streaks, leaderboards and level editors that turn routine into habit.', ['Gamification', 'Level editors', 'Canvas'], 1),
  _svc('globe', 'Websites with substance', 'Fast, search-friendly marketing sites wired into real systems such as bookings, content APIs and lead pipelines.', ['SEO', 'Bookings', 'CMS'], 2),
])


def _pt(ico, title, text):
  return f'<li><span class="i">{icon(ico)}</span><div><b>{t(title)}</b><span>{t(text)}</span></div></li>'


WS_CLIENT = f'''
<div class="mini-app">
  <div class="hd"><b>{t('Bistro Laurier · Workspace')}</b><span class="aa-btn sm" style="pointer-events:none">{icon('plus', 'width="14" height="14"')} {t('New request')}</span></div>
  <div class="tiles">
    <div class="tile"><div class="v">3</div><div class="l">{t('Open')}</div></div>
    <div class="tile" style="background:var(--accent-soft);border-color:#CBD6FF"><div class="v" style="color:var(--accent-d)">1</div><div class="l">{t('Needs you')}</div></div>
    <div class="tile"><div class="v">2</div><div class="l">{t('In progress')}</div></div>
    <div class="tile"><div class="v">14</div><div class="l">{t('Delivered')}</div></div>
  </div>
  <div class="rows">
    <div class="row"><span class="ref">AA-1042</span><div><div class="ttl">{t('Deposits for large parties')}</div><div class="progress"><i style="width:72%"></i></div></div><span class="chip ai"><span class="d"></span>{t('In progress')}</span></div>
    <div class="row"><span class="ref">AA-1047</span><div><div class="ttl">{t('Gift card balance page')}</div><div class="sub">{t('Fixed quote $2,400 · ETA 6 days')}</div></div><span class="chip accent"><span class="d"></span>{t('Quote ready')}</span></div>
    <div class="row"><span class="ref">AA-1039</span><div><div class="ttl">{t('Weekly covers report (PDF)')}</div><div class="progress done"><i style="width:100%"></i></div></div><span class="chip human"><span class="d"></span>{t('Delivered')}</span></div>
  </div>
</div>'''

WS_ADMIN = f'''
<div class="mini-app">
  <div class="hd"><b>{t('Consultant console · Board')}</b><span class="chip accent">{t('4 unread')}</span></div>
  <div class="cols">
    <div class="colk"><h5>{t('Scoping')} <span>2</span></h5>
      <div class="kc"><b>{t('SSO with Google Workspace')}</b><span class="small muted">Northline Logistics</span></div>
      <div class="kc"><b>{t('Inventory CSV import')}</b><span class="small muted">Atelier Rossi</span></div></div>
    <div class="colk"><h5>{t('In progress')} <span>3</span></h5>
      <div class="kc"><b>{t('Deposits for large parties')}</b><div class="progress"><i style="width:72%"></i></div></div>
      <div class="kc"><b>{t('Driver mobile check-in')}</b><div class="progress"><i style="width:40%"></i></div></div></div>
    <div class="colk"><h5>{t('Review')} <span>1</span></h5>
      <div class="kc"><b>{t('Route optimisation v2')}</b><span class="chip human" style="margin-top:6px">{t('Validated')}</span></div></div>
  </div>
  <div class="note-box"><div class="ph">{t('Write a progress note for the client…')}</div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;justify-content:space-between;align-items:center">
      <span style="display:flex;gap:6px;flex-wrap:wrap"><span class="chip accent">{t('Progress update')}</span><span class="chip human">{icon('shield', 'width="12" height="12"')}{t('Human-validated')}</span></span>
      <span class="aa-btn sm" style="pointer-events:none">{t('Post note')}</span></div></div>
</div>'''


def _eng(kind, title, price, text, items, cta, act, feat=False, badge=''):
  li = ''.join(f'<li>{icon("check")}<span>{t(x)}</span></li>' for x in items)
  btn = 'light' if feat else 'ghost'
  b = f'<span class="badge chip accent">{t(badge)}</span>' if badge else ''
  return f'''<div class="e rv{' feat' if feat else ''}">{b}<div class="k">{t(kind)}</div><h3>{t(title)}</h3>
    <div class="price">{t(price)}</div><p>{t(text)}</p><ul>{li}</ul>
    <button type="button" class="aa-btn {btn} block" data-act="{act}">{t(cta)} <span class="arr">&rarr;</span></button></div>'''


ENGAGEMENTS = ''.join([
  _eng('For existing products', 'Single feature', 'Fixed quote per request',
       'Add capability to the app you already run, whether we built it or not.',
       ['Fixed quote within 2 business days', 'Scope, price and ETA agreed upfront', 'Code review and tests included',
        'Invoiced only when you accept'], 'Request a feature', 'signup'),
  _eng('From idea to launch', 'New product', 'Milestones, each at a fixed price',
       'A complete web or mobile-first app, admin panel included, delivered in milestones you accept one at a time.',
       ['Discovery workshop and clickable prototype', 'Milestones you accept one by one', 'Hosting, monitoring and backups',
        'Documentation and a full handover'], 'Plan a product', 'contact', feat=True, badge='Most requested'),
  _eng('Ongoing', 'Product partner', 'Reserved monthly capacity',
       'A senior engineer for your roadmap, with AI leverage behind them and your request queue always moving.',
       ['Priority request queue', 'Monthly roadmap review', 'Fix-first response on production issues',
        'Pause or stop any month'], 'Talk to us', 'contact'),
])


def _commit(ico, title, text):
  return f'<div class="c rv">{icon(ico)}<b>{t(title)}</b><span>{t(text)}</span></div>'


COMMITMENTS = ''.join([
  _commit('key', 'You own everything', 'Code, data and accounts are yours from day one. No lock-in.'),
  _commit('receipt', 'No acceptance, no invoice', 'You pay for results you have tested and approved.'),
  _commit('shield', 'Human-validated', 'No AI output ships without an engineer\'s sign-off.'),
  _commit('lock', 'Privacy by design', 'Built with Québec\'s Law 25 and PIPEDA in mind. Canadian hosting on request.'),
  _commit('lang', 'English &amp; français', 'Bilingual service from a Montréal-based team.'),
])

FAQ = [
  ("How exactly do you use AI?",
   "AI tools help us draft code, tests, data migrations and documentation, and explore alternatives quickly. An engineer "
   "directs that work, reviews every change line by line, runs the tests and checks security before anything reaches you. "
   "AI makes us faster. It never makes the decisions."),
  ("What does “you pay for results” mean?",
   "Each request gets a fixed price before work starts. When it's ready, you test it on a staging version. If it meets the "
   "acceptance criteria you agreed to, you accept it and we invoice. If not, we fix it at no extra cost. There are no timesheets."),
  ("What kinds of apps can you build?",
   "Business software with real operational weight: admin panels and back-offices, client portals, configurable SaaS, APIs and "
   "integrations, data pipelines and reporting, mobile-first web apps, and even games. If it needs logins, roles, data and an "
   "admin side, it's our specialty."),
  ("Do I own the code?",
   "Yes. You own the code, the data and the accounts from day one. We can host and maintain the app for you, or hand everything "
   "over to your team or your infrastructure."),
  ("How fast can you deliver?",
   "Most feature requests get a fixed quote within two business days and ship within one to three weeks. New products are planned "
   "in milestones, and the first usable version typically lands in four to eight weeks."),
  ("Can you take over an existing app?",
   "Often, yes. We start with a short, fixed-price audit of the codebase, document the risks, then quote improvements request by "
   "request, like any other work.", 'rebuild'),
  ("Do you only work with Montréal companies?",
   "No. We're based in Montréal and happy to meet in person locally, but we work with clients across Canada, the United States and "
   "Europe. Service is available in English and French."),
  ("Is my data safe?",
   "Workspaces are private, connections are encrypted and access follows least privilege. Apps are built with Québec's Law 25 and "
   "PIPEDA in mind, and we can host in Canada when required."),
  ("What technology do you use?",
   "Mostly full-stack Python with modern web front ends, managed databases and cloud hosting, plus JavaScript where the browser "
   "demands it (audio, MIDI, maps, offline). We choose proven technology for the parts that must not break."),
]


def _faq_rebuild():
  """Example under "Can you take over an existing app?": the Parapeet rebuild film (opens YouTube)."""
  link = (f'<a href="https://www.youtube.com/watch?v={YT_REBUILD}" target="_blank" rel="noopener">'
          f'{t("Parapeet’s before-and-after film")} <span class="arr">&#8599;</span></a>')
  return t('For an example, watch {link}: a live app from 2023 that we rebuilt from scratch.', link=link)


FAQ_EXTRA = {'rebuild': _faq_rebuild}  # optional third item of a FAQ entry: one more paragraph under the answer


def _faq():
  out = ''
  for item in FAQ:
    qn, ans = item[0], item[1]
    extra = f'<p>{FAQ_EXTRA[item[2]]()}</p>' if len(item) > 2 else ''
    out += f'<details class="rv"><summary>{t(qn)}</summary><p>{t(ans)}</p>{extra}</details>'
  return out


# Lead form choices are saved in English (the value) and shown translated (the label).
LEAD_TYPES = ['A new app or product', 'A feature for an existing app', 'An admin panel or internal tool', 'A client portal',
              'API or integration work', 'Taking over an existing app', 'Something else']
LEAD_BUDGETS = ['Not sure yet', 'Under $10k', '$10k – $25k', '$25k – $75k', '$75k+']


def _opts(items):
  return ''.join(f'<option value="{x}">{t(x)}</option>' for x in items)


LEAD_FORM = f'''
<div class="lp-form rv d1" id="lead-form">
  <div class="form-body">
    <h3 style="font-size:1.3rem;margin-bottom:4px">{t('Send a project brief')}</h3>
    <p class="small muted" style="margin-bottom:20px">{t('Takes two minutes. An engineer replies within two business days.')}</p>
    <div class="aa-error hidden"></div>
    <div class="row2">
      <div class="f"><label for="ld-name">{t('Name')}</label><input id="ld-name" type="text" name="name" autocomplete="name" placeholder="{t('Jane Tremblay')}"></div>
      <div class="f"><label for="ld-email">{t('Work email')}</label><input id="ld-email" type="email" name="email" autocomplete="email" placeholder="{t('jane@company.com')}"></div>
    </div>
    <div class="row2">
      <div class="f"><label for="ld-company">{t('Company')} <span class="opt">{t('(optional)')}</span></label><input id="ld-company" type="text" name="company" autocomplete="organization" placeholder="{t('Company Inc.')}"></div>
      <div class="f"><label for="ld-budget">{t('Budget')}</label><select id="ld-budget" name="budget">{_opts(LEAD_BUDGETS)}</select></div>
    </div>
    <div class="f"><label for="ld-kind">{t('What do you need?')}</label><select id="ld-kind" name="kind">{_opts(LEAD_TYPES)}</select></div>
    <div class="f"><label for="ld-msg">{t("The outcome you're after")}</label><textarea id="ld-msg" name="message" rows="4" placeholder="{t('e.g. Our team tracks 400 orders a week in spreadsheets. We want a dashboard with roles, approvals and a weekly PDF report.')}"></textarea></div>
    <input class="hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
    <label class="check" style="margin-bottom:18px"><input type="checkbox" name="consent"><span>{t('I agree that Addanapp may contact me about this request. See our <a href="javascript:void(0)" data-lk-open="privacy">privacy policy</a>.')}</span></label>
    <button type="button" class="aa-btn accent block lg" data-act="lead">{t('Send brief')} <span class="arr">&rarr;</span></button>
    <p class="tiny muted center" style="margin:14px 0 0">{t('Prefer the full experience?')} <button type="button" class="aa-link" data-act="signup">{t('Create a client workspace')}</button></p>
  </div>
  <div class="ok hidden">
    <div class="seal">{icon('check')}</div>
    <h3 style="font-size:1.4rem">{t('Brief received. Thank you.')}</h3>
    <p class="muted">{t('An engineer will reply within two business days. In the meantime, you can create a workspace and submit the request in full.')}</p>
    <button type="button" class="aa-btn" data-act="signup">{t('Create a workspace')} <span class="arr">&rarr;</span></button>
  </div>
</div>'''


FAQ_CONTACT = ('<p class="muted">' + t('Anything else? Write to {email} and an engineer will answer.',
                 email='<a href="mailto:' + CONTACT_EMAIL + '">' + CONTACT_EMAIL + '</a>') + '</p>'
               if CONTACT_EMAIL else '')
EMAIL_WAY = (f'<div class="way"><span class="i">{icon("mail")}</span><div><b>{t("Email")}</b>'
             f'<a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></div></div>' if CONTACT_EMAIL else '')

HTML = f'''
<div class="lp">

<!-- ============================================================ hero -->
<section class="lp-hero" id="top" data-ch="" aria-labelledby="hero-title">
  <div class="aa-wrap grid">
    <div>
      <div class="tag-loc rv"><b>Montréal</b>{t('Custom software studio · EN / FR')}</div>
      <div class="lp-we rv d1">{t('We build')} <span class="lp-roll" aria-hidden="true">{ROLL}</span></div>
      <h1 id="hero-title" class="rv d1">{t('Apps built at AI speed. <em>Signed off by senior engineers.</em>')}</h1>
      <p class="sub rv d2">{t('Addanapp designs and builds <b>web apps, admin panels, client portals and data-heavy platforms</b>. AI accelerates every step, and an engineer reviews, tests and approves every line before it reaches you. <b>You pay for accepted results, not hours.</b>')}</p>
      <div class="ctas rv d3">
        <button type="button" class="aa-btn accent lg" data-act="contact">{t('Start a project')} <span class="arr">&rarr;</span></button>
        <a class="aa-btn ghost-light lg" href="#home/work">{t("See work we've shipped")}</a>
      </div>
      <div class="assure rv d4">
        <span>{icon('check')}{t('Fixed quote before work starts')}</span>
        <span>{icon('check')}{t('Track every request live')}</span>
        <span>{icon('check')}{t('You own 100% of the code')}</span>
      </div>
    </div>
    {HERO_MOCK}
  </div>
  <div class="lp-proof">
    <div class="aa-wrap pin">
      <span class="lbl">{t('Built &amp; running')}</span>
      <div class="marquee">{_proof()}</div>
    </div>
  </div>
</section>

<!-- ============================================================ why -->
<section class="lp-sec" id="approach" data-ch="approach" aria-labelledby="why-title">
  <div class="aa-wrap">
    <div class="lp-head rv">
      <div class="eyebrow">{t('Why Addanapp')}</div>
      <h2 id="why-title">{t('Most consultancies sell hours. <em>We sell outcomes.</em>')}</h2>
      <p class="lead">{t("Hourly billing rewards slow work. We quote every request at a fixed price, build it with AI-accelerated tooling and have a senior engineer validate everything before it ships. If you don't accept it, you don't pay for it.")}</p>
    </div>
    {COMPARE}
  </div>
</section>

<!-- ============================================================ method -->
<section class="lp-sec on-dark" id="method" data-ch="approach" aria-labelledby="method-title">
  <div class="aa-wrap">
    <div class="lp-head rv">
      <div class="eyebrow">{t('The method')}</div>
      <h2 id="method-title">{t('AI does the heavy lifting. <em>A human signs every step.</em>')}</h2>
      <p class="lead">{t("AI lets us explore, draft and test at a pace traditional teams can't match. Speed without judgment is a liability, though, so every artifact passes through an engineer who is accountable for it.")}</p>
    </div>
    <div class="lp-steps">{STEPS}</div>
    <div class="lp-stats">
      <div class="lp-stat rv"><div class="v">2<small>{t('days')}</small></div><div class="l">{t('to a fixed quote on most requests')}</div></div>
      <div class="lp-stat rv d1"><div class="v">100<small>%</small></div><div class="l">{t('of AI-generated code reviewed by a senior engineer')}</div></div>
      <div class="lp-stat rv d2"><div class="v">0<small>{t('hours')}</small></div><div class="l">{t('billed. You pay per accepted result')}</div></div>
      <div class="lp-stat rv d3"><div class="v">EN<small>/</small>FR</div><div class="l">{t('bilingual service from Montréal')}</div></div>
    </div>
  </div>
</section>

<!-- ============================================================ services -->
<section class="lp-sec" id="services" data-ch="services" aria-labelledby="svc-title">
  <div class="aa-wrap">
    <div class="lp-head rv">
      <div class="eyebrow">{t('Capabilities')}</div>
      <h2 id="svc-title">{t('If it runs your business, <em>we can build it.</em>')}</h2>
      <p class="lead">{t('From a single feature to a full platform. We specialise in software with real operational weight: admin panels, deep configurability and high data throughput.')}</p>
    </div>
    <div class="lp-svc">{SERVICES}</div>
  </div>
</section>

<!-- ============================================================ work -->
<section class="lp-sec lp-alt" id="work" data-ch="work" aria-labelledby="work-title">
  <div class="aa-wrap">
    <div class="lp-head rv">
      <div class="eyebrow">{t('Selected work')}</div>
      <h2 id="work-title">{t('Shipped, live and <em>in daily use.</em>')}</h2>
      <p class="lead">{t('Three of our {n} products, picked at random each time you open this page. Every one is live, so click through and try it.', n=len(portfolio.PROJECTS))}</p>
    </div>
    {portfolio.showcase(portfolio.picks(3))}
    <div class="pf-more">
      <a class="aa-btn lg" href="#work">{t('See all {n} products in depth', n=len(portfolio.PROJECTS))} <span class="arr">&rarr;</span></a>
      <button type="button" class="aa-btn ghost lg" data-act="shuffle" title="{t('Show three other products')}">{icon('refresh', 'width="18" height="18"')} {t('Shuffle')}</button>
    </div>
  </div>
</section>

<!-- ============================================================ youtube -->
<section class="lp-sec on-dark lp-yt" id="youtube" data-ch="work" aria-labelledby="yt-title">
  <div class="aa-wrap yt-grid">
    <div class="rv">
      <div class="eyebrow">{YT_LOGO}{t('On YouTube')}</div>
      <h2 id="yt-title">{t('Every product, <em>in about a minute.</em>')}</h2>
      <p class="lead">{t("Our new YouTube channel, Addanapp, has a short film for almost every app we've built: what it does, who it's for and how it works in real use. Start with the one about us.")}</p>
      <div class="ctas">
        <a class="aa-btn accent" href="{YT_CHANNEL}?sub_confirmation=1" target="_blank" rel="noopener">{t('Subscribe on YouTube')} <span class="arr">&#8599;</span></a>
        <a class="aa-btn ghost-light" href="{YT_CHANNEL}" target="_blank" rel="noopener">{t('Visit the channel')}</a>
      </div>
      <p class="yt-handle">youtube.com/@addanapp</p>
    </div>
    <div class="yt-player rv d2">
      <div class="yt-frame">
        <button type="button" class="yt-cover" data-act="video" aria-label="{t('Play the Addanapp film')}">
          <img src="_/theme/{YT_COVER}" alt="" loading="lazy" decoding="async" width="960" height="540">
          <span class="yt-play" aria-hidden="true">{YT_PLAY}</span>
          <span class="yt-len">{YT_FILM_LENGTH}</span>
        </button>
      </div>
      <p class="yt-note">{t('The video loads from YouTube when you press play.')}</p>
      <p class="aa-langs">{other_languages(_film_lang_link)}</p>
      <button type="button" class="yt-more" data-act="video" data-arg="{YT_REBUILD}" aria-label="{t('Play the Parapeet before-and-after film')}">
        <span class="yt-thumb"><img src="_/theme/{YT_REBUILD_COVER}" alt="" loading="lazy" decoding="async" width="320" height="180"><span class="yt-len">{YT_REBUILD_LENGTH}</span></span>
        <span class="yt-more-t"><span class="k">{t('Not only new apps')}</span><b>{t('Parapeet, before and after')}</b>{t('A live app from 2023, rebuilt from scratch with every player and their progress kept. The film shows the old version next to the new one.')}</span>
      </button>
    </div>
  </div>
</section>

<!-- ============================================================ workspace -->
<section class="lp-sec" id="workspace" data-ch="workspace" aria-labelledby="ws-title">
  <div class="aa-wrap lp-ws">
    <div class="rv">
      <div class="eyebrow">{t('Client workspace')}</div>
      <h2 id="ws-title">{t('Your own space. <em>Every request, visible.</em>')}</h2>
      <p class="lead muted" style="font-size:1.1rem">{t('No more chasing status updates by email. Every client gets a private workspace to request features and follow them from quote to delivery, with progress notes written by the engineer doing the work.')}</p>
      <ul class="pts">
        {_pt('plus', 'Request anything', 'New features, fixes, integrations or a whole new app, described in plain language.')}
        {_pt('receipt', 'Approve fixed quotes', 'See the price, scope and ETA before any work starts. Approve with one click.')}
        {_pt('activity', 'Follow real progress', 'Status, percent complete and notes from your engineer, not an automated ticket bot.')}
        {_pt('badge', 'Accept, then pay', 'Review on staging. Accept the result or request changes.')}
      </ul>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <button type="button" class="aa-btn" data-act="signup">{t('Create your workspace')} <span class="arr">&rarr;</span></button>
        <button type="button" class="aa-btn ghost" data-act="login">{t('Sign in')}</button>
      </div>
    </div>
    <div class="rv d2">
      <div class="tabs" role="tablist"><button type="button" class="on" data-act="wstab" data-arg="client" role="tab">{t('Client view')}</button>
        <button type="button" data-act="wstab" data-arg="admin" role="tab">{t('Consultant view')}</button></div>
      <div class="panel on" data-panel="client">{WS_CLIENT}</div>
      <div class="panel" data-panel="admin">{WS_ADMIN}</div>
    </div>
  </div>
</section>

<!-- ============================================================ engagements -->
<section class="lp-sec lp-alt" id="engage" data-ch="engage" aria-labelledby="eng-title">
  <div class="aa-wrap">
    <div class="lp-head center rv">
      <div class="eyebrow">{t('Engagements')}</div>
      <h2 id="eng-title">{t('Three ways to <em>work together.</em>')}</h2>
      <p class="lead">{t('Every engagement runs through your workspace, with fixed quotes and acceptance-based billing.')}</p>
    </div>
    <div class="lp-eng">{ENGAGEMENTS}</div>
  </div>
</section>

<!-- ============================================================ partners (deck download) -->
<section class="lp-sec tight" id="partners" data-ch="engage" aria-labelledby="partner-title">
  <div class="aa-wrap">
    <div class="lp-partner rv">
      <a class="cover" {deck_attrs()} tabindex="-1" aria-hidden="true">
        <img src="{DECK_COVER}" alt="" loading="lazy" decoding="async" width="960" height="540"></a>
      <div class="txt">
        <div class="eyebrow">{t('For agencies and software firms')}</div>
        <h2 id="partner-title">{t('Need extra hands on delivery? <em>Partner with us.</em>')}</h2>
        <p>{t("We build fixed-price modules, prototypes and internal tools behind consulting and software firms, at AI speed with senior sign-off. The partner deck covers what we've shipped, how we work, our stack and how a first pilot runs.")}</p>
        <div class="dl">
          <a class="aa-btn accent" {deck_attrs()}>{icon('file', 'width="18" height="18"')} {t('Download the partner deck')}</a>
          <span class="meta">{t('PDF · {n} slides · {size}', n=DECK_SLIDES, size=t(DECKS[DECK_LANG][2]))} · {i18n.NAMES[DECK_LANG]}</span>
        </div>
        <p class="aa-langs">{other_languages(_deck_lang_link)}</p>
      </div>
    </div>
  </div>
</section>

<!-- ============================================================ commitments -->
<section class="lp-sec tight" data-ch="engage" aria-label="{t('Our commitments')}">
  <div class="aa-wrap"><div class="lp-commit">{COMMITMENTS}</div></div>
</section>

<!-- ============================================================ free guides -->
<section class="lp-sec tight lp-alt" id="guides" data-ch="engage" aria-labelledby="guides-title">
  <div class="aa-wrap lp-gteaser">
    <div class="txt rv">
      <div class="eyebrow">{t('Free guides')}</div>
      <h2 id="guides-title">{t('Five short guides <em>for people who run things.</em>')}</h2>
      <p>{t('Spreadsheets that became apps, what software should cost, buying AI-built work, build or buy, and Law 25. Practical, sourced, about ten pages each.')}</p>
      <a class="aa-btn accent" href="#guides">{icon('file', 'width="18" height="18"')} {t('Get the free guides')} <span class="arr">&rarr;</span></a>
    </div>
    <div class="fan rv d1" aria-hidden="true">{''.join(f'<a href="#guides/{g[0]}" tabindex="-1"><img src="{guide_cover(g[0])}" alt="" loading="lazy" decoding="async" width="480" height="621"></a>' for g in GUIDES)}</div>
  </div>
</section>

<!-- ============================================================ montreal -->
<section class="lp-sec tight" id="montreal" data-ch="" aria-labelledby="mtl-title" style="padding-top:0">
  <div class="aa-wrap lp-local">
    <div class="rv">
      <div class="eyebrow">{t('Based in Montréal')}</div>
      <h2 id="mtl-title" class="sr-only">{t('Custom software development in Montréal')}</h2>
      <blockquote>{t('Built in Montréal for teams everywhere. <em>Local accountability, global standards.</em>')}</blockquote>
      <p class="muted" style="margin-top:20px;max-width:560px">{t('We meet Montréal businesses in person and work remotely with clients across Canada, the United States and Europe, in your time zone and your language. From startups validating an MVP to established companies replacing spreadsheets with real software.')}</p>
    </div>
    <div class="fr rv d2" lang="fr-CA">
      <div class="eyebrow">En français</div>
      <h3>Développement d'applications sur mesure à Montréal</h3>
      <p>Addanapp conçoit et développe des applications web, des portails clients et des tableaux de bord administratifs pour
        les PME et les entreprises en croissance. L'intelligence artificielle accélère chaque étape; un ingénieur valide chaque
        livraison. Vous payez pour des résultats acceptés, pas pour des heures.</p>
      <p style="margin:0"><b>Service offert en français et en anglais.</b> <a href="#home/contact">Parlez-nous de votre projet &rarr;</a></p>
    </div>
  </div>
</section>

<!-- ============================================================ faq -->
<section class="lp-sec lp-alt" id="faq" data-ch="faq" aria-labelledby="faq-title">
  <div class="aa-wrap lp-faq">
    <div class="rv">
      <div class="eyebrow">{t('FAQ')}</div>
      <h2 id="faq-title">{t('Questions, <em>answered.</em>')}</h2>
      {FAQ_CONTACT}
    </div>
    <div>{_faq()}</div>
  </div>
</section>

<!-- ============================================================ contact -->
<section class="lp-sec on-dark" id="contact" data-ch="" aria-labelledby="contact-title">
  <div class="aa-wrap lp-contact">
    <div class="rv">
      <div class="eyebrow">{t('Start a project')}</div>
      <h2 id="contact-title">{t("Tell us what you need. <em>We'll tell you what it costs.</em>")}</h2>
      <p class="lead">{t("Send a short brief. Within two business days you'll hear back from an engineer, not a salesperson, with questions or a fixed quote.")}</p>
      <div class="ways">
        {EMAIL_WAY}
        <div class="way"><span class="i">{icon('pin')}</span><div><b>{t('Studio')}</b>{t('Montréal, Québec, Canada')}</div></div>
        <div class="way"><span class="i">{icon('clock')}</span><div><b>{t('Response time')}</b>{t('Within two business days')}</div></div>
      </div>
    </div>
    {LEAD_FORM}
  </div>
</section>

</div>'''
