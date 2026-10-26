from ._anvil_designer import AdminTemplate
from anvil import *

from .. import ui, state
from ..ui import esc
from ..icons import icon
from ..Portal import row_html
from ..NewRequest import request_form_html, collect, validate

EMPTY_COL = '<p class="tiny muted" style="margin:4px">Nothing here</p>'
BOARD_COLS = ['new','scoping', 'quoted', 'in_progress', 'review', 'delivered']
TABS = [('requests', 'Requests', '#admin'), ('clients', 'Clients', '#admin/clients'), ('leads', 'Leads', '#admin/leads'),
        ('tools', 'Tools', '#admin/tools')]
LEAD_STATUSES = [('new', 'New'), ('contacted', 'Contacted'), ('won', 'Won'), ('lost', 'Lost'), ('archived', 'Archived')]


class Admin(AdminTemplate):
  """Consultant console."""

  def __init__(self, tab='requests', **properties):
    self.init_components(**properties)
    self.tab = tab if tab in [t[0] for t in TABS] else 'requests'
    self.view = 'list'
    self.filter = 'open'
    self.client_filter = ''
    self.search = ''
    self.data = None
    c = state.counts or {}
    tabs = ''
    for key, label, href in TABS:
      n = c.get('unread', 0) if key == 'requests' else (c.get('leads', 0) if key == 'leads' else 0)
      cnt = f'<span class="count">{n}</span>' if n else ''
      tabs += f'<a href="{href}" class="{"on" if key == self.tab else ""}">{label}{cnt}</a>'
    self.html = f'''
    <div class="app-page"><div class="aa-wrap">
      <div class="page-head"><div><div class="eyebrow">Consultant console</div><h1 class="js-title">Requests</h1>
        <p class="js-sub"></p></div><div class="actions js-actions"></div></div>
      <div class="tabs-line">{tabs}</div>
      <div class="js-root"></div>
    </div></div>'''
    ui.bind(self, {
      'filter': self._set_filter, 'view': self._set_view, 'new-for': self.new_for_client,
      'client-req': self._client_requests, 'toggle-admin': self._toggle_admin, 'toggle-enabled': self._toggle_enabled,
      'lead-del': self._lead_delete, 'seed': lambda a: self._tool('admin_seed_demo'),
      'clear': lambda a: self._tool('admin_clear_demo'), 'open': lambda rid: state.go('r/' + rid),
    })
    getattr(self, 'show_' + self.tab)()

  def _head(self, title, sub, actions=''):
    ui.q(self, '.js-title').textContent = title
    ui.q(self, '.js-sub').textContent = sub
    ui.q(self, '.js-actions').innerHTML = actions

  # ================================================================ requests
  def show_requests(self):
    res = ui.call('admin_overview')
    if res is ui.FAIL:
      return
    self.data = res
    self.render_requests()

  def render_requests(self):
    reqs = self.data['requests']
    open_n = len([r for r in reqs if r['status'] in ui.OPEN_STATUSES])
    unread = len([r for r in reqs if r.get('unread')])
    self._head('Requests', f"{ui.plural(open_n, 'open request')} across {ui.plural(len(self.data['clients']), 'client')} · {unread} unread",
               f'<button type="button" class="aa-btn accent" data-act="new-for">{icon("plus", "width=16 height=16")} New request for a client</button>')

    def count(fn):
      return len([r for r in reqs if fn(r)])
    tiles_def = [
      ('unread', 'Unread', count(lambda r: r.get('unread')), '#2F5BFF'),
      ('new', 'New', count(lambda r: r['status'] == 'new'), '#8C94A3'),
      ('scoping', 'Scoping', count(lambda r: r['status'] == 'scoping'), '#B7791F'),
      ('waiting', 'Waiting on client', count(lambda r: r['status'] in ('quoted', 'review')), '#2F5BFF'),
      ('in_progress', 'In progress', count(lambda r: r['status'] == 'in_progress'), '#7A5CFA'),
      ('delivered', 'Delivered', count(lambda r: r['status'] == 'delivered'), '#0E9F6E'),
    ]
    tiles = '<div class="tiles six">'
    for key, label, n, color in tiles_def:
      attn = ' attn' if key == 'unread' and n else ''
      tiles += (f'<button type="button" class="tile{attn}{" on" if self.filter == key else ""}" data-act="filter" data-arg="{key}">'
                f'<div class="v">{n}</div><div class="l"><span class="d" style="background:{color}"></span>{label}</div></button>')
    tiles += '</div>'
    clients = ui.options([(c['id'], (c.get('company') + ' · ' if c.get('company') else '') + c['name']) for c in self.data['clients']],
                         self.client_filter, 'All clients')
    pills = ''.join(f'<button type="button" class="{"on" if self.filter == k else ""}" data-act="filter" data-arg="{k}">{lbl}</button>'
                    for k, lbl in [('open', 'Open'), ('all', 'All'), ('declined', 'Closed')])
    views = ''.join(f'<button type="button" class="{"on" if self.view == k else ""}" data-act="view" data-arg="{k}">{icon(ic, "width=14 height=14")} {lbl}</button>'
                    for k, lbl, ic in [('list', 'List', 'list'), ('board', 'Board', 'columns')])
    root = ui.q(self, '.js-root')
    root.innerHTML = tiles + f'''
      <div class="toolbar">
        <div class="left"><div class="pills">{pills}</div><select class="js-client" aria-label="Filter by client">{clients}</select></div>
        <div class="right"><input type="search" class="js-search" placeholder="Search title, ref, client" value="{esc(self.search)}" aria-label="Search">
          <div class="pills">{views}</div></div>
      </div>
      <div class="js-list"></div>'''
    sel = root.querySelector('.js-client')
    search = root.querySelector('.js-search')

    def on_client(e):
      self.client_filter = sel.value
      self.render_list()

    def on_search(e):
      self.search = (search.value or '').strip().lower()
      self.render_list()
    sel.addEventListener('change', on_client)
    search.addEventListener('input', on_search)
    self.render_list()

  def _filtered(self):
    reqs = self.data['requests']
    f = self.filter
    if self.view == 'board' and f in ('open', 'all'):
      pass
    elif f == 'open':
      reqs = [r for r in reqs if r['status'] in ui.OPEN_STATUSES]
    elif f == 'unread':
      reqs = [r for r in reqs if r.get('unread')]
    elif f == 'waiting':
      reqs = [r for r in reqs if r['status'] in ('quoted', 'review')]
    elif f in ui.STATUS:
      reqs = [r for r in reqs if r['status'] == f]
    if self.client_filter:
      reqs = [r for r in reqs if (r.get('client') or {}).get('id') == self.client_filter]
    if self.search:
      s = self.search
      reqs = [r for r in reqs if s in (r['title'] + ' ' + r['ref'] + ' ' + (r.get('client') or {}).get('name', '') + ' ' +
                                       (r.get('client') or {}).get('company', '')).lower()]
    return reqs

  def render_list(self):
    reqs = self._filtered()
    box = ui.q(self, '.js-list')
    if self.view == 'board':
      cols = ''
      for st in BOARD_COLS:
        items = [r for r in reqs if r['status'] == st]
        label, _cls, color = ui.STATUS[st]
        cards = ''
        for r in items:
          c = r.get('client') or {}
          cards += (f'<div class="kc{" unread" if r.get("unread") else ""}" data-act="open" data-arg="{r["id"]}">'
                    f'<div class="ref"><span>{esc(r["ref"])}</span>{ui.priority_chip(r["priority"]) if r["priority"] in ("high", "urgent") else ""}</div>'
                    f'<b>{esc(r["title"])}</b><div class="who">{esc(c.get("company") or c.get("name", ""))}</div>'
                    f'{ui.progress_bar(r["progress"], st == "delivered")}</div>')
        cols += (f'<div class="col"><h4><span><span class="d" style="background:{color}"></span>{label}</span><span>{len(items)}</span></h4>'
                 f'{cards or EMPTY_COL}</div>')
      box.innerHTML = f'<div class="board">{cols}</div>'
      return
    if not reqs:
      box.innerHTML = ui.empty('inbox', 'No requests here', 'Try another filter, or load demo data from the Tools tab.')
      return
    head = ('<div class="rq admin head"><span>Ref</span><span>Request</span><span>Client</span><span>Status</span>'
            '<span>Progress</span><span style="text-align:right">Activity</span></div>')
    box.innerHTML = '<div class="rq-list">' + head + ''.join(row_html(r, admin=True) for r in reqs) + '</div>'

  def _set_filter(self, key):
    self.filter = key
    self.render_requests()

  def _set_view(self, key):
    self.view = key
    self.render_requests()

  def new_for_client(self, client_id=None):
    clients = [c for c in self._clients_cache() if not c.get('is_admin')]
    if not clients:
      return ui.toast("No clients yet. Clients appear once they create a workspace (or load demo data).", 'warning', 5)
    box = ui.H(f'''
      <div>
        <h3 style="font-size:1.3rem;margin-bottom:4px">New request for a client</h3>
        <p class="small muted">It appears in their workspace right away, and they get an email.</p>
        <div class="f"><label>Client</label><select name="client_id">{ui.options([(c["id"], (c.get("company") + " · " if c.get("company") else "") + c["name"]) for c in clients], client_id)}</select></div>
        {request_form_html(budgets=False)}
        <div style="display:flex;gap:8px;justify-content:flex-end"><button type="button" class="aa-btn ghost" data-act="cancel">Cancel</button>
          <button type="button" class="aa-btn accent" data-act="ok">Create request</button></div>
      </div>''')
    ui.wire_segs(box)

    def ok(_):
      data = collect(box)
      msg = validate(data)
      if msg:
        err = ui.q(box, '.aa-error')
        err.textContent = msg
        ui.show(err)
        return
      cid = ui.vals(box).get('client_id')
      res = ui.call('admin_create_request', cid, data)
      if res is not ui.FAIL:
        ui.close_modal(box, res)

    ui.bind(box, {'ok': ok, 'cancel': lambda a: ui.close_modal(box, None)})
    rid = ui.modal(box, large=True)
    if rid:
      ui.toast("Request created.")
      state.go('r/' + rid)

  # ================================================================ clients
  def _clients_cache(self):
    if getattr(self, '_clients', None) is None:
      res = ui.call('admin_clients')
      self._clients = [] if res is ui.FAIL else res
    return self._clients

  def show_clients(self, reload=False):
    if reload:
      self._clients = None
    people = self._clients_cache()
    clients = [p for p in people if not p.get('is_admin')]
    self._head('Clients', f"{ui.plural(len(clients), 'client')} · {ui.plural(len(people) - len(clients), 'consultant')}")
    if not people:
      ui.q(self, '.js-root').innerHTML = ui.empty('users', 'No clients yet', 'Clients appear here once they create a workspace.')
      return
    cards = ''
    for p in people:
      tags = ''
      if p.get('is_admin'):
        tags += ui.chip('Consultant', 'ink')
      if p.get('is_demo'):
        tags += ui.chip('Demo', 'amber')
      if not p.get('enabled') and not p.get('is_demo'):
        tags += ui.chip('Disabled', 'red')
      seen = ('Active ' + ui.ago(p['last_seen'])) if p.get('last_seen') else 'Never signed in'
      acts = ''
      if not p.get('is_admin'):
        acts += (f'<button type="button" class="aa-btn sm" data-act="new-for" data-arg="{p["id"]}">{icon("plus", "width=14 height=14")} Request</button>'
                 f'<button type="button" class="aa-btn sm ghost" data-act="client-req" data-arg="{p["id"]}">View requests</button>')
      if not p.get('is_demo') and p['id'] != (state.me or {}).get('id'):
        acts += (f'<button type="button" class="aa-btn sm ghost" data-act="toggle-admin" data-arg="{p["id"]}">{"Remove consultant" if p.get("is_admin") else "Make consultant"}</button>'
                 f'<button type="button" class="aa-btn sm {"ghost" if p.get("enabled") else "green"}" data-act="toggle-enabled" data-arg="{p["id"]}">{"Disable" if p.get("enabled") else "Enable"}</button>')
      cards += f'''
        <div class="person">
          <div class="top">{ui.avatar(p, 44)}<div style="min-width:0"><b>{esc(p["name"])}</b>
            <div class="s">{esc(p.get("company") or "")}{" · " if p.get("company") else ""}<a href="mailto:{esc(p.get("email"))}">{esc(p.get("email"))}</a></div></div></div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px">{tags}<span class="chip outline">{esc(seen)}</span></div>
          <div class="stats"><div><b>{p["open"]}</b>open</div><div><b>{p["delivered"]}</b>delivered</div><div><b>{ui.money(p["value"])}</b>accepted value</div></div>
          <div class="acts">{acts}</div>
        </div>'''
    ui.q(self, '.js-root').innerHTML = f'<div class="people">{cards}</div>'

  def _client_requests(self, client_id):
    self.tab = 'requests'
    self.client_filter = client_id
    self.filter = 'all'
    for a in ui.qa(self, '.tabs-line a'):
      a.classList.toggle('on', a.getAttribute('href') == '#admin')
    self.show_requests()

  def _find(self, uid):
    for p in self._clients_cache():
      if p['id'] == uid:
        return p
    return None

  def _toggle_admin(self, uid):
    p = self._find(uid)
    if p is None:
      return
    make = not p.get('is_admin')
    if make and not ui.ask(f"Give {p['name']} consultant access? They'll see every client and request.", yes='Make consultant'):
      return
    if ui.call('admin_set_user', uid, {'is_admin': make}) is not ui.FAIL:
      self.show_clients(reload=True)

  def _toggle_enabled(self, uid):
    p = self._find(uid)
    if p is None:
      return
    if ui.call('admin_set_user', uid, {'enabled': not p.get('enabled')}) is not ui.FAIL:
      self.show_clients(reload=True)

  # ================================================================ leads
  def show_leads(self):
    res = ui.call('admin_leads')
    if res is ui.FAIL:
      return
    self.leads = res
    new = len([l for l in res if l['status'] == 'new'])
    self._head('Leads', f"Project briefs from the website · {new} new")
    if not res:
      ui.q(self, '.js-root').innerHTML = ui.empty('mail', 'No briefs yet', 'Briefs sent from the website contact form land here, and you get an email for each one.')
      return
    out = ''
    for l in res:
      subj = 'Re: your Addanapp project brief'
      out += f'''
        <div class="lead-card">
          <div><div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><b style="color:var(--ink);font-size:1.05rem">{esc(l["name"])}</b>
            {ui.chip("New", "accent") if l["status"] == "new" else ""}<span class="small muted">{esc(ui.ago(l["created"]))}</span></div>
            <div class="small"><a href="mailto:{esc(l["email"])}?subject={esc(subj)}">{esc(l["email"])}</a>{(" · " + esc(l["company"])) if l["company"] else ""}</div>
            <div class="meta">{ui.chip(l["kind"], "outline") if l["kind"] else ""}{ui.chip("Budget: " + l["budget"], "outline") if l["budget"] else ""}</div>
            <div class="msg">{esc(l["message"])}</div></div>
          <div class="side">
            <select class="inp js-lead-status" data-id="{l["id"]}" aria-label="Lead status">{ui.options(LEAD_STATUSES, l["status"])}</select>
            <a class="aa-btn sm" href="mailto:{esc(l["email"])}?subject={esc(subj)}">{icon("mail", "width=14 height=14")} Reply</a>
            <button type="button" class="aa-btn sm danger" data-act="lead-del" data-arg="{l["id"]}">Delete</button>
          </div>
        </div>'''
    root = ui.q(self, '.js-root')
    root.innerHTML = out
    for sel in ui.qa(root, '.js-lead-status'):
      self._wire_lead_select(sel)

  def _wire_lead_select(self, sel):
    def on_change(e):
      if ui.call('admin_update_lead', sel.getAttribute('data-id'), sel.value) is not ui.FAIL:
        ui.toast("Lead updated.")
        if state.main:
          state.main._poll()
    sel.addEventListener('change', on_change)

  def _lead_delete(self, lid):
    if ui.ask("Delete this lead permanently?", yes='Delete'):
      if ui.call('admin_update_lead', lid, None, True) is not ui.FAIL:
        self.show_leads()

  # ================================================================ tools
  def show_tools(self):
    self._head('Tools', 'Demo content and site checks.')
    ui.q(self, '.js-root').innerHTML = f'''
      <div class="people">
        <div class="person"><div class="top"><span class="av" style="width:44px;height:44px;background:var(--ai)">{icon("sparkle", "width=20 height=20")}</span>
          <div><b>Demo data</b><div class="s">3 fictional clients, 8 requests at every stage</div></div></div>
          <p class="small muted">Great for showing the console and workspace to prospects. Demo clients can't sign in and never receive email.</p>
          <div class="acts"><button type="button" class="aa-btn sm" data-act="seed">Load demo data</button>
            <button type="button" class="aa-btn sm danger" data-act="clear">Remove demo data</button></div></div>
        <div class="person"><div class="top"><span class="av" style="width:44px;height:44px;background:var(--human)">{icon("globe", "width=20 height=20")}</span>
          <div><b>Search &amp; SEO</b><div class="s">For Google Search Console</div></div></div>
          <p class="small muted">Submit the sitemap at <span class="mono">/_/api/sitemap.xml</span> in Search Console. Titles, descriptions,
            Open Graph tags and structured data (ProfessionalService, FAQ, portfolio) are in the page head.</p>
          <div class="acts"><a class="aa-btn sm ghost" href="/_/api/sitemap.xml" target="_blank" rel="noopener">Open sitemap</a>
            <a class="aa-btn sm ghost" href="https://search.google.com/test/rich-results" target="_blank" rel="noopener">Rich results test</a></div></div>
        <div class="person"><div class="top"><span class="av" style="width:44px;height:44px;background:var(--accent)">{icon("bell", "width=20 height=20")}</span>
          <div><b>Notifications</b><div class="s">Email on new requests, comments and briefs</div></div></div>
          <p class="small muted">Consultant email notifications follow your account settings.</p>
          <div class="acts"><a class="aa-btn sm ghost" href="#account">Account settings</a></div></div>
      </div>'''

  def _tool(self, fn):
    if fn == 'admin_clear_demo' and not ui.ask("Remove all demo clients and their requests?", yes='Remove'):
      return
    res = ui.call(fn)
    if res is not ui.FAIL:
      ui.toast(res, timeout=5)
      self._clients = None
      if state.main:
        state.main._poll()
