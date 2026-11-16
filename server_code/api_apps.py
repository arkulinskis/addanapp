"""Apps: the browser's API for a client's app portfolio board (#apps, #app/<key>). See apps_core.py for the data.

Who may see a portfolio: its client and Addanapp consultants. Consultants pick the client (client_id); a client always
sees their own. Facts come from two places: Refresh here (apps_refresh.py: GitHub, live site + SEO, schema,
mentions, Prepsto, YouTube public numbers; only when someone presses it) and the PC's one-shot update (apps_sync.py:
audit, legal, screenshots, posts, plans, new apps). Here people tick steps, write notes and ask Claude for changes.
"""
import datetime

import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables

from . import apps_core as core
from . import apps_refresh as rf
from .common import current_user, by_id, rid, clean, now, add_note, touch
from .api_client import create_request_row



def _client(client_id=None):
  """-> (viewer, client row). Consultants may open any client's portfolio; clients only their own."""
  u = current_user()
  touch(u)
  if not u['is_admin']:
    if not core.has_portfolio(u):
      raise Exception("There's no app portfolio in this workspace yet.")
    return u, u
  if client_id:
    c = by_id(app_tables.users, client_id)
    if c is None:
      raise Exception("That client doesn't exist.")
    return u, c
  owners = sorted(core.portfolio_clients(), key=lambda x: -x[1])
  if not owners:
    raise Exception("No client has an app portfolio yet. Send one from the PC: python APP_MAKER/board/addanapp_link.py sync")
  return u, owners[0][0]


def _row(client, key):
  r = app_tables.app_projects.get(client=client, key=str(key or ''))
  if r is None:
    raise Exception("That app isn't in this portfolio.")
  return r


def _summary(client):
  return {'id': rid(client), 'name': client['company'] or client['name'] or 'Client', 'person': client['name'] or ''}


@anvil.server.callable
def apps_board(client_id=None):
  """Everything the #apps views need in one go (screenshots come as Media)."""
  u, client = _client(client_id)
  vs, m = core.views(client)
  phases = core.phases_of(m)
  out = {
    'client': _summary(client), 'is_admin': bool(u['is_admin']),
    'clients': sorted([dict(_summary(c), n=n) for c, n in core.portfolio_clients()], key=lambda x: x['name'].lower()) if u['is_admin'] else [],
    'phases': phases, 'lanes': core.lanes(phases), 'items': core.flat_items(phases), 'short': core.SHORT,
    'projects': vs, 'stats': core.stats(vs), 'notes': core.notes(vs, m),
    'note_types': [{'id': i, 'name': n, 'desc': d, 'icon': core.NOTE_ICONS.get(i, 'bell')} for i, n, d in core.NOTE_TYPES],
    'dismissed': core.doc_data(client, 'dismissed', {}) or {},
    'refreshed_at': core.latest(m.get('refreshed_at'), m.get('server_refreshed_at')),
    'pc_at': m.get('pushed_at') or '', 'errors': core.errors_of(m), 'money_meta': m.get('money_meta') or {},
    'actions': rf.ACTIONS, 'all_default': list(rf.ACTIONS), 'batch': rf.BATCH,
    'modules': m.get('modules') or list(core.MODULES), 'seo_labels': core.SEO_LABELS, 'std_labels': core.STD_LABELS,
  }
  return out


@anvil.server.callable
def apps_project(key, client_id=None):
  """One app in full: the board's view plus recent commits, past changes, its posts and video kit."""
  _u, client = _client(client_id)
  r = _row(client, key)
  m = core.meta(client)
  v = core.view(r, core.phases_of(m), core.changes_by_key(client), full=True)
  v['promo'] = r['promo'] or {}
  v['video_kit'] = r['video_kit'] or {}
  v['ideas'] = ((r['card'] or {}).get('server') or {}).get('ideas')
  return v


def _redraw(client, r):
  m = core.meta(client)
  ch = core.changes_by_key(client)
  v = core.view(r, core.phases_of(m), ch)
  vs, _m = core.views(client)
  return {'project': v, 'stats': core.stats(vs), 'notes': core.notes(vs, m)}


@anvil.server.callable
def apps_tick(key, item_id, value=None, client_id=None):
  """Click a step: empty -> done -> not needed -> empty (or set value). Returns the redrawn app."""
  _u, client = _client(client_id)
  r = _row(client, key)
  m = core.meta(client)
  ids = [it['id'] for it in core.flat_items(core.phases_of(m))]
  if item_id not in ids:
    raise Exception("Unknown step.")
  state = dict(r['state'] or {})
  checks = dict(state.get('checks') or {})
  if value not in ('todo', 'done', 'na'):
    cur, _auto = core.item_value(state, core.auto_of(r['card'] or {}, state), item_id)
    value = {'todo': 'done', 'done': 'na'}.get(cur, 'todo')
  checks[item_id] = value
  state['checks'] = checks
  r.update(state=state, state_updated=now())
  return _redraw(client, r)


@anvil.server.callable
def apps_set_state(key, changes, client_id=None):
  """Notes, park / un-park, and Posted ticks ({'posted': {'li3': True}})."""
  _u, client = _client(client_id)
  r = _row(client, key)
  state = dict(r['state'] or {})
  changes = changes or {}
  if 'notes' in changes:
    state['notes'] = clean(changes.get('notes'), 20000)
  if 'parked' in changes:
    state['parked'] = bool(changes.get('parked'))
  if isinstance(changes.get('posted'), dict):
    posted = dict(state.get('posted') or {})
    for pid, on in changes['posted'].items():
      pid = str(pid)[:20]
      if on:
        posted[pid] = on if isinstance(on, str) else now().date().isoformat()
      else:
        posted.pop(pid, None)
    state['posted'] = posted
  r.update(state=state, state_updated=now())
  return _redraw(client, r)


@anvil.server.callable
def apps_add_change(key, text, client_id=None):
  """"Changes for Claude": a request on the app (kind 'change', project = key), straight to In progress (no quote)."""
  u, client = _client(client_id)
  r = _row(client, key)
  text = clean(text, 8000)
  if len(text) < 10:
    raise Exception("Describe the change in a sentence or two.")
  first = text.split('\n', 1)[0].strip()
  title = (r['name'] or key) + ': ' + (first[:90] + ('…' if len(first) > 90 else ''))
  req = create_request_row(client, {'title': title, 'description': text, 'kind': 'change', 'project': key}, u)
  old = req['status']
  req.update(status='in_progress', updated=now(), last_activity=now())
  add_note(req, u, 'status', "Queued for Claude from the Apps board", status_from=old, status_to='in_progress')
  return dict(_redraw(client, r), request_id=rid(req))


@anvil.server.callable
def apps_refresh(keys, actions, first=False, last=False, whole=False, client_id=None):
  """Check these apps now, from here (rf.BATCH at a time; the browser sends the batches one after another).
  first: a new run (its problems replace the last run's); whole: every app (sets the board's "checked" time at the end)."""
  _u, client = _client(client_id)
  acts = [a for a in (actions or []) if a in rf.ACTIONS]
  if not acts:
    raise Exception("Tick at least one thing to check.")
  keys = [str(k) for k in (keys or [])][:rf.BATCH]
  rows = [_row(client, k) for k in keys]
  errors = rf.refresh(rows, acts)
  m = dict(core.meta(client))
  m['server_errors'] = ([] if first else list(m.get('server_errors') or [])) + errors
  if whole and last:
    m['server_refreshed_at'] = rf.now_iso()
  core.set_doc(client, 'meta', data=m)
  phases, ch = core.phases_of(m), core.changes_by_key(client)
  vs, _m = core.views(client)
  return {'projects': [core.view(r, phases, ch) for r in rows], 'errors': errors, 'stats': core.stats(vs),
          'notes': core.notes(vs, m), 'all_errors': core.errors_of(m),
          'refreshed_at': core.latest(m.get('refreshed_at'), m.get('server_refreshed_at'))}


@anvil.server.callable
def apps_save_link(key, field, value, client_id=None):
  """The live address or Anvil editor link, typed on the board. Shown at once; the PC's next update writes apps.json."""
  _u, client = _client(client_id)
  r = _row(client, key)
  rf.save_link(r, field, clean(value, 300))
  return _redraw(client, r)


@anvil.server.callable
def apps_send_idea(key, text, kind='idea', client_id=None):
  """An improvement idea (or bug / question) for the app's Prepsto inbox, sent with Claude's Prepsto key."""
  _u, client = _client(client_id)
  r = _row(client, key)
  return rf.send_idea(r['card'] or {}, clean(text, 4000), kind)


@anvil.server.callable
def apps_tickets(key, client_id=None):
  """The app's open Prepsto tickets, kept on the card until the next check."""
  _u, client = _client(client_id)
  r = _row(client, key)
  card = dict(r['card'] or {})
  ideas = rf.open_tickets(card)
  srv = dict(card.get('server') or {})
  srv['ideas'] = ideas
  card['server'] = srv
  r['card'] = card
  return ideas


@anvil.server.callable
def apps_dismiss(note_id, sig, client_id=None):
  """Hide a notification until something about it changes (or bring it back)."""
  _u, client = _client(client_id)
  d = dict(core.doc_data(client, 'dismissed', {}) or {})
  note_id = str(note_id)[:200]
  if d.get(note_id) == sig:
    d.pop(note_id, None)
  else:
    d[note_id] = str(sig)[:4000]
  core.set_doc(client, 'dismissed', data=d)
  return d


@anvil.server.callable
def apps_bizdev(name='README', client_id=None):
  """The biz dev view: ranked plans (index), one document as HTML, or the outreach log."""
  _u, client = _client(client_id)
  idx = core.doc_data(client, 'bizdev/index', {}) or {}
  apps = sorted(idx.get('apps') or [], key=lambda a: a.get('rank') or 999)
  log = core.doc_data(client, 'outreach', {}) or {}
  rows = log.get('rows') or []
  name = str(name or 'README').replace('.', '/')
  if not core.DOC_NAME.fullmatch(name):
    name = 'README'
  out = {'apps': apps, 'log_count': len(rows), 'name': name, 'html': '', 'rows': [], 'missing': False}
  if name == 'outreach-log':
    out['rows'] = rows
  else:
    text = core.doc_text(client, 'bizdev/' + name)
    out['missing'] = not text
    out['html'] = core.markdown(text, name)
  return out


@anvil.server.callable
def apps_bizdev_plan(biz_key, client_id=None):
  """One app's plan (without its title) as HTML + its outreach rows, for the dossier."""
  _u, client = _client(client_id)
  text = core.doc_text(client, 'bizdev/apps/' + str(biz_key))
  if text.startswith('# '):
    text = text.split('\n', 1)[1] if '\n' in text else ''
  rows = (core.doc_data(client, 'outreach', {}) or {}).get('rows') or []
  return {'html': core.markdown(text, 'apps/' + str(biz_key)) if text else '', 'rows': rows}


OUTREACH_FIELDS = ('date', 'app', 'channel', 'who', 'message_type', 'result', 'next_step', 'notes')


@anvil.server.callable
def apps_add_outreach(row, client_id=None):
  """One line in the outreach log (the PC copies it into bizdev/outreach-log.csv)."""
  _u, client = _client(client_id)
  row = row or {}
  vals = [clean(row.get(k), 600) for k in OUTREACH_FIELDS]
  if not vals[0]:
    vals[0] = now().date().isoformat()
  try:
    datetime.date.fromisoformat(vals[0])
  except ValueError:
    raise Exception("The date should look like 2026-11-11.")
  if not any(vals[1:]):
    raise Exception("Fill in at least the app, channel or who.")
  log = dict(core.doc_data(client, 'outreach', {}) or {})
  rows = list(log.get('rows') or [])
  rows.append(vals)
  log['rows'] = rows
  log.setdefault('header', list(OUTREACH_FIELDS))
  core.set_doc(client, 'outreach', data=log)
  return {'rows': rows}


@anvil.server.callable
def apps_youtube_update(client_id=None):
  """Fresh public numbers from YouTube (an API key: views, likes, comments, subscribers). Analytics stay the PC's."""
  _u, client = _client(client_id)
  d = core.doc_row(client, 'youtube')
  data = rf.youtube_numbers((d['data'] if d is not None else None) or {})
  core.set_doc(client, 'youtube', data=data)
  return apps_youtube(client_id)


@anvil.server.callable
def apps_youtube(client_id=None):
  """The channel numbers: from the PC's update (youtube/stats.py, with Analytics) and Update numbers here."""
  _u, client = _client(client_id)
  d = core.doc_row(client, 'youtube')
  data = (d['data'] if d is not None else None) or {}
  return dict(data, updated_doc=d['updated'] if d is not None else None)
