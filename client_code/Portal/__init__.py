from ._anvil_designer import PortalTemplate
from anvil import *

from .. import ui, state
from ..ui import esc
from ..icons import icon

FILTERS = [('active', 'Active'), ('action', 'Needs you'), ('delivered', 'Delivered'), ('closed', 'Closed'), ('all', 'All')]


def row_html(r, admin=False):
  sub_bits = [r['kind_label']]
  if r['status'] == 'quoted' and r.get('quote_amount') is not None:
    sub_bits.append('Fixed quote ' + ui.money(r['quote_amount']))
  if r.get('eta') and r['status'] in ('quoted', 'in_progress', 'review'):
    sub_bits.append('ETA ' + ui.fmt_date(r['eta']))
  if admin:
    c = r.get('client') or {}
    sub_bits.insert(0, c.get('company') or c.get('name') or '')
  sub = ' · '.join([b for b in sub_bits if b])
  done = r['status'] == 'delivered'
  pg = (f'<div class="pg">{ui.progress_bar(r["progress"], done)}<span>{r["progress"]}%</span></div>'
        if r['status'] not in ('declined',) else '<div class="pg"></div>')
  unread = ' unread' if r.get('unread') else ''
  if admin:
    c = r.get('client') or {}
    return (f'<a class="rq admin{unread}" href="#r/{r["id"]}"><span class="ref">{esc(r["ref"])}</span>'
            f'<div class="main"><div class="ttl">{esc(r["title"])}</div><div class="sub">{esc(sub)}</div></div>'
            f'<span class="cl small">{ui.avatar(c, 22)} {esc(c.get("name", ""))}</span>'
            f'<span class="st">{ui.status_chip(r["status"])}</span>{pg}'
            f'<span class="upd">{esc(ui.ago(r.get("last_activity")))}</span></a>')
  return (f'<a class="rq{unread}" href="#r/{r["id"]}"><span class="ref">{esc(r["ref"])}</span>'
          f'<div class="main"><div class="ttl">{esc(r["title"])}</div><div class="sub">{esc(sub)}</div></div>'
          f'<span class="st">{ui.status_chip(r["status"])}</span>{pg}'
          f'<span class="upd">{esc(ui.ago(r.get("last_activity")))}</span></a>')


class Portal(PortalTemplate):
  """Client dashboard: stats, what needs their attention, and every request."""

  def __init__(self, **properties):
    self.init_components(**properties)
    self.filter = 'active'
    self.search = ''
    self.data = None
    self.html = '<div class="app-page"><div class="aa-wrap js-root"></div></div>'
    ui.bind(self, {'filter': self._set_filter, 'new': lambda a: state.go('new')})
    self.load()

  def load(self):
    res = ui.call('my_requests')
    if res is ui.FAIL:
      return
    self.data = res
    self.render()

  def render(self):
    me = state.me or {}
    st = self.data['stats']
    reqs = self.data['requests']
    root = ui.q(self, '.js-root')
    first = (me.get('name') or '').split(' ')[0]
    company = me.get('company') or 'Your'
    head = f'''
      <div class="page-head">
        <div><div class="eyebrow">{esc(company)} workspace</div>
          <h1>{ui.greeting()}, {esc(first)}.</h1>
          <p>{ui.plural(st["open"], "open request")} · {ui.plural(st["delivered"], "delivery", "deliveries")} accepted</p></div>
        <div class="actions"><button type="button" class="aa-btn accent" data-act="new">{icon("plus", 'width="16" height="16"')} New request</button></div>
      </div>'''
    if not reqs:
      root.innerHTML = head + f'''
        <div class="empty">
          <div class="ico">{icon("rocket")}</div>
          <h3>Your workspace is ready</h3>
          <p>Submit your first request: a new feature, a fix, an integration or a whole new app. An engineer will scope it and
            send you a fixed quote, usually within two business days.</p>
          <button type="button" class="aa-btn accent lg" data-act="new">Submit your first request <span class="arr">&rarr;</span></button>
        </div>
        <div class="tiles" style="margin-top:28px">
          <div class="tile"><div class="v">1</div><div class="l">Describe the outcome</div></div>
          <div class="tile"><div class="v">2</div><div class="l">Approve a fixed quote</div></div>
          <div class="tile"><div class="v">3</div><div class="l">Follow progress notes</div></div>
          <div class="tile"><div class="v">4</div><div class="l">Accept, then pay</div></div>
        </div>'''
      return
    action = [r for r in reqs if r['status'] in ui.CLIENT_ACTION]
    attn = ''
    if action:
      items = ''
      for r in action:
        what = ('Approve quote · ' + ui.money(r.get('quote_amount'))) if r['status'] == 'quoted' else 'Review &amp; accept delivery'
        items += f'<a href="#r/{r["id"]}"><span><span class="mono muted">{esc(r["ref"])}</span> &nbsp;<b>{esc(r["title"])}</b></span><span class="small" style="color:var(--accent-d);font-weight:600;white-space:nowrap">{what} &rarr;</span></a>'
      attn = f'<div class="attn-box"><h4>Waiting on you</h4>{items}</div>'

    def tile(key, v, label, color, cls=''):
      return (f'<button type="button" class="tile {cls}{" on" if self.filter == key else ""}" data-act="filter" data-arg="{key}">'
              f'<div class="v">{v}</div><div class="l"><span class="d" style="background:{color}"></span>{label}</div></button>')
    tiles = ('<div class="tiles">' + tile('active', st['open'], 'Open', '#182031') +
             tile('action', st['action'], 'Needs you', '#2F5BFF', 'attn' if st['action'] else '') +
             tile('progress', st['in_progress'], 'In progress', '#7A5CFA') +
             tile('delivered', st['delivered'], 'Delivered', '#0E9F6E') + '</div>')
    pills = ''.join(f'<button type="button" class="{"on" if self.filter == k else ""}" data-act="filter" data-arg="{k}">{lbl}</button>'
                    for k, lbl in FILTERS)
    root.innerHTML = head + attn + tiles + f'''
      <div class="toolbar"><div class="left"><div class="pills">{pills}</div></div>
        <div class="right"><input type="search" class="js-search" placeholder="Search requests" aria-label="Search requests" value="{esc(self.search)}"></div></div>
      <div class="js-list"></div>'''
    search = root.querySelector('.js-search')

    def on_input(e):
      self.search = (search.value or '').strip().lower()
      self.render_list()
    search.addEventListener('input', on_input)
    self.render_list()

  def _set_filter(self, key):
    self.filter = key
    self.render()

  def render_list(self):
    reqs = self.data['requests']
    f = self.filter
    if f == 'active':
      reqs = [r for r in reqs if r['status'] in ui.OPEN_STATUSES]
    elif f == 'action':
      reqs = [r for r in reqs if r['status'] in ui.CLIENT_ACTION]
    elif f == 'progress':
      reqs = [r for r in reqs if r['status'] == 'in_progress']
    elif f == 'delivered':
      reqs = [r for r in reqs if r['status'] == 'delivered']
    elif f == 'closed':
      reqs = [r for r in reqs if r['status'] == 'declined']
    if self.search:
      s = self.search
      reqs = [r for r in reqs if s in (r['title'] + ' ' + r['ref'] + ' ' + r['description']).lower()]
    box = ui.q(self, '.js-list')
    if not reqs:
      box.innerHTML = ui.empty('inbox', 'Nothing here', 'No requests match this view.')
      return
    head = ('<div class="rq head"><span>Ref</span><span>Request</span><span>Status</span><span>Progress</span>'
            '<span style="text-align:right">Updated</span></div>')
    box.innerHTML = '<div class="rq-list">' + head + ''.join(row_html(r) for r in reqs) + '</div>'
