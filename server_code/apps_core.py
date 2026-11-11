"""Apps: a client's app portfolio board (the App Board that used to run on the user's PC, moved here 2026-11-11).

Shared logic for the browser API (api_apps.py) and the PC / Claude HTTP API (apps_sync.py).

Data (all rows belong to one client, a `users` row):
  app_projects  one row per app: `card` = the facts the PC worker found (GitHub, live site, SEO, schema, legal,
                standard audit, videos, biz dev and money plans; written by the worker, never by the browser),
                `state` = what people click here (checks, notes, parked, posted), screenshots, posts, video kit
  app_docs      per client: meta (steps, refresh time, errors), bizdev/* plans, outreach log, youtube stats,
                dismissed notifications, worker heartbeat
  app_jobs      work for the PC worker (refresh, links, Prepsto ideas, YouTube numbers), done when the PC is on
  requests      "Changes for Claude" are ordinary requests with project = the app key (kind 'change')

The PC side lives in APP_MAKER/board/addanapp_link.py.
"""
import datetime
import html
import re

import anvil.tables as tables
from anvil.tables import app_tables

from .common import now, rid, STATUS_LABEL

DONE_STATUSES = ('delivered', 'declined')
TODO_STATUSES = ('new', 'scoping', 'in_progress')  # changes Claude still has to make
MANAGED_STATE = ('checks', 'notes', 'parked', 'posted')  # what the browser owns in `state`

SHORT = {'github': 'GitHub', 'anvil': 'Anvil', 'domain': 'Domain', 'legal': 'Legal', 'seo': 'SEO', 'admin': 'Admin',
         'usability': 'Usability', 'tech': 'Tech', 'linkedin': 'LinkedIn', 'social': 'Social', 'youtube': 'YouTube',
         'arkvital': 'arkvital', 'addanapp': 'addanapp', 'std_map': 'Map', 'std_schema': 'Schema',
         'std_prepsto': 'Prepsto', 'std_devlink': 'Dev link', 'std_parent': 'Parent', 'forms': 'Forms'}
SEO_LABELS = [('title', 'Page title'), ('description', 'Meta description'), ('canonical', 'Canonical link'),
              ('share', 'Share tags (og:title + og:image)'), ('robots', 'robots.txt'), ('sitemap', 'sitemap.xml')]
STD_LABELS = {'map': 'Code map (APP_MAP.md)', 'youtube': 'Watch section with the YouTube video',
              'prepsto': 'Submit feedback → Prepsto link', 'devlink': 'Footer: Contact developer, arkvital.com',
              'parent': 'Footer: Parent company, addanapp.com'}
NOTE_TYPES = [
  ('error', 'Refresh problems', 'Something went wrong while the PC checked your apps.'),
  ('schema', 'Database doesn’t match the code', 'The live database is missing tables or columns that anvil.yaml on GitHub has. Until it’s fixed, parts of the app can break.'),
  ('down', 'Site not answering', 'The live address didn’t answer at the last check.'),
  ('changes', 'Changes queued for Claude', 'Requests you wrote for an app. Claude makes them with /app-board run.'),
  ('link', 'New links to finish', 'You saved a new live address. Claude still has to put it in Privacy & Terms and the README, then redeploy.'),
  ('merge', 'Branches to merge', 'GitHub branches with work that master doesn’t have yet. You merge them on GitHub; the live app follows master.'),
  ('legal', 'Legal needs work', 'The Privacy & Terms page isn’t in good standing.'),
  ('seo', 'SEO gaps', 'Things search engines look for that the live site is missing.'),
  ('standard', 'App standard', 'Quick fixes from the app standard. (Forms conversions are left out: that’s /app-forms.)'),
  ('guess', 'Found on Anvil?', 'An Anvil site with this app’s name answers. If it’s yours, save it as the app’s live link.'),
  ('video', 'Pitch video ready to upload', 'The pitch video is made but not published on YouTube yet.'),
  ('moved', 'Moved to a new domain', 'The app moved address. Videos and reels made before the move show the old one: make fresh ones, then upload them.'),
]
NOTE_ICONS = {'error': 'alert', 'schema': 'database', 'down': 'x', 'changes': 'edit', 'link': 'link', 'merge': 'branch',
              'legal': 'shield', 'seo': 'search', 'standard': 'ruler', 'guess': 'compass', 'video': 'play', 'moved': 'truck'}
EXTRA_LANES = [{'id': 'launched', 'name': 'Launched', 'desc': 'Every step done or marked not needed.'},
               {'id': 'parked', 'name': 'Parked', 'desc': 'On hold. Open an app and choose Park to move it here or back.'}]
MODULES = ('posts', 'bizdev', 'money', 'youtube')  # optional views; the board, grid, dossiers and notes always show


def esc(s):
  return html.escape(str(s if s is not None else ''), quote=True)


def parse_iso(s):
  if not s:
    return None
  if isinstance(s, datetime.datetime):
    return s if s.tzinfo else s.replace(tzinfo=datetime.timezone.utc)
  try:
    d = datetime.datetime.fromisoformat(str(s).replace('Z', '+00:00'))
  except ValueError:
    try:
      d = datetime.datetime.strptime(str(s)[:10], '%Y-%m-%d')
    except ValueError:
      return None
  return d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)


def ago(s):
  d = parse_iso(s)
  if d is None:
    return ''
  sec = (now() - d).total_seconds()
  if sec < 90:
    return 'just now'
  if sec < 3600:
    return '%dm ago' % round(sec / 60)
  if sec < 86400:
    return '%dh ago' % round(sec / 3600)
  if sec < 86400 * 45:
    return '%dd ago' % round(sec / 86400)
  return d.strftime('%Y-%m-%d')


def plural(n, word, many=None):
  return '%d %s' % (n, word if n == 1 else (many or word + 's'))


# ---------------------------------------------------------------- docs

def doc_row(client, name):
  return app_tables.app_docs.get(client=client, name=name)


def doc_data(client, name, default=None):
  r = doc_row(client, name)
  if r is None or r['data'] is None:
    return default
  return r['data']


def doc_text(client, name):
  r = doc_row(client, name)
  return (r['text'] or '') if r is not None else ''


def set_doc(client, name, data=None, text=None):
  r = doc_row(client, name)
  ch: dict = {'updated': now()}
  if data is not None:
    ch['data'] = data
  if text is not None:
    ch['text'] = text
  if r is None:
    r = app_tables.app_docs.add_row(client=client, name=name, **ch)
  else:
    r.update(**ch)
  return r


def meta(client):
  m = doc_data(client, 'meta', {}) or {}
  return m if isinstance(m, dict) else {}


def phases_of(m):
  ph = m.get('phases') or []
  return ph if isinstance(ph, list) else []


def lanes(phases):
  return [{'id': p['id'], 'name': p['name'], 'desc': p.get('desc', '')} for p in phases] + EXTRA_LANES


def flat_items(phases):
  return [dict(it, phase=p['id']) for p in phases for it in p.get('items', [])]


# ---------------------------------------------------------------- portfolio owners

def portfolio_clients():
  """Clients that have an app portfolio, as (row, number of apps)."""
  counts: dict = {}
  rows: dict = {}
  for r in app_tables.app_projects.search():
    c = r['client']
    if c is None:
      continue
    k = c.get_id()
    counts[k] = counts.get(k, 0) + 1
    rows[k] = c
  return [(rows[k], counts[k]) for k in rows]


def has_portfolio(u):
  if u is None:
    return False
  if u['is_admin']:
    return len(app_tables.app_projects.search()) > 0
  return len(app_tables.app_projects.search(client=u)) > 0


# ---------------------------------------------------------------- one app

def posted_of(card, state):
  """Posted / published ticks; a public pitch video on YouTube counts as published on its upload date."""
  m = dict(state.get('posted') or {})
  y = card.get('youtube') or {}
  if y.get('public') and not m.get('yt-video'):
    m['yt-video'] = y.get('published') or 'yes'
  return m


def auto_of(card, state):
  a = dict(card.get('auto') or {})
  m = posted_of(card, state)
  a['linkedin'] = any(k.startswith('li') and v for k, v in m.items())
  a['youtube'] = any(k.startswith('yt') and v for k, v in m.items()) and card.get('watch', True) is not False
  return a


def item_value(state, auto, item_id):
  v = (state.get('checks') or {}).get(item_id)
  if v in ('done', 'na', 'todo'):
    return v, False
  return ('done' if auto.get(item_id) else 'todo'), bool(auto.get(item_id))


def stage_of(state, auto, phases):
  if state.get('parked'):
    return 'parked'
  for ph in phases:
    if any(item_value(state, auto, it['id'])[0] == 'todo' for it in ph.get('items', [])):
      return ph['id']
  return 'launched'


def clean_desc(card):
  d = card.get('desc') or ''
  name = card.get('name') or ''
  i = d.find(':')
  if 0 < i < 40 and d[:i].lower().replace(' ', '') == name.lower().replace(' ', ''):
    d = d[i + 1:].strip()
  if 'built with anvil' in d.lower():
    d = ''
  return d or card.get('notes_tech') or ''


def changes_by_key(client):
  """Open "Changes for Claude": the client's requests whose project is an app key."""
  out: dict = {}
  if client is None:
    return out
  for r in app_tables.requests.search(tables.order_by('created', ascending=True), client=client):
    if not r['project'] or r['status'] in DONE_STATUSES:
      continue
    out.setdefault(r['project'], []).append({
      'id': rid(r), 'ref': r['ref'], 'title': r['title'], 'status': r['status'],
      'status_label': STATUS_LABEL.get(r['status'], r['status']), 'description': r['description'] or ''})
  return out


def changes_text(changes):
  return '\n\n'.join('%s (%s): %s' % (c['ref'], c['status_label'], c['description'] or c['title']) for c in changes)


def tags_of(v):
  t = []
  s = v.get('structure') or ''
  if s and s != 'missing':
    if s == 'forms':
      t.append({'text': '◧ Forms', 'cls': 'ok', 'title': 'Native Anvil Forms: Layouts + components, as Anvil prescribes'})
    elif v.get('forms_branch'):
      t.append({'text': '◧ Forms on branch', 'cls': 'merge', 'title': 'Converted to Forms on branch forms, not merged yet'})
    elif s == 'classic':
      t.append({'text': '◧ Classic Forms', 'cls': '', 'title': 'Old Anvil designer Forms, no Layouts yet: /app-forms converts it'})
    else:
      t.append({'text': '◧ JavaScript', 'cls': '', 'title': 'JavaScript pages front end: /app-forms converts it to native Anvil Forms'})
  m = v.get('money')
  if m:
    t.append({'text': m.get('role_icon', '') + ' ' + ('traffic' if m.get('role') == 'traffic' else (m.get('role_label') or '').lower()),
              'cls': 'money', 'title': (m.get('role_label') or '') + ': ' + (m.get('role_meaning') or '') + ' · ' + (m.get('when_label') or '')})
  b = v.get('bizdev')
  if b and str(b.get('wave')) == '1':
    t.append({'text': '🎯 Wave 1', 'cls': 'ok', 'title': 'Biz dev Wave 1: active outreach now. Open the app for the plan.'})
  if v.get('video') and not v['posted'].get('yt-video'):
    t.append({'text': '🎬 video ready', 'cls': '', 'title': 'Pitch video ready to upload'})
  if v.get('changes_todo'):
    t.append({'text': '📝 ' + plural(len(v['changes_todo']), 'change') + ' queued', 'cls': 'ai', 'title': 'Changes for Claude: /app-board run ' + v['key']})
  review = [c for c in v.get('changes') or [] if c['status'] == 'review']
  if review:
    t.append({'text': '👀 %d to review' % len(review), 'cls': 'ok', 'title': 'Claude finished: test it, then accept the request'})
  if v.get('url_followup'):
    t.append({'text': '🔗 tell Claude', 'cls': '', 'title': 'New link saved: Claude still has to finish it'})
  if (v.get('schema') or {}).get('state') == 'mismatch':
    t.append({'text': '🗄️ schema mismatch', 'cls': 'bad', 'title': 'The live database does not match the code'})
  if v.get('guess_url'):
    t.append({'text': '🔎 found on Anvil?', 'cls': '', 'title': 'A live Anvil site with this name exists: open the app to confirm'})
  if v.get('branches'):
    t.append({'text': '⑂ %d to merge' % len(v['branches']), 'cls': 'merge',
              'title': 'Branches to merge into master: ' + ', '.join(b.get('name', '') for b in v['branches'])})
  return t


CARD_FIELDS = ('key', 'name', 'source', 'repo', 'url', 'url_kind', 'domain_planned', 'anvil_editor', 'github_url',
               'github_missing', 'pushed_at', 'branch', 'branches', 'branches_merged', 'live', 'seo', 'schema', 'legal',
               'guess_url', 'guess_title', 'url_followup', 'folder', 'local', 'layout', 'old_urls', 'moved', 'structure',
               'forms_branch', 'standard_problems', 'watch', 'youtube', 'video', 'promo', 'bizdev', 'money', 'prepsto')


def view(row, phases, changes, full=False, media=True):
  """One app as the pages show it: the worker's facts + the browser's state, with the steps worked out."""
  card = row['card'] or {}
  state = row['state'] or {}
  auto = auto_of(card, state)
  v = {k: card.get(k) for k in CARD_FIELDS}
  v['key'], v['name'] = row['key'], row['name'] or card.get('name') or row['key']
  v['desc'] = clean_desc(dict(card, name=v['name']))
  v['branches'] = v['branches'] or []
  v['posted'] = posted_of(card, state)
  v['auto'] = auto
  items = {}
  done = 0
  total = 0
  nxt = None
  for ph in phases:
    for it in ph.get('items', []):
      val, is_auto = item_value(state, auto, it['id'])
      items[it['id']] = {'v': val, 'auto': is_auto}
      total += 1
      if val != 'todo':
        done += 1
      elif nxt is None:
        nxt = it['label']
  v['items'], v['done'], v['total'], v['next'] = items, done, total, nxt
  v['stage'] = stage_of(state, auto, phases)
  v['stage_name'] = next((ln['name'] for ln in lanes(phases) if ln['id'] == v['stage']), v['stage'])
  v['parked'] = bool(state.get('parked'))
  v['notes'] = state.get('notes') or ''
  v['changes'] = changes.get(row['key'], [])
  v['changes_todo'] = [c for c in v['changes'] if c['status'] in TODO_STATUSES]
  v['tags'] = tags_of(v)
  if media:
    v['hero'], v['hero_phone'], v['thumb'] = row['hero'], row['hero_phone'], row['thumb']
  else:
    v['has_hero'] = row['hero'] is not None
  if full:
    v['commits'] = (card.get('commits') or [])[:8]
    v['changes_done'] = card.get('changes_done') or ''
  return v


def views(client, full=False, media=True):
  m = meta(client)
  phases = phases_of(m)
  ch = changes_by_key(client)
  rows = app_tables.app_projects.search(client=client)
  return [view(r, phases, ch, full=full, media=media) for r in rows], m


def stats(vs):
  by: dict = {}
  for v in vs:
    by[v['stage']] = by.get(v['stage'], 0) + 1
  forms = len([v for v in vs if v.get('structure') == 'forms'])
  known = len([v for v in vs if v.get('structure')])
  return [('projects', len(vs)), ('live', len([v for v in vs if (v.get('live') or {}).get('ok')])),
          ('to deploy', by.get('build', 0) + by.get('deploy', 0)), ('to test', by.get('test', 0)),
          ('to promote', by.get('promote', 0)), ('to standard', by.get('standard', 0)),
          ('native Forms', '%d/%d' % (forms, known)), ('launched', by.get('launched', 0))]


# ---------------------------------------------------------------- notifications

def _ul(items):
  return '<ul>' + ''.join('<li>%s</li>' % x for x in items) + '</ul>' if items else ''


def _codes(xs):
  return ', '.join('<code>%s</code>' % esc(x) for x in xs)


def notes(vs, m):
  """Everything that needs the user or Claude: [{id, sig, type, key, name, stage, title, desc (html), prompt, acts}].
    acts: [{label, href}] links, or [{label, do}] with do in refresh | posts | grid-merge | grid-schema."""
  out = []

  def add(n):
    n['id'] = n['type'] + ':' + (n.get('key') or n.get('k', ''))
    n['sig'] = str(n.get('sig') if n.get('sig') is not None else n['prompt'])
    out.append(n)

  for e in m.get('errors') or []:
    e = str(e)
    add({'type': 'error', 'k': e[:80], 'title': e.split(':')[0][:60] or 'Problem', 'desc': esc(e),
         'prompt': 'The App Board refresh reported this problem: "%s". Find out why (APP_MAKER/board/server.py and the tool it '
                   'names) and fix it, or tell me what I need to do.' % e, 'acts': [{'label': 'Refresh all', 'do': 'refresh-all'}]})
  for v in vs:
    n, k = v['name'], v['key']
    base = {'key': k, 'name': n, 'stage': v['stage'], 'stage_name': v['stage_name']}
    ed = [{'label': 'Anvil editor ↗', 'href': v['anvil_editor']}] if v.get('anvil_editor') else []
    site = [{'label': 'Open site ↗', 'href': v['url']}] if v.get('url') else []
    sc = v.get('schema') or {}
    if sc.get('state') == 'mismatch':
      parts = []
      for label, key in (('Tables missing in the database', 'missing_tables'), ('Columns missing in the database', 'missing_columns'),
                         ('Columns only in the database (accepting the code’s schema deletes them)', 'extra_columns')):
        if sc.get(key):
          parts.append(label + ': ' + _codes(sc[key]))
      txt = ''.join(' %s: %s.' % (lbl, ', '.join(sc[key])) for lbl, key in
                    (('Missing tables', 'missing_tables'), ('Missing columns', 'missing_columns'),
                     ('Columns only in the database', 'extra_columns')) if sc.get(key))
      add(dict(base, type='schema', title='live database ≠ code',
               desc=_ul(parts) + '<span class="muted">Fix: in the Anvil editor, click <b>Resolve</b> on the Schema Mismatch alert. '
                                 'Checked %s.</span>' % esc(ago(sc.get('checked'))),
               prompt="%s (%s): the live database doesn't match anvil.yaml on GitHub.%s Tell me exactly what to choose in the "
                      "Anvil editor's Schema Mismatch dialog, or add the columns to the code first if the database is right." % (n, k, txt),
               acts=ed + [{'label': 'Show in grid', 'do': 'grid-schema'}]))
    lv = v.get('live') or {}
    if v.get('url') and v.get('live') and not lv.get('ok'):
      why = lv.get('error') or 'HTTP %s' % lv.get('status')
      add(dict(base, type='down', title='certificate not ready' if lv.get('cert_pending') else 'not answering',
               desc='<code>%s</code>: %s. Checked %s.' % (esc(v['url']), esc(why), esc(ago(lv.get('checked')))),
               prompt="%s's live site %s isn't answering (%s). Find out why and fix it, or tell me what to do in Anvil (publish, "
                      "domain, certificate)." % (n, v['url'], why), acts=site + ed))
    if v.get('changes_todo'):
      txt = changes_text(v['changes_todo'])
      add(dict(base, type='changes', title=plural(len(v['changes_todo']), 'change') + ' waiting',
               desc='<div class="ap-pre">%s</div>' % esc(txt[:600] + ('…' if len(txt) > 600 else '')),
               prompt='/app-board run %s' % k, sig=txt,
               acts=[{'label': 'Request %s' % c['ref'], 'href': '#r/' + c['id']} for c in v['changes_todo'][:3]]))
    if v.get('url_followup'):
      add(dict(base, type='link', title='new link saved', desc='Live address <code>%s</code>. %s' % (esc(v.get('url')), esc(v['url_followup'])),
               prompt='/app-board finish %s — the new live link %s still has to go into the legal kit, README/guide and a deploy.' % (k, v.get('url'))))
    bs = v.get('branches') or []
    if bs:
      lines = []
      for b in bs:
        x = '<code>%s</code> · %s not on %s' % (esc(b.get('name')), plural(b.get('ahead', 0), 'commit'), esc(b.get('base')))
        if b.get('last_msg'):
          x += ' · last: “%s”' % esc(b['last_msg'])
        if b.get('last_date'):
          x += ' · ' + esc(ago(b['last_date']))
        if b.get('pr'):
          x += ' · pull request #%s' % b['pr'].get('number')
        lines.append(x)
      what = '; '.join('%s (%s%s)' % (b.get('name'), plural(b.get('ahead', 0), 'commit'),
                                       ', last: "%s"' % b['last_msg'] if b.get('last_msg') else '') for b in bs)
      acts = [{'label': 'PR #%s ↗' % b['pr']['number'], 'href': b['pr']['url']} if b.get('pr') else
              {'label': 'Merge %s ↗' % b.get('name'), 'href': b.get('compare_url')} for b in bs]
      add(dict(base, type='merge', title=plural(len(bs), 'branch', 'branches'), desc=_ul(lines),
               prompt="%s (GitHub %s) has work on %s not merged into %s: %s. Review what %s and tell me whether it's safe to merge, "
                      "and anything I must test first." % (n, v.get('repo'), 'a branch' if len(bs) == 1 else 'branches',
                                                            bs[0].get('base'), what, 'it changes' if len(bs) == 1 else 'each one changes'),
               sig=str([b.get('name', '') + str(b.get('sha', '')) for b in bs]), acts=acts + [{'label': 'Show in grid', 'do': 'grid-merge'}]))
    lg = v.get('legal') or {}
    if v.get('legal') and not lg.get('ok'):
      probs = lg.get('problems') or []
      add(dict(base, type='legal', title=plural(len(probs), 'issue'), desc=_ul([esc(x) for x in probs]),
               prompt='/app-board fix legal for %s (%s). The App Board says: %s' % (n, k, ' '.join(probs))))
    seo = v.get('seo') or {}
    if seo.get('missing'):
      add(dict(base, type='seo', title='%d missing' % len(seo['missing']),
               desc='Missing on the live site: %s.' % ', '.join(esc(x) for x in seo['missing']),
               prompt='/app-board fix SEO for %s (%s): the live site %s is missing %s. Then re-check with board_cli.py check %s.'
                      % (n, k, v.get('url'), ', '.join(seo['missing']), k), acts=site))
    std = [(r, pr) for r, pr in (v.get('standard_problems') or {}).items() if r in STD_LABELS]
    if std:
      add(dict(base, type='standard', title=', '.join(STD_LABELS[r].split(' (')[0].split(':')[0] for r, _ in std),
               desc=_ul(['<b>%s</b>%s' % (esc(STD_LABELS[r]), (': ' + esc(' '.join(pr))) if pr else '') for r, pr in std]),
               prompt='/app-standard %s (%s): fix %s.' % (n, k, '; '.join(STD_LABELS[r] + (' (%s)' % ' '.join(pr) if pr else '') for r, pr in std))))
    if v.get('guess_url'):
      gt = v.get('guess_title') or ''
      add(dict(base, type='guess', title='live site found',
               desc='<code>%s</code> answers%s. Open the app to confirm it with one click.' % (esc(v['guess_url']), ' with “%s”' % esc(gt) if gt else ''),
               prompt="%s (%s) has no live link on the App Board, but %s answers%s. Check whether it's this app and, if so, save it as "
                      "its url in apps.json and finish the link (/app-board finish)." % (n, k, v['guess_url'], ' ("%s")' % gt if gt else ''),
               acts=[{'label': 'Open it ↗', 'href': v['guess_url']}]))
    vid = v.get('video') or {}
    if v.get('video') and not v['posted'].get('yt-video'):
      add(dict(base, type='video', title='ready' + (' (%s)' % vid.get('length') if vid.get('length') else ''),
               desc='The pitch video, thumbnail and upload kit are ready in the Posts view.',
               prompt='Upload the %s (%s) pitch video to YouTube with youtube/yt.py, make it public, and make sure the app shows it in '
                      'its Watch section.' % (n, k), acts=[{'label': 'Upload kit', 'do': 'posts'}]))
    if v.get('moved'):
      frm = (v.get('old_urls') or ['its old address'])[-1]
      made = vid.get('made') or ''
      pub = (v.get('youtube') or {}).get('published') or ''
      if not made or made < v['moved']:
        add(dict(base, type='moved', title='fresh videos needed',
                 desc='Moved from <code>%s</code> to <code>%s</code> on %s. The pitch video%s and reels still show the old address.'
                      % (esc(frm), esc(v.get('url')), esc(v['moved']), ' (made %s)' % esc(made) if made else ''),
                 prompt='%s (%s) moved from %s to %s on %s. Make a fresh pitch video and 5 reels that show the new address (/domain-move, '
                        'videos step).' % (n, k, frm, v.get('url'), v['moved'])))
      elif not pub or pub < v['moved']:
        add(dict(base, type='moved', title='new videos to upload',
                 desc='The new pitch video (made %s) and reels for %s are ready. Upload them in YouTube Studio; then Claude fills them in.'
                      % (esc(made), esc(v.get('url'))),
                 prompt='I uploaded the new %s (%s) pitch video and reels made after its move to %s. Fill them in with yt.py / ytreels.py '
                        "apply, point youtube/manifest.json and the app's Watch section at the new video, and ask me what to do with the "
                        'old videos (/domain-move, after-upload step).' % (n, k, v.get('url')), acts=[{'label': 'Upload kit', 'do': 'posts'}]))
  return out


# ---------------------------------------------------------------- markdown (biz dev plans) -> HTML

DOC_NAME = re.compile(r'README|PLAYBOOK|outreach-log|apps/[a-z0-9_-]+')


def doc_link(href, base):
  """A link inside a biz dev document -> another biz dev document ("apps/x", "PLAYBOOK"...), or None."""
  if re.match(r'^[a-z]+:', href, re.I):
    return None
  parts = base.split('/')[:-1] + href.split('#')[0].split('/')
  out: list = []
  for s in parts:
    if s == '..':
      if out:
        out.pop()
    elif s and s != '.':
      out.append(s)
  name = re.sub(r'\.(md|csv)$', '', '/'.join(out))
  return name if DOC_NAME.fullmatch(name) else None


def doc_route(name):
  """Biz dev document name -> the part after #apps/bizdev/ (no slashes inside an address part)."""
  return name.replace('/', '.')


def _inline(s, base):
  s = esc(s)
  s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)

  def link(m):
    text, url = m.group(1), m.group(2).replace('&amp;', '&')
    d = doc_link(url, base)
    if d:
      return '<a href="#apps/bizdev/%s">%s</a>' % (doc_route(d), text)
    if re.match(r'^https?:', url):
      return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(url), text)
    return text
  s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', link, s)
  s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
  s = re.sub(r'(^|[^*\w])\*([^*\s][^*]*?)\*(?!\w)', r'\1<i>\2</i>', s)
  return s


def _indent(line):
  return len(line) - len(line.lstrip())


def _is_item(line):
  return re.match(r'^\s*(?:[-*]|\d+\.)\s+', line) is not None


def _ordered(line):
  return re.match(r'^\s*\d+\.\s', line) is not None


def _list(lines, i, base):
  ind, ordered = _indent(lines[i]), _ordered(lines[i])
  h = ''
  while i < len(lines):
    ln = lines[i]
    if not ln.strip():
      j = i
      while j < len(lines) and not lines[j].strip():
        j += 1
      if j < len(lines) and (_indent(lines[j]) > ind or (_is_item(lines[j]) and _indent(lines[j]) == ind and _ordered(lines[j]) == ordered)):
        i = j
        continue
      break
    li = _indent(ln)
    if li < ind:
      break
    if li > ind:
      if _is_item(ln):
        add, i = _list(lines, i, base)
      else:
        add, i = '<br>' + _inline(ln.strip(), base), i + 1
      h = h[:-5] + add + '</li>' if h.endswith('</li>') else h + '<li>%s</li>' % add
      continue
    if not _is_item(ln) or _ordered(ln) != ordered:
      break
    h += '<li>%s</li>' % _inline(re.sub(r'^\s*(?:[-*]|\d+\.)\s+', '', ln), base)
    i += 1
  return ('<ol>%s</ol>' if ordered else '<ul>%s</ul>') % h, i


def _table(rows, base):
  def cells(r):
    return [c.strip() for c in re.sub(r'^\||\|$', '', r.strip()).split('|')]
  body = rows[2:] if len(rows) > 1 and re.match(r'^\|[\s:|-]+$', rows[1].strip()) else rows[1:]
  head = ''.join('<th>%s</th>' % _inline(c, base) for c in cells(rows[0]))
  trs = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % _inline(c, base) for c in cells(r)) for r in body)
  return '<div class="ap-table"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (head, trs)


def markdown(text, base=''):
  """Small markdown renderer (headings, nested lists, tables, quotes, rules, bold, italic, code, links). Text is escaped."""
  lines = (text or '').replace('\r', '').split('\n')
  out = []
  i = 0

  def special(ln):
    return re.match(r'^(#{1,4}\s|>|\||-{3,}\s*$)', ln) is not None or _is_item(ln)
  while i < len(lines):
    ln = lines[i]
    if not ln.strip():
      i += 1
      continue
    mh = re.match(r'^(#{1,4})\s+(.*)$', ln)
    if mh:
      lvl = len(mh.group(1)) + 1
      out.append('<h%d>%s</h%d>' % (lvl, _inline(mh.group(2), base), lvl))
      i += 1
    elif re.match(r'^-{3,}\s*$', ln):
      out.append('<hr>')
      i += 1
    elif ln.startswith('|'):
      rows = []
      while i < len(lines) and lines[i].startswith('|'):
        rows.append(lines[i])
        i += 1
      out.append(_table(rows, base))
    elif ln.startswith('>'):
      q = []
      while i < len(lines) and lines[i].startswith('>'):
        q.append(re.sub(r'^>\s?', '', lines[i]))
        i += 1
      out.append('<blockquote>%s</blockquote>' % '<br>'.join(_inline(x, base) for x in q))
    elif _is_item(ln):
      block, i = _list(lines, i, base)
      out.append(block)
    else:
      p = []
      while i < len(lines) and lines[i].strip() and not special(lines[i]):
        p.append(lines[i].strip())
        i += 1
      out.append('<p>%s</p>' % _inline(' '.join(p), base))
  return '\n'.join(out)
