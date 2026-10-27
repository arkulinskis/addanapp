"""Landing page markup. Buttons use data-act (handled in the Landing form).
Everything a search engine should read lives here, on the indexable home page.
Visible text goes through t() so it can be shown in French, Russian or Latvian (see i18n.py)."""
from .icons import icon
from .i18n import t
from . import portfolio

# Blank until the official address is ready; every spot that shows it hides itself while empty.
CONTACT_EMAIL = ''


def _ev(cls, ico, title, text, when):
  return (f'<div class="ev"><div class="ic {cls}">{icon(ico)}</div>'
          f'<div class="t"><b>{title}</b>{text} <span class="when">· {when}</span></div></div>')


HERO_MOCK = f'''
<div class="lp-mock rv d2" role="img" aria-label="{t('Example: a feature request tracked in the Addanapp client workspace, from fixed quote to AI draft, human validation and client review.')}">
  <div class="win">
    <div class="bar"><i></i><i></i><i></i><span class="url">addanapp.com · workspace</span></div>
    <div class="body">
      <div class="top">
        <div><span class="chip mono">AA-1042</span> <span class="chip outline">{t('Integration / API')}</span>
          <h4>{t('Deposits for large-party reservations')}</h4></div>
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
   "request, like any other work."),
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


def _faq():
  out = ''
  for qn, ans in FAQ:
    out += f'<details class="rv"><summary>{t(qn)}</summary><p>{t(ans)}</p></details>'
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
<section class="lp-hero" id="top" aria-labelledby="hero-title">
  <div class="aa-wrap grid">
    <div>
      <div class="tag-loc rv"><b>Montréal</b>{t('Custom software studio · EN / FR')}</div>
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
<section class="lp-sec" id="approach" aria-labelledby="why-title">
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
<section class="lp-sec on-dark" id="method" aria-labelledby="method-title">
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
<section class="lp-sec" id="services" aria-labelledby="svc-title">
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
<section class="lp-sec lp-alt" id="work" aria-labelledby="work-title">
  <div class="aa-wrap">
    <div class="lp-head rv">
      <div class="eyebrow">{t('Selected work')}</div>
      <h2 id="work-title">{t('Shipped, live and <em>in daily use.</em>')}</h2>
      <p class="lead">{t("A sample of products we've designed, built and run, from revenue-generating platforms to games people can't put down. Every one is live, so click through and try it.")}</p>
    </div>
    {portfolio.filter_bar()}
    {portfolio.grid()}
    <div class="center" style="margin-top:40px"><a class="aa-btn ghost" href="#work">{t('Explore every project in detail')} <span class="arr">&rarr;</span></a></div>
  </div>
</section>

<!-- ============================================================ workspace -->
<section class="lp-sec" id="workspace" aria-labelledby="ws-title">
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
<section class="lp-sec lp-alt" id="engage" aria-labelledby="eng-title">
  <div class="aa-wrap">
    <div class="lp-head center rv">
      <div class="eyebrow">{t('Engagements')}</div>
      <h2 id="eng-title">{t('Three ways to <em>work together.</em>')}</h2>
      <p class="lead">{t('Every engagement runs through your workspace, with fixed quotes and acceptance-based billing.')}</p>
    </div>
    <div class="lp-eng">{ENGAGEMENTS}</div>
  </div>
</section>

<!-- ============================================================ commitments -->
<section class="lp-sec tight" aria-label="{t('Our commitments')}">
  <div class="aa-wrap"><div class="lp-commit">{COMMITMENTS}</div></div>
</section>

<!-- ============================================================ montreal -->
<section class="lp-sec tight" id="montreal" aria-labelledby="mtl-title" style="padding-top:0">
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
<section class="lp-sec lp-alt" id="faq" aria-labelledby="faq-title">
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
<section class="lp-sec on-dark" id="contact" aria-labelledby="contact-title">
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
