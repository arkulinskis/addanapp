"""Apps: check an app's facts from addanapp.com itself, only when someone presses Refresh (no schedule, no PC link).

    ACTIONS                      github (commits, branches to merge, anvil.yaml tables) · live (site + SEO, and the
                                 <name>.anvil.app guess) · schema (live database vs anvil.yaml) · mentions (arkvital.com,
                                 addanapp.com)
    refresh(rows, acts)          check up to BATCH apps in parallel and write the facts into their cards
    save_link(row, field, value) a link typed on the board (the PC's one-shot update copies it into apps.json)
    send_idea / open_tickets     the app's Prepsto feedback link, with Claude's Prepsto key
    youtube_numbers(data)        fresh public numbers for the channel and the client's videos

What only the PC has (the standard audit, legal status, screenshots, posts, video kits, plans, new apps) still comes
from its one-shot update, APP_MAKER/board/addanapp_link.py sync. Facts written here carry card['server']['at']; a PC push
with older facts keeps them (apps_sync.a_push -> keep_server_facts).

App Secrets: github_token (fine-grained, read-only), prepsto_key (Claude's Prepsto API key), youtube_api_key (Google API
key for the YouTube Data API v3: public numbers only, it can't touch the channel).
"""
import concurrent.futures
import datetime as dt
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

import anvil.secrets

ACTIONS = {
  'github': "GitHub: commits, branches to merge, the tables in anvil.yaml",
  'live': "Live site + SEO (and the <name>.anvil.app guess for apps with no link)",
  'schema': "Live database vs the code (schema check)",
  'mentions': "Mentioned on arkvital.com / addanapp.com",
}
BATCH = 3           # apps per server call (the browser sends the next batch when one is done)
TIMEOUT = 12        # per web request
DEADLINE = 24       # per call: Anvil stops a server call after 30 s; unfinished apps keep their last facts
SERVER_FIELDS = ('desc', 'github_url', 'github_missing', 'pushed_at', 'commits', 'branch', 'branches', 'branches_merged',
                 'guess_url', 'guess_title', 'live', 'seo', 'schema')
SERVER_AUTO = ('github', 'anvil', 'domain', 'seo', 'arkvital', 'addanapp')
LINK_FIELDS = ('url', 'anvil_editor')
MENTION_PAGES = {'arkvital': ['https://arkvital.com/', 'https://arkvital.com/apps.html', 'https://arkvital.com/projects.html'],
                 'addanapp': ['https://addanapp.com/']}
SEO_CHECKS = [('title', 'Page title'), ('description', 'Meta description'), ('canonical', 'Canonical link'),
              ('share', 'Share tags (og:title + og:image)'), ('robots', 'robots.txt'), ('sitemap', 'sitemap.xml')]
# columns Anvil's Users service adds by itself (remember me, Google sign-in...): not a mismatch
USERS_SERVICE_COLUMNS = {'email', 'enabled', 'signed_up', 'last_login', 'password_hash', 'n_password_failures',
                         'confirmed_email', 'email_confirmation_key', 'remembered_logins', 'mfa'}
PREPSTO = 'https://prepsto.com/_/api'
YOUTUBE = 'https://www.googleapis.com/youtube/v3'
_cache: dict = {'mentions_at': 0, 'mentions': None, 'links_at': 0, 'links': {}}


def now_iso():
  return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def secret(name, what):
  try:
    v = anvil.secrets.get_secret(name)
  except Exception:
    v = None
  if not v or not str(v).strip():
    raise Exception("Add the App Secret %s in the Anvil editor first (%s)." % (name, what))
  return str(v).strip()


def http(url, headers=None, limit=600000, method='GET', body=None):
  """-> (status, text). An HTTP error comes back as its status; a network problem raises. (Tests replace this.)"""
  h = {'User-Agent': 'Mozilla/5.0 (Addanapp App Board)'}
  h.update(headers or {})
  data = None
  if body is not None:
    data = json.dumps(body).encode('utf-8')
    h['Content-Type'] = 'application/json'
  req = urllib.request.Request(url, data=data, method=method, headers=h)
  try:
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
      return r.status, r.read(limit).decode('utf-8', 'replace')
  except urllib.error.HTTPError as e:
    try:
      txt = e.read(20000).decode('utf-8', 'replace')
    except Exception:
      txt = ''
    return e.code, txt


def _json(txt):
  try:
    return json.loads(txt) if txt else None
  except ValueError:
    return None


# ---------------------------------------------------------------- GitHub

def gh(token, path):
  st, txt = http('https://api.github.com' + path, {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                                                    'X-GitHub-Api-Version': '2022-11-28'}, limit=5000000)
  if st == 401:
    raise Exception("GitHub refused the github_token App Secret (expired or mistyped?).")
  if st in (403, 429) and 'rate limit' in (txt or '').lower():
    raise Exception("GitHub's rate limit was reached: try again in an hour.")
  return st, _json(txt)


def fetch_commits(token, full, default_branch):
  for branch in ('master', default_branch):
    st, body = gh(token, '/repos/%s/commits?per_page=8&sha=%s' % (full, urllib.parse.quote(branch or 'master')))
    if st == 200 and isinstance(body, list):
      return [{'sha': c['sha'][:7], 'msg': ((c.get('commit') or {}).get('message') or '').splitlines()[0][:140] if (c.get('commit') or {}).get('message') else '',
               'date': ((c.get('commit') or {}).get('committer') or {}).get('date', ''),
               'author': ((c.get('commit') or {}).get('author') or {}).get('name', ''), 'url': c.get('html_url', '')} for c in body], branch
  return [], None


def fetch_branches(token, full, base, old):
  """Branches with work that isn't on the base branch yet. old = last check's list: unchanged tips are reused."""
  st, body = gh(token, '/repos/%s/branches?per_page=100' % full)
  if st != 200 or not isinstance(body, list):
    return []
  tips = {b['name']: b['commit']['sha'] for b in body}
  base_sha = tips.get(base)
  if not base_sha:
    return []
  prev = {b.get('name'): b for b in old or []}
  st, pulls = gh(token, '/repos/%s/pulls?state=open&per_page=100' % full)
  prs = {}
  for pr in pulls if st == 200 and isinstance(pulls, list) else []:
    head = pr.get('head') or {}
    if head.get('repo') and head['repo'].get('full_name', '').lower() == full.lower():
      prs[head.get('ref')] = {'number': pr['number'], 'url': pr['html_url'], 'title': pr.get('title', ''), 'into': (pr.get('base') or {}).get('ref')}
  q = lambda s: urllib.parse.quote(s, safe='')
  out = []
  for name, sha in sorted(tips.items()):
    if name == base:
      continue
    b = prev.get(name)
    if not (b and b.get('sha') == sha and b.get('base_sha') == base_sha):
      st, c = gh(token, '/repos/%s/compare/%s...%s?per_page=100' % (full, q(base), q(name)))
      if st != 200 or not isinstance(c, dict):
        continue
      last = (c.get('commits') or [{}])[-1] or {}
      msg = ((last.get('commit') or {}).get('message') or '')
      b = {'name': name, 'sha': sha, 'base_sha': base_sha, 'ahead': c.get('ahead_by', 0), 'behind': c.get('behind_by', 0),
           'last_msg': msg.splitlines()[0][:140] if msg else '',
           'last_date': ((last.get('commit') or {}).get('committer') or {}).get('date', ''),
           'compare_url': 'https://github.com/%s/compare/%s...%s' % (full, q(base), q(name))}
    out.append(dict(b, base=base, pr=prs.get(name)))
  return out


def tables_of(text):
  """{table: [columns]} from anvil.yaml's db_schema (no PyYAML on the server): db_schema -> <table>: -> columns: ->
  list items with a name."""
  out, table, t_ind, col_ind, in_db = {}, None, None, None, False
  for line in text.splitlines():
    if not line.strip() or line.lstrip().startswith('#'):
      continue
    ind = len(line) - len(line.lstrip())
    s = line.strip()
    if ind == 0:
      in_db = s.startswith('db_schema:')
      table = None
      continue
    if not in_db:
      continue
    if t_ind is None or ind <= t_ind:
      m = re.match(r'([A-Za-z_][\w]*):\s*$', s)
      if m:
        t_ind, table, col_ind = ind, m.group(1), None
        out[table] = []
      continue
    if table is None:
      continue
    if s.startswith('columns:'):
      col_ind = ind
      continue
    if col_ind is not None and ind <= col_ind and not s.startswith('- '):
      col_ind = None
      continue
    if col_ind is not None:
      m = re.match(r'(?:- )?name:\s*[\'"]?([^\'"\s]+)', s) or re.match(r'- \{.*?[{,]\s*name:\s*[\'"]?([^\'",}\s]+)', s)
      item_ind = ind if s.startswith('- ') else ind - 2
      if m and item_ind in (col_ind, col_ind + 2):
        out[table].append(m.group(1))
  return {k: sorted(v) for k, v in out.items()}


def expected_schema(token, full, branch, sha, old):
  """{sha, tables} from the repo's anvil.yaml; reused while the branch tip hasn't moved."""
  if old and old.get('sha') == sha and old.get('tables') is not None:
    return old
  out = {'sha': sha, 'tables': None}
  st, body = gh(token, '/repos/%s/contents/anvil.yaml?ref=%s' % (full, urllib.parse.quote(branch)))
  if st != 200 or not isinstance(body, dict) or not body.get('content'):
    return out
  try:
    import base64
    out['tables'] = tables_of(base64.b64decode(body['content']).decode('utf-8'))
  except Exception as e:
    out['error'] = 'anvil.yaml unreadable: %s' % str(e)[:80]
  return out


def github_facts(token, card, raw):
  """The repo's facts for the card + the raw parts kept for next time (full branch list, expected schema)."""
  full = card.get('repo') or ''
  st, r = gh(token, '/repos/%s' % full)
  if st == 404:
    return {'github_missing': True}, raw, []
  if st != 200 or not isinstance(r, dict):
    return None, raw, ['GitHub answered %s for %s' % (st, full)]
  commits, branch = fetch_commits(token, r['full_name'], r.get('default_branch'))
  branches = fetch_branches(token, r['full_name'], branch, raw.get('branches_raw')) if branch else []
  want_schema = card.get('source') == 'apps.json' and bool(card.get('url'))
  schema_exp = raw.get('schema_exp')
  if branch and commits and want_schema:
    schema_exp = expected_schema(token, r['full_name'], branch, commits[0]['sha'], schema_exp)
  facts = {'desc': r.get('description') or '', 'github_url': r.get('html_url') or '', 'github_missing': False,
           'pushed_at': r.get('pushed_at'), 'commits': commits, 'branch': branch,
           'branches': [b for b in branches if b.get('ahead')], 'branches_merged': [b['name'] for b in branches if not b.get('ahead')]}
  return facts, dict(raw, branches_raw=branches, schema_exp=schema_exp), []


# ---------------------------------------------------------------- live site + SEO

def page_seo(html):
  low = html.lower()
  has = lambda pat: bool(re.search(pat, low))
  return {
    'title': has(r"<title[^>]*>\s*[^<\s]"),
    'description': has(r"<meta[^>]+name=[\"']description[\"'][^>]+content=[\"'][^\"']{20,}")
                   or has(r"<meta[^>]+content=[\"'][^\"']{20,}[\"'][^>]+name=[\"']description"),
    'canonical': has(r"<link[^>]+rel=[\"']canonical"),
    'share': has(r"property=[\"']og:title") and has(r"property=[\"']og:image"),
  }


def check_url(url, seo=False):
  """Does the address answer? With seo=True also look at the page, robots.txt and sitemap.xml."""
  try:
    status, html = http(url, limit=600000 if seo else 8000)
  except Exception as e:  # DNS, timeout, TLS...
    txt = (type(e).__name__ + str(e)).upper()
    if 'CERTIFICATE' in txt or 'SSL' in txt:
      return {'ok': False, 'status': None, 'cert_pending': True, 'checked': now_iso(),
              'error': 'security certificate not ready yet (normal for a new domain; Anvil issues it soon)'}
    return {'ok': False, 'status': None, 'error': type(e).__name__ + ': ' + str(e)[:80], 'checked': now_iso()}
  if not 200 <= status < 400:
    return {'ok': False, 'status': status, 'error': 'HTTP %s' % status, 'checked': now_iso()}
  m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
  out = {'ok': True, 'status': status, 'title': m.group(1).strip()[:80] if m else '', 'checked': now_iso()}
  if seo:
    checks = page_seo(html)
    p = urllib.parse.urlparse(url)
    base = '%s://%s' % (p.scheme, p.netloc)
    for key, path, needle in (('robots', '/robots.txt', 'user-agent'), ('sitemap', '/sitemap.xml', '<urlset|<sitemapindex')):
      try:
        st, body = http(base + path, limit=20000)
        checks[key] = st == 200 and bool(re.search(needle, body.lower()))
      except Exception:
        checks[key] = False
    out['seo'] = {'checks': checks, 'missing': [label for k, label in SEO_CHECKS if not checks.get(k)]}
  return out


def guess_candidates(card):
  """Apps with no link yet: the <name>.anvil.app addresses worth trying (a suggestion; the user confirms it)."""
  if card.get('source') != 'apps.json' or card.get('url'):
    return []
  names = {card.get('key') or '', (card.get('repo') or '').split('/')[-1], (card.get('name') or '').lower().replace(' ', ''),
           (card.get('name') or '').lower().replace(' ', '-')}
  return sorted({'https://%s.anvil.app' % n for n in (re.sub(r'[^a-z0-9-]', '', x.lower()) for x in names) if n})


def live_facts(card):
  url = card.get('url') or ''
  live = check_url(url, seo=True) if url else None
  facts = {'live': live, 'seo': (live or {}).get('seo')}
  hit = None
  for u in guess_candidates(card):
    g = check_url(u)
    if g.get('ok'):
      hit = (u, g.get('title', ''))
      break
  facts['guess_url'], facts['guess_title'] = hit if hit else ('', '')
  return facts


# ---------------------------------------------------------------- schema

def check_schema(url, expected):
  """Live database vs anvil.yaml. state: ok | mismatch | not_installed | error."""
  tables = (expected or {}).get('tables')
  t = now_iso()
  if tables is None:
    return {'state': 'error', 'error': (expected or {}).get('error') or 'no anvil.yaml found on GitHub', 'checked': t}
  if not tables:
    return {'state': 'ok', 'tables': 0, 'checked': t}
  q = urllib.parse.urlencode({'tables': ','.join(sorted(tables))})
  try:
    st, body = http(url.rstrip('/') + '/_/api/schema-check?' + q, limit=300000)
  except Exception as e:
    return {'state': 'error', 'error': type(e).__name__ + ': ' + str(e)[:80], 'checked': t}
  if st == 404:
    return {'state': 'not_installed', 'checked': t}
  live = (_json(body) or {}).get('tables') if st == 200 else None
  if not isinstance(live, dict):
    return {'state': 'error', 'error': 'HTTP %s' % st if st != 200 else 'unexpected answer', 'checked': t}
  missing_tables = sorted(x for x in tables if live.get(x) is None)
  missing = ['%s.%s' % (x, c) for x in sorted(tables) if live.get(x) is not None for c in tables[x] if c not in live[x]]
  extra = ['%s.%s' % (x, c) for x in sorted(tables) if live.get(x) is not None for c in live[x]
           if c not in tables[x] and not (x == 'users' and c in USERS_SERVICE_COLUMNS)]
  bad = missing_tables or missing or extra
  return {'state': 'mismatch' if bad else 'ok', 'tables': len(tables), 'missing_tables': missing_tables,
          'missing_columns': missing, 'extra_columns': extra, 'checked': t}


# ---------------------------------------------------------------- mentions

def needles(card):
  out = []
  host = (urllib.parse.urlparse(card.get('url') or '').hostname or '').lower()
  if host:
    out.append(host[4:] if host.startswith('www.') else host)
  name = (card.get('name') or '').lower()
  if len(name) >= 6:
    out.append(name)
  return out


def mention_texts():
  """{site: lower-case text of its pages} (kept 10 minutes). A site that doesn't answer is left out."""
  if _cache['mentions'] is not None and time.time() - _cache['mentions_at'] < 600:
    return _cache['mentions']
  out = {}
  for site, urls in MENTION_PAGES.items():
    parts = []
    for u in urls:
      try:
        st, txt = http(u, limit=3000000)
        if st == 200:
          parts.append(txt.lower())
      except Exception:
        pass
    if parts:
      out[site] = '\n'.join(parts)
  _cache.update(mentions=out, mentions_at=time.time())
  return out


# ---------------------------------------------------------------- the refresh

def effective(card, state):
  """The card with links typed on the board (state['links']) applied: they win until the PC has copied them."""
  c = dict(card or {})
  for f, v in ((state or {}).get('links') or {}).items():
    if f in LINK_FIELDS:
      c[f] = v
  return c


def _auto(card, facts):
  a = dict(card.get('auto') or {})
  if 'github_missing' in facts:
    a['github'] = not facts['github_missing']
  if 'live' in facts:
    lv = facts['live'] or {}
    host = (urllib.parse.urlparse(card.get('url') or '').hostname or '')
    a['anvil'] = bool(lv.get('ok'))
    a['domain'] = bool(lv.get('ok')) and not host.endswith('.anvil.app')
    seo = facts.get('seo')
    a['seo'] = bool(seo and not seo.get('missing'))
  if 'mentions' in facts:
    for site, on in facts['mentions'].items():
      a[site] = bool(on)
  return a


class Job:
  """One app's checks during a refresh."""

  def __init__(self, card, raw):
    self.card: dict = card
    self.raw: dict = raw
    self.facts: dict = {}
    self.errors: list = []
    self.futures: dict = {}


def refresh(rows, acts):
  """Check these app rows (BATCH at most) and write the facts into their cards. -> list of problems (text)."""
  acts = [a for a in acts if a in ACTIONS]
  token = secret('github_token', 'a read-only GitHub token') if ('github' in acts or 'schema' in acts) else None
  texts = mention_texts() if 'mentions' in acts else {}
  start = time.time()
  ex = concurrent.futures.ThreadPoolExecutor(max_workers=8)
  jobs: dict = {}
  for r in rows:
    card = effective(r['card'], r['state'])
    j = Job(card, dict(card.get('server') or {}))
    jobs[r['key']] = j
    if 'github' in acts and card.get('repo'):
      j.futures['gh'] = ex.submit(github_facts, token, card, j.raw)
    if 'live' in acts:
      j.futures['lv'] = ex.submit(live_facts, card)
  errors = []

  def result(j, name, fut):
    try:
      return fut.result(timeout=max(0.1, DEADLINE - (time.time() - start)))
    except concurrent.futures.TimeoutError:
      j.errors.append("%s: %s check didn't finish in time (kept the last one)" % (j.card.get('name'), name))
    except Exception as e:
      j.errors.append('%s: %s' % (j.card.get('name'), str(e)[:200]))
    return None

  for j in jobs.values():
    if 'gh' in j.futures:
      res = result(j, 'GitHub', j.futures['gh'])
      if res:
        facts, j.raw, errs = res
        j.errors += ['%s: %s' % (j.card.get('name'), e) for e in errs]
        if facts:
          j.facts.update(facts)
    if 'lv' in j.futures:
      res = result(j, 'live site', j.futures['lv'])
      if res:
        j.facts.update(res)
  if 'schema' in acts:
    for j in jobs.values():
      card, raw = j.card, j.raw
      live = j.facts['live'] if 'live' in j.facts else card.get('live')
      if not (card.get('url') and (live or {}).get('ok') and card.get('source') == 'apps.json' and card.get('repo')):
        continue
      exp = raw.get('schema_exp')
      if not exp and 'github' not in acts:  # schema alone: read anvil.yaml for it
        try:
          commits, branch = (card.get('commits') or []), card.get('branch') or 'master'
          exp = expected_schema(token, card['repo'], branch, commits[0].get('sha') if commits else None, None)
          raw['schema_exp'] = exp
        except Exception as e:
          j.errors.append('%s: %s' % (card.get('name'), str(e)[:200]))
          continue
      j.futures['sc'] = ex.submit(check_schema, card['url'], exp)
    for j in jobs.values():
      if 'sc' in j.futures:
        res = result(j, 'database', j.futures['sc'])
        if res:
          j.facts['schema'] = res
  ex.shutdown(wait=False)
  at = now_iso()
  by_key = {r['key']: r for r in rows}
  for key, j in jobs.items():
    if 'mentions' in acts and texts:
      ns = needles(j.card)
      j.facts['mentions'] = {site: any(n in t for n in ns) for site, t in texts.items()} if ns else {}
    r = by_key[key]
    card = dict(r['card'] or {})
    card.update({k: v for k, v in j.facts.items() if k in SERVER_FIELDS})
    card['auto'] = _auto(effective(card, r['state']), j.facts)
    card['server'] = dict(j.raw, at=at, acts=sorted(set((j.raw.get('acts') or [])) | set(acts)))
    r['card'] = card
    errors += j.errors
  if 'mentions' in acts and not texts:
    errors.append("Mentions: arkvital.com and addanapp.com didn't answer (kept the last check)")
  return errors


def keep_server_facts(old, new):
  """A PC push replaces the card, except the facts Addanapp checked itself more recently than the PC did."""
  srv = (old or {}).get('server')
  if not srv:
    return new
  new = dict(new or {})
  new['server'] = srv
  from .apps_core import parse_iso
  pc, here = parse_iso(new.get('facts_at')), parse_iso(srv.get('at'))
  if pc is not None and here is not None and pc >= here:
    return new
  for f in SERVER_FIELDS:
    if f in old:
      new[f] = old[f]
  auto = dict(new.get('auto') or {})
  for a in SERVER_AUTO:
    if a in (old.get('auto') or {}):
      auto[a] = old['auto'][a]
  new['auto'] = auto
  return new


# ---------------------------------------------------------------- links

def save_link(row, field, value):
  """A link typed on the board: shown straight away (state['links']), copied into apps.json by the PC's next update."""
  if field not in LINK_FIELDS:
    raise Exception("Unknown link.")
  value = str(value or '').strip()
  if value and (not re.match(r'^https?://[^\s/]+\.[^\s]+$', value)):
    raise Exception("That doesn't look like a web address (it should start with https://).")
  state = dict(row['state'] or {})
  links = dict(state.get('links') or {})
  links[field] = value
  state['links'] = links
  card = dict(row['card'] or {})
  before = card.get(field) or ''
  card[field] = value
  if field == 'url' and value != before:
    host = urllib.parse.urlparse(value).hostname or ''
    card['url_kind'] = '' if not value else ('anvil' if host.endswith('.anvil.app') else 'domain')
    card['guess_url'], card['guess_title'] = '', ''
    if value:
      card['url_followup'] = ("Live link saved on Addanapp %s. Still to do (an /anvil-update): set url in "
                              "legal-kit/apps/<key>.json, rebuild + install the kit, update README/guide, deploy." % dt.date.today().isoformat())
      live = check_url(value, seo=True)
      card['live'], card['seo'] = live, live.get('seo')
      card['auto'] = _auto(card, {'live': live, 'seo': live.get('seo')})
      srv = dict(card.get('server') or {})
      srv['at'] = now_iso()
      card['server'] = srv
  row.update(card=card, state=state)
  return card.get('live') if field == 'url' else None


# ---------------------------------------------------------------- Prepsto

def prepsto(method, path, body=None, query=None):
  key = secret('prepsto_key', "Claude's Prepsto API key")
  q = {k: v for k, v in (query or {}).items() if v not in (None, '')}
  url = PREPSTO + path + ('?' + urllib.parse.urlencode(q) if q else '')
  try:
    st, txt = http(url, {'Authorization': 'Bearer ' + key, 'Accept': 'application/json'}, method=method, body=body)
  except Exception as e:
    raise Exception("Couldn't reach Prepsto (%s)." % str(e)[:80])
  d = _json(txt) or {}
  if not 200 <= st < 300:
    raise Exception(d.get('error') or "Prepsto answered %s." % st)
  return d


def prepsto_link_id(code):
  if time.time() - _cache['links_at'] > 600 or code not in _cache['links']:
    links = prepsto('GET', '/v1/links').get('links', [])
    _cache.update(links_at=time.time(), links={b.get('code'): b['id'] for b in links if b.get('code')})
  return _cache['links'].get(code, '')


def send_idea(card, text, kind):
  code = card.get('prepsto') or ''
  if not code:
    raise Exception("%s has no Prepsto feedback link." % (card.get('name') or 'This app'))
  text = str(text or '').strip()
  if len(text) < 3:
    raise Exception("Write the idea first.")
  body = {'link': code, 'message': text[:4000], 'kind': kind if kind in ('idea', 'bug', 'question') else 'idea',
          'name': 'App Board', 'tags': ['app-board']}
  if card.get('url'):
    body['page_url'] = card['url']
  t = prepsto('POST', '/v1/tickets', body).get('ticket') or {}
  return {'url': t.get('url'), 'kind': t.get('kind')}


def open_tickets(card):
  """The app's open Prepsto tickets (newest first). -> {code, total, tickets, checked} or with error."""
  code = card.get('prepsto') or ''
  out = {'code': code, 'tickets': [], 'total': 0, 'checked': now_iso()}
  if not code:
    return out
  link = prepsto_link_id(code)
  if not link:
    return dict(out, error="Claude's Prepsto key can't see this app's link (%s) yet." % code)
  d = prepsto('GET', '/v1/tickets', query={'link': link, 'status': 'open', 'limit': 8})
  return dict(out, total=d.get('total', 0),
              tickets=[{k: t.get(k) for k in ('id', 'url', 'kind', 'status', 'message', 'from', 'created', 'priority')}
                       for t in d.get('tickets', [])])


# ---------------------------------------------------------------- YouTube (public numbers, API key)

def youtube_numbers(data):
  """Fresh numbers for the channel and the videos the PC listed (data = the client's 'youtube' doc). Private videos and
  YouTube Analytics need the channel's sign-in, so they keep what the PC's update sent."""
  data = dict(data or {})
  latest = dict(data.get('latest') or {})
  ch = dict(latest.get('channel') or {})
  if not ch.get('id'):
    raise Exception("No YouTube numbers yet: the PC's one-shot update sends the first ones.")
  key = secret('youtube_api_key', 'a Google API key for the YouTube Data API')

  def yt(path, **q):
    q['key'] = key
    st, txt = http(YOUTUBE + path + '?' + urllib.parse.urlencode(q), limit=3000000)
    d = _json(txt) or {}
    if st != 200:
      raise Exception("YouTube answered %s: %s" % (st, ((d.get('error') or {}).get('message') or '')[:160]))
    return d

  items = yt('/channels', part='statistics', id=ch['id']).get('items') or []
  if items:
    s = items[0].get('statistics') or {}
    ch.update(subscribers=int(s.get('subscriberCount', ch.get('subscribers') or 0)), views=int(s.get('viewCount', ch.get('views') or 0)),
              videos=int(s.get('videoCount', ch.get('videos') or 0)), hidden_subs=bool(s.get('hiddenSubscriberCount')))
  videos = [dict(v) for v in latest.get('videos') or []]
  ids = [v['id'] for v in videos if v.get('id')]
  fresh = {}
  for i in range(0, len(ids), 50):
    for it in yt('/videos', part='statistics,status', id=','.join(ids[i:i + 50])).get('items') or []:
      fresh[it['id']] = it
  for v in videos:
    it = fresh.get(v.get('id'))
    if it:
      s = it.get('statistics') or {}
      v.update(views=int(s.get('viewCount', 0)), likes=int(s.get('likeCount', 0)), comments=int(s.get('commentCount', 0)),
               privacy=(it.get('status') or {}).get('privacyStatus') or v.get('privacy'))
  now = dt.datetime.now(dt.timezone.utc)
  latest.update(channel=ch, videos=videos, updated=now.isoformat(timespec='seconds'))
  hist = dict(data.get('history') or {})
  day = dict(hist.get(now.date().isoformat()) or {})
  day.update(subscribers=ch.get('subscribers', 0), views=ch.get('views', 0),
             videos=dict(day.get('videos') or {}, **{v['id']: [v.get('views', 0), v.get('likes', 0), v.get('comments', 0)] for v in videos if v.get('id')}))
  hist[now.date().isoformat()] = day
  data.update(latest=latest, history=hist)
  return data
