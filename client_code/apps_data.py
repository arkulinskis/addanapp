"""Apps (#apps, #app/<key>): a client's app portfolio board. Shared client state for its pages and views:

    load(force)            the whole board in one server call (apps_board), kept while you move between views
    client_id()            which client's portfolio a consultant is looking at (remembered in this browser)
    tick / set_state / set_posted / add_change   change something; the server sends the app back redrawn
    queue(kind, key, args) work for the user's PC (refresh, link, idea, ideas, branches, schema, yt)
    listen(fn)             the open page redraws when something changed (one listener: the current page)
Facts come from the PC worker (APP_MAKER/board/addanapp_link.py); see server_code/apps_core.py.
"""
import json

import anvil.js
from anvil.js import window

from . import state, ui

VIEWS = [('board', 'Board', 'columns'), ('grid', 'Checklist grid', 'grid'), ('posts', 'Posts', 'message'),
         ('bizdev', 'Biz dev', 'target'), ('money', 'Money', 'receipt'), ('youtube', 'YouTube', 'play'),
         ('dossier', 'Dossiers', 'file'), ('notes', 'Notifications', 'bell')]
MODULE_VIEWS = ('posts', 'bizdev', 'money', 'youtube')
STAGE_COLOR = {'build': '--ap-build', 'deploy': '--ap-deploy', 'test': '--ap-test', 'promote': '--ap-promote',
               'standard': '--ap-standard', 'components': '--ap-components', 'launched': '--ap-launched', 'parked': '--ap-parked'}
_d: dict = {"board": None, "listener": None, "q": "", "copied": set()}


def sget(key, default=None):
    """A dict or list remembered in this browser (stored as JSON text, so it comes back as Python, not a JS object)."""
    raw = state.store_get(key, None)
    if not isinstance(raw, str):
        return default
    try:
        return json.loads(raw)
    except Exception:
        return default


def sset(key, value):
    state.store_set(key, json.dumps(value))


def color(stage):
    return "var(%s)" % STAGE_COLOR.get(stage, '--ap-build')


def client_id():
    return state.store_get('apps.client', None)


def set_client(cid):
    state.store_set('apps.client', cid or None)
    _d["board"] = None


def board():
    return _d["board"]


def load(force=False):
    """The board, from cache unless force. None when it couldn't load (the message was shown)."""
    if _d["board"] is not None and not force:
        return _d["board"]
    res = ui.call('apps_board', client_id())
    if res is ui.FAIL:
        return None
    _d["board"] = res
    _d["full"] = {}  # apps_project answers (posts, video kits) are fetched again after a reload
    return res


def call(fn, *args):
    return ui.call(fn, *args, client_id=client_id())


def listen(fn):
    _d["listener"] = fn


def changed(key=None):
    fn = _d["listener"]
    if fn is not None:
        fn(key)


def query():
    return _d["q"]


def set_query(q):
    _d["q"] = (q or '').strip().lower()


def visible():
    b = board() or {}
    q = _d["q"]
    out = []
    for p in b.get('projects') or []:
        if not q or q in ' '.join(str(p.get(k) or '') for k in ('name', 'key', 'desc', 'url', 'repo')).lower():
            out.append(p)
    return out


def project(key):
    for p in (board() or {}).get('projects') or []:
        if p['key'] == key:
            return p
    return None


def biz_key(key):
    return key[3:] if key.startswith('gh:') else key


def project_by_biz(k):
    for p in (board() or {}).get('projects') or []:
        if biz_key(p['key']) == k:
            return p
    return None


def lane_name(stage):
    for ln in (board() or {}).get('lanes') or []:
        if ln['id'] == stage:
            return ln['name']
    return stage


def items():
    return (board() or {}).get('items') or []


def put(res):
    """A server answer {project, stats, notes}: swap the app in, keep the rest."""
    b = board()
    if b is None or res is ui.FAIL or not res:
        return
    p = res.get('project')
    if p:
        b['projects'] = [p if x['key'] == p['key'] else x for x in b['projects']]
    for k in ('stats', 'notes'):
        if k in res:
            b[k] = res[k]


def tick(key, item_id):
    res = call('apps_tick', key, item_id)
    if res is not ui.FAIL:
        put(res)
        changed(key)
    return res


def set_state(key, changes, quiet=False):
    res = call('apps_set_state', key, changes)
    if res is not ui.FAIL:
        put(res)
        if not quiet:
            changed(key)
    return res


def set_posted(key, post_id, on):
    res = set_state(key, {'posted': {post_id: bool(on)}})
    if res is not ui.FAIL:
        state.toast("Ticked as posted" if on else "Unticked", "ok")
    return res


def add_change(key, text):
    res = call('apps_add_change', key, text)
    if res is not ui.FAIL:
        put(res)
        changed(key)
        state.toast("Queued for Claude as a request", "ok")
    return res


WHAT = {'refresh': 'Refresh', 'link': 'Saving the link', 'idea': 'Sending the idea', 'ideas': 'Loading its tickets',
        'branches': 'Checking branches', 'schema': 'Checking the database', 'yt': 'Updating YouTube numbers'}


def queue(kind, key=None, args=None):
    """Ask the PC to do something. The page polls until it's done (Pages/Apps, Pages/AppDetail)."""
    job = call('apps_queue', kind, key, args)
    if job is ui.FAIL:
        return None
    b = board()
    if b is not None:
        b['jobs'] = [j for j in b.get('jobs') or [] if j['id'] != job['id']] + [job]
        online = (b.get('worker') or {}).get('online')
    else:
        online = True
    state.toast(WHAT.get(kind, 'Job') + (": your PC is on it." if online else
                                         ": waiting for your PC (it runs when the PC link is on)."), "ok")
    changed()
    return job


def jobs():
    return (board() or {}).get('jobs') or []


def pending(key=None):
    return [j for j in jobs() if j['status'] in ('queued', 'running') and (key is None or j.get('key') == key)]


def copy(text, what="Copied"):
    try:
        ok = window.aa.copy(text or '')
    except Exception:
        ok = False
    state.toast((what + ": paste it where you need it") if ok else "Copy didn't work: select the text instead", "ok" if ok else "error")
    return ok


def js():
    """The drawing engine (theme/assets/apps.js)."""
    return window.apps


def dismissed():
    return (board() or {}).get('dismissed') or {}


def is_dismissed(n):
    return dismissed().get(n['id']) == n['sig']


def active_notes():
    return [n for n in (board() or {}).get('notes') or [] if not is_dismissed(n)]


def dismiss(n):
    d = call('apps_dismiss', n['id'], n['sig'])
    if d is not ui.FAIL and board() is not None:
        board()['dismissed'] = d
        changed()


def links(p):
    """The app's outside links as [{label, href, title}]."""
    out = []
    if p.get('url'):
        out.append({'label': 'Live on Anvil ↗' if p.get('url_kind') == 'anvil' else 'Live ↗', 'href': p['url'], 'title': p['url']})
    if p.get('anvil_editor'):
        out.append({'label': 'Anvil editor ↗', 'href': p['anvil_editor']})
    if p.get('github_url'):
        out.append({'label': 'GitHub ↗', 'href': p['github_url']})
    y = p.get('youtube')
    if y and y.get('url'):
        note = '' if y.get('public') else (' (private)' if y.get('note') == 'private' else ' (held)')
        out.append({'label': 'YouTube' + note + ' ↗', 'href': y['url'],
                    'title': 'Pitch video' + (', published ' + y['published'] if y.get('published') else '')})
    return out


def media_url(m):
    """A Media object's URL for an <img>."""
    if m is None:
        return ''
    try:
        return m.url or ''
    except Exception:
        try:
            return m.get_url() or ''
        except Exception:
            return ''


def segs(p):
    return [[(p['items'].get(it['id']) or {}).get('v', 'todo'), color(it['phase']), it['label']] for it in items()]


def live_text(p):
    lv = p.get('live')
    if not p.get('url'):
        return 'No live address yet.'
    if not lv:
        return 'Not checked yet.'
    kind = 'Anvil address' if p.get('url_kind') == 'anvil' else 'Custom domain'
    from . import apps_fmt
    if lv.get('ok'):
        return '✅ %s answers (%s)%s · checked %s' % (kind, lv.get('status'), ': “%s”' % lv['title'] if lv.get('title') else '',
                                                   apps_fmt.ago(lv.get('checked')))
    return '❌ %s not answering (%s) · checked %s' % (kind, lv.get('error') or lv.get('status'), apps_fmt.ago(lv.get('checked')))


def dom(component):
    return anvil.js.get_dom_node(component)
