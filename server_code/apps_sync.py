"""Apps: the HTTP API for the PC worker and Claude (APP_MAKER/board/addanapp_link.py and board_cli.py).

    POST|GET <origin>/_/api/apps/v1/<action>      Authorization: Bearer <PC link key>      JSON in, JSON out

The key lives only on the user's PC (~/.addanapp/apps-link.json); this file keeps its SHA-256, never the key. The
key may act for any portfolio, so every call names the client by email ("client" in the body or the query).

  hello    who am I, heartbeat                         push     app facts, docs, steps (creates the client if new)
  media    one screenshot / thumbnail (base64)         pull     what people changed here: states, changes, outreach
  board    the board as the pages see it (no media)    state    set checks / notes / parked / posted (board_cli tick)
  changes  open "Changes for Claude"                   change   queue a change (board_cli add)
  done     Claude finished a change: note + Ready for review
  claim    the next job for the PC (and a heartbeat)   finish   a job's result
"""
import base64
import hashlib
import hmac
import json
import random

import anvil
import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables

from . import apps_core as core
from .api_admin import update_request_as
from .api_apps import job_dict, OUTREACH_FIELDS
from .common import AVATAR_COLORS, admins, by_id, clean, now, rid

# SHA-256 of the PC link key (python APP_MAKER/board/addanapp_link.py key shows how to make a new one).
KEY_HASHES = {'ea367d88526b539c95ec3eb04ccfa6b83542d0005c826a1cbee0e333b9298738'}
# Accepted only when the app runs on this PC's local App Server (tests), never on addanapp.com.
LOCAL_TEST_KEY = 'aal_local_test_key'
MEDIA_FIELDS = ('hero', 'hero_phone', 'thumb')
MEDIA_TYPES = ('image/png', 'image/jpeg', 'image/webp')
MAX_MEDIA = 3 * 1024 * 1024


def _json(status, data):
  return anvil.server.HttpResponse(status, json.dumps(data, default=str, ensure_ascii=False),
                                   headers={'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store'})


def _local():
  try:
    origin = anvil.server.get_app_origin() or ''
  except Exception:
    return False
  host = origin.split('://', 1)[-1].split('/', 1)[0].split(':', 1)[0]
  return host in ('localhost', '127.0.0.1')


def key_ok(auth):
  auth = str(auth or '')
  if not auth.lower().startswith('bearer '):
    return False
  key = auth[7:].strip()
  digest = hashlib.sha256(key.encode('utf-8')).hexdigest()
  if any(hmac.compare_digest(digest, h) for h in KEY_HASHES):
    return True
  return _local() and hmac.compare_digest(key, LOCAL_TEST_KEY)


def _body():
  req = anvil.server.request
  try:
    b = req.body_json
    b = b() if hasattr(b, '__call__') else b
  except Exception:
    b = None
  return b if isinstance(b, dict) else {}


def find_client(email, create=None):
  """The portfolio's client by email (case-insensitive). create = {name, company} makes the account when missing:
  it has no password, so its owner sets one with "Forgot your password?"."""
  email = clean(email, 200).lower()
  if '@' not in email:
    raise ValueError("Name the client by email.")
  for u in app_tables.users.search():
    if (u['email'] or '').strip().lower() == email:
      return u
  if not create:
    raise ValueError("No account with that email.")
  t = now()
  return app_tables.users.add_row(email=email, enabled=True, confirmed_email=True, signed_up=t, created=t,
                                  name=clean(create.get('name') or 'Client', 80), company=clean(create.get('company'), 120),
                                  role='client', is_admin=False, is_demo=False, email_notifications=True,
                                  color=random.choice(AVATAR_COLORS))


def _heartbeat(client, host=''):
  core.set_doc(client, 'worker', data={'seen': now().isoformat(), 'host': clean(host, 80)})


def _state_seed(seed):
  return {k: seed[k] for k in core.MANAGED_STATE if k in seed}


# ---------------------------------------------------------------- actions

def a_hello(b, client):
  _heartbeat(client, b.get('host', ''))
  return {'ok': True, 'client': {'id': rid(client), 'name': client['name'], 'company': client['company']},
          'apps': len(app_tables.app_projects.search(client=client))}


def a_push(b, client):
  """projects: [{key, name, card, promo?, video_kit?, state_seed?}]; keep: every key (others are removed);
  meta: steps etc.; docs: [{name, text?, data?}]."""
  t = now()
  added = updated = 0
  for p in b.get('projects') or []:
    key = clean(p.get('key'), 120)
    if not key:
      continue
    r = app_tables.app_projects.get(client=client, key=key)
    ch: dict = {'name': clean(p.get('name') or key, 120), 'updated': t}
    for col in ('card', 'promo', 'video_kit'):
      if col in p:
        ch[col] = p[col]
    if r is None:
      seed = _state_seed(p.get('state_seed') or {})
      app_tables.app_projects.add_row(client=client, key=key, state=seed, state_updated=t, media_v={}, **ch)
      added += 1
    else:
      if p.get('state_seed') and not r['state']:
        ch['state'] = _state_seed(p['state_seed'])
      r.update(**ch)
      updated += 1
  removed = 0
  if isinstance(b.get('keep'), list):
    keep = set(str(k) for k in b['keep'])
    for r in app_tables.app_projects.search(client=client):
      if r['key'] not in keep:
        r.delete()
        removed += 1
  if isinstance(b.get('meta'), dict):
    m = dict(core.meta(client))
    m.update(b['meta'])
    core.set_doc(client, 'meta', data=m)
  for d in b.get('docs') or []:
    name = clean(d.get('name'), 200)
    if name and name not in ('dismissed', 'worker', 'outreach'):
      core.set_doc(client, name, data=d.get('data'), text=d.get('text'))
  if isinstance(b.get('outreach_rows'), list):  # rows the PC has that Addanapp doesn't (union, no deletes)
    log = dict(core.doc_data(client, 'outreach', {}) or {})
    rows = list(log.get('rows') or [])
    have = set(json.dumps(r) for r in rows)
    for row in b['outreach_rows']:
      vals = [clean(x, 600) for x in list(row)[:len(OUTREACH_FIELDS)]]
      vals += [''] * (len(OUTREACH_FIELDS) - len(vals))
      if json.dumps(vals) not in have:
        rows.append(vals)
        have.add(json.dumps(vals))
    log['rows'] = rows
    log.setdefault('header', list(OUTREACH_FIELDS))
    core.set_doc(client, 'outreach', data=log)
  return {'ok': True, 'added': added, 'updated': updated, 'removed': removed,
          'media_v': {r['key']: r['media_v'] or {} for r in app_tables.app_projects.search(client=client)}}


def a_media(b, client):
  r = app_tables.app_projects.get(client=client, key=clean(b.get('key'), 120))
  field, ctype = b.get('field'), b.get('type') or 'image/jpeg'
  if r is None:
    raise ValueError("No such app.")
  if field not in MEDIA_FIELDS or ctype not in MEDIA_TYPES:
    raise ValueError("field must be hero, hero_phone or thumb (png, jpeg or webp).")
  if not b.get('data'):
    r[field] = None
  else:
    raw = base64.b64decode(b['data'])
    if len(raw) > MAX_MEDIA:
      raise ValueError("Image too big (3 MB at most).")
    ext = {'image/png': 'png', 'image/jpeg': 'jpg', 'image/webp': 'webp'}[ctype]
    r[field] = anvil.BlobMedia(ctype, raw, name='%s-%s.%s' % (r['key'].replace(':', '_'), field, ext))
  mv = dict(r['media_v'] or {})
  mv[field] = clean(b.get('v'), 80)
  r['media_v'] = mv
  return {'ok': True}


def _open_changes(client, todo_only=False):
  out = []
  for r in app_tables.requests.search(tables.order_by('created', ascending=True), client=client):
    if not r['project'] or r['status'] in core.DONE_STATUSES:
      continue
    if todo_only and r['status'] not in core.TODO_STATUSES:
      continue
    notes = [{'kind': n['kind'], 'body': n['body'] or '', 'created': n['created'], 'internal': bool(n['internal'])}
             for n in app_tables.notes.search(tables.order_by('created', ascending=True), request=r) if n['kind'] != 'status']
    out.append({'id': rid(r), 'ref': r['ref'], 'key': r['project'], 'title': r['title'], 'status': r['status'],
                'description': r['description'] or '', 'created': r['created'], 'notes': notes})
  return out


def a_pull(b, client):
  return {'states': {r['key']: r['state'] or {} for r in app_tables.app_projects.search(client=client)},
          'changes': _open_changes(client), 'outreach': core.doc_data(client, 'outreach', {}) or {},
          'dismissed': core.doc_data(client, 'dismissed', {}) or {}}


def a_board(b, client):
  vs, m = core.views(client, full=bool(b.get('full')), media=False)
  return {'projects': vs, 'phases': core.phases_of(m), 'stats': core.stats(vs), 'notes': core.notes(vs, m),
          'refreshed_at': m.get('refreshed_at'), 'errors': m.get('errors') or []}


def a_state(b, client):
  r = app_tables.app_projects.get(client=client, key=clean(b.get('key'), 120))
  if r is None:
    raise ValueError("No such app.")
  s = dict(r['state'] or {})
  st = b.get('set') or {}
  if isinstance(st.get('checks'), dict):
    checks = dict(s.get('checks') or {})
    for k, v in st['checks'].items():
      if v in ('done', 'na', 'todo'):
        checks[str(k)] = v
      elif v is None:
        checks.pop(str(k), None)
    s['checks'] = checks
  if 'notes' in st:
    s['notes'] = clean(st['notes'], 20000)
  if 'parked' in st:
    s['parked'] = bool(st['parked'])
  if isinstance(st.get('posted'), dict):
    posted = dict(s.get('posted') or {})
    for k, v in st['posted'].items():
      if v:
        posted[str(k)] = str(v)
      else:
        posted.pop(str(k), None)
    s['posted'] = posted
  r.update(state=s, state_updated=now())
  return {'ok': True, 'state': s}


def a_changes(b, client):
  return {'changes': _open_changes(client, todo_only=not b.get('all'))}


def _consultant():
  a = admins()
  if not a:
    raise ValueError("Addanapp has no consultant account yet.")
  return a[0]


def a_change(b, client):
  from .api_client import create_request_row
  key = clean(b.get('key'), 120)
  r = app_tables.app_projects.get(client=client, key=key)
  if r is None:
    raise ValueError("No such app.")
  text = clean(b.get('text'), 8000)
  if len(text) < 10:
    raise ValueError("Describe the change in a sentence or two.")
  u = _consultant()
  first = text.split('\n', 1)[0].strip()
  req = create_request_row(client, {'title': (r['name'] or key) + ': ' + first[:90], 'description': text, 'kind': 'change',
                                    'project': key}, u)
  update_request_as(u, req, {'status': 'in_progress'})
  return {'ok': True, 'id': rid(req), 'ref': req['ref']}


def a_done(b, client):
  """Claude finished a change: a progress note (what was done) and Ready for review (or another status)."""
  req = by_id(app_tables.requests, b.get('id'))
  if req is None or req['client'] != client:
    raise ValueError("No such change.")
  status = b.get('status') or 'review'
  if status not in ('review', 'in_progress', 'on_hold', 'delivered', 'declined'):
    raise ValueError("Unknown status.")
  summary = clean(b.get('summary'), 8000)
  note = {'kind': 'validated' if status == 'review' else 'update', 'body': summary} if summary else None
  update_request_as(_consultant(), req, {'status': status}, note)
  return {'ok': True, 'status': req['status']}


def a_claim(b, client):
  _heartbeat(client, b.get('host', ''))
  for j in app_tables.app_jobs.search(tables.order_by('created', ascending=True), client=client, status='queued'):
    j.update(status='running', started=now())
    return {'job': job_dict(j)}
  # a job left "running" for 15 minutes: the PC stopped; offer it again
  for j in app_tables.app_jobs.search(client=client, status='running'):
    if j['started'] is not None and (now() - j['started']).total_seconds() > 900:
      j.update(status='queued')
  return {'job': None}


def a_finish(b, client):
  j = by_id(app_tables.app_jobs, b.get('id'))
  if j is None or j['client'] != client:
    raise ValueError("No such job.")
  j.update(status='done' if b.get('ok') else 'failed', finished=now(), result=b.get('result') or {},
           error=clean(b.get('error'), 2000))
  return {'ok': True}


ACTIONS = {'hello': a_hello, 'push': a_push, 'media': a_media, 'pull': a_pull, 'board': a_board, 'state': a_state,
           'changes': a_changes, 'change': a_change, 'done': a_done, 'claim': a_claim, 'finish': a_finish}


@anvil.server.http_endpoint('/apps/v1/:action', methods=['GET', 'POST'])
def apps_api(action, **kw):
  req = anvil.server.request
  headers = {str(k).lower(): v for k, v in (req.headers or {}).items()}
  if not key_ok(headers.get('authorization')):
    return _json(401, {'error': 'Missing or wrong key.'})
  fn = ACTIONS.get(action)
  if fn is None:
    return _json(404, {'error': 'Unknown action.'})
  b = _body()
  query = getattr(req, 'query_params', None) or {}
  email = b.get('client') or query.get('client') or ''
  try:
    client = find_client(email, create=b.get('create') if action in ('hello', 'push') else None)
    return _json(200, fn(b, client))
  except ValueError as e:
    return _json(400, {'error': str(e)})
