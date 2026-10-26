from ._anvil_designer import MainTemplate
from anvil import *
import anvil.js
import anvil.users
import anvil.server

from .. import ui, state, dialogs
from ..icons import icon, LOGO, WORDMARK
from ..content import CONTACT_EMAIL
from ..Landing import Landing
from ..Work import Work
from ..Portal import Portal
from ..NewRequest import NewRequest
from ..RequestDetail import RequestDetail
from ..Admin import Admin
from ..Account import Account
from ..Privacy import Privacy

SEO_TITLE = "AI-Accelerated App Development in Montréal | Addanapp"
SEO_DESC = ("Montréal software consultancy for web apps, admin panels, client portals and data platforms. "
        "AI-accelerated, human-validated, fixed quotes. Pay for results.")

SHELL = f'''
<div class="aa-shell mode-public signed-out">
  <header class="aa-header">
    <div class="aa-wrap aa-header-inner">
      <a class="aa-brand" href="#home" aria-label="Addanapp home">{LOGO}{WORDMARK}</a>
      <nav class="aa-nav aa-nav-public" aria-label="Main">
        <a href="#home/approach" data-nav="approach">Approach</a>
        <a href="#home/services" data-nav="services">Services</a>
        <a href="#work" data-nav="work">Work</a>
        <a href="#home/workspace" data-nav="workspace">Client workspace</a>
        <a href="#home/engage" data-nav="engage">Engagements</a>
        <a href="#home/faq" data-nav="faq">FAQ</a>
        <a href="#login" class="sm-only js-out-only">Client sign in</a>
      </nav>
      <nav class="aa-nav aa-nav-app js-appnav" aria-label="Workspace"></nav>
      <div class="aa-header-actions">
        <span class="when-out">
          <button type="button" class="aa-text-btn hide-sm js-login">Client sign in</button>
          <a class="aa-btn accent sm" href="#home/contact">Start a project</a>
        </span>
        <span class="when-in">
          <a class="aa-btn accent sm public-only hide-sm js-ws" href="#portal">Open workspace</a>
          <div class="aa-me">
            <button type="button" class="aa-me-btn js-me-btn" aria-haspopup="true" aria-label="Account menu">
              <span class="js-avatar"></span><span class="nm js-first"></span><span class="chev">&#9662;</span></button>
            <div class="aa-menu" role="menu">
              <div class="head"><b class="js-name"></b><span class="small muted js-email"></span></div>
              <hr>
              <a href="#portal" class="js-ws-link" role="menuitem">My workspace</a>
              <a href="#admin" class="js-admin-link hidden" role="menuitem">Consultant console</a>
              <a href="#new" class="js-client-only" role="menuitem">New request</a>
              <a href="#account" role="menuitem">Account settings</a>
              <a href="#home" role="menuitem">Addanapp website</a>
              <hr>
              <button type="button" class="js-logout" role="menuitem">Sign out</button>
            </div>
          </div>
        </span>
        <button class="aa-burger js-burger" type="button" aria-label="Open menu" aria-expanded="false"><span></span></button>
      </div>
    </div>
  </header>
  <main class="aa-main" id="main" anvil-slot="content"></main>
  <footer class="aa-footer">
    <div class="aa-wrap">
      <div class="cols">
        <div>
          <a class="aa-brand" href="#home">{LOGO}{WORDMARK}</a>
          <p style="max-width:340px">Custom software, AI-accelerated and human-validated. Web apps, admin panels, client portals and
            data platforms, built in Montréal.</p>
          <address>Montréal, Québec, Canada<br><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></address>
        </div>
        <div><h4>Services</h4><ul>
          <li><a href="#home/services">Admin panels &amp; back-offices</a></li>
          <li><a href="#home/services">Client portals</a></li>
          <li><a href="#home/services">APIs &amp; integrations</a></li>
          <li><a href="#home/services">Mobile-first web apps</a></li>
          <li><a href="#home/services">AI features</a></li></ul></div>
        <div><h4>Company</h4><ul>
          <li><a href="#home/approach">Our approach</a></li>
          <li><a href="#work">Work</a></li>
          <li><a href="#home/engage">Engagements</a></li>
          <li><a href="#home/faq">FAQ</a></li>
          <li><a href="#privacy">Privacy</a></li></ul></div>
        <div><h4>Clients</h4><ul>
          <li><a href="#home/contact">Start a project</a></li>
          <li><a href="#signup">Create a workspace</a></li>
          <li><a href="#login">Client sign in</a></li>
          <li><a href="#home/montreal" lang="fr-CA">En français</a></li></ul></div>
      </div>
      <div class="base">
        <span>&copy; <span class="js-year"></span> Addanapp · Custom software development, Montréal</span>
        <span>AI-accelerated. Human-validated. <a href="#privacy">Privacy</a></span>
      </div>
    </div>
  </footer>
  <div anvil-slot="hidden" style="display:none"></div>
</div>'''


class Main(MainTemplate):
  """App shell + hash router. Routes: #home[/section], #work, #portal, #new, #r/ID, #admin[/tab], #account."""

  def __init__(self, **properties):
    self.init_components(**properties)
    self.html = SHELL
    state.main = self
    self.page = None
    self.node = ui.dom(self)
    self.shell = self.node.querySelector('.aa-shell')
    self.menu = self.node.querySelector('.aa-me')
    self.node.querySelector('.js-year').textContent = str(ui.now_local().year)
    self.node.querySelector('.js-me-btn').addEventListener('click', self._toggle_menu)
    self.node.querySelector('.js-logout').addEventListener('click', self._logout)
    self.node.querySelector('.js-login').addEventListener('click', lambda e: state.go('login'))
    self.node.querySelector('.js-burger').addEventListener('click', self._toggle_nav)
    anvil.js.window.document.addEventListener('click', self._outside_click)
    anvil.js.window.addEventListener('hashchange', lambda e: self.route())

    self.timer = Timer(interval=0)
    self.timer.add_event_handler('tick', self._poll)
    self.add_component(self.timer, slot='hidden')

    if state.logged_in():
      state.refresh_me()
      self._start_polling()
    self.update_header()
    self.route()

  # ------------------------------------------------------------ header
  def _toggle_menu(self, e):
    e.stopPropagation()
    self.menu.classList.toggle('open')

  def _toggle_nav(self, e):
    e.stopPropagation()
    self.shell.classList.toggle('nav-open')
    b = self.node.querySelector('.js-burger')
    b.setAttribute('aria-expanded', 'true' if self.shell.classList.contains('nav-open') else 'false')

  def _outside_click(self, e):
    if not self.menu.contains(e.target):
      self.menu.classList.remove('open')

  def update_header(self):
    me = state.me
    signed = state.logged_in() and me is not None
    self.shell.classList.toggle('signed-in', signed)
    self.shell.classList.toggle('signed-out', not signed)
    for el in ui.qa(self.node, '.js-out-only'):
      ui.show(el, not signed)
    if not signed:
      self._render_app_nav()
      return
    def q(sel):
      return self.node.querySelector(sel)
    q('.js-avatar').innerHTML = ui.avatar(me, 30)
    q('.js-first').textContent = (me.get('name') or 'Account').split(' ')[0]
    q('.js-name').textContent = me.get('name') or ''
    q('.js-email').textContent = me.get('email') or ''
    admin = bool(me.get('is_admin'))
    ui.show(q('.js-admin-link'), admin)
    ui.show(q('.js-client-only'), not admin)
    ui.show(q('.js-ws-link'), not admin)
    q('.js-ws').setAttribute('href', '#admin' if admin else '#portal')
    q('.js-ws').textContent = 'Open console' if admin else 'Open workspace'
    self._render_app_nav()

  def _render_app_nav(self):
    nav = self.node.querySelector('.js-appnav')
    if not state.logged_in() or not state.me:
      nav.innerHTML = ''
      return
    c = state.counts or {}

    def cnt(n):
      return f' <span class="count">{n}</span>' if n else ''
    if state.is_admin():
      nav.innerHTML = (f'<a href="#admin" data-nav="admin">{icon("inbox", "width=16 height=16")}Requests{cnt(c.get("unread", 0))}</a>'
                       f'<a href="#admin/clients" data-nav="admin/clients">{icon("users", "width=16 height=16")}Clients</a>'
                       f'<a href="#admin/leads" data-nav="admin/leads">{icon("mail", "width=16 height=16")}Leads{cnt(c.get("leads", 0))}</a>'
                       f'<a href="#admin/tools" data-nav="admin/tools">{icon("sliders", "width=16 height=16")}Tools</a>'
                       f'<a href="#account" data-nav="account" class="sm-only">{icon("user", "width=16 height=16")}Account</a>'
                       f'<a href="#home" class="sm-only">{icon("globe", "width=16 height=16")}Website</a>')
    else:
      nav.innerHTML = (f'<a href="#portal" data-nav="portal">{icon("grid", "width=16 height=16")}Dashboard{cnt(c.get("unread", 0))}</a>'
                       f'<a href="#new" data-nav="new">{icon("plus", "width=16 height=16")}New request</a>'
                       f'<a href="#account" data-nav="account">{icon("user", "width=16 height=16")}Account</a>'
                       f'<a href="#home" class="sm-only">{icon("globe", "width=16 height=16")}Website</a>')
    self._mark_nav()

  def _mark_nav(self):
    key = getattr(self, 'nav_key', None)
    for a in ui.qa(self.node, '.aa-nav a'):
      a.classList.toggle('active', bool(key) and a.getAttribute('data-nav') == key)

  def update_counts(self, counts):
    state.counts = counts or {}
    self._render_app_nav()

  def _start_polling(self):
    self._poll()
    self.timer.interval = 60

  def _poll(self, **e):
    if not state.logged_in():
      self.timer.interval = 0
      return
    res = ui.call('poll_counts', _quiet=True)
    if res is not ui.FAIL and res:
      self.update_counts(res)

  # ------------------------------------------------------------ auth
  def open_auth(self, mode):
    if state.logged_in():
      return state.go(state.home_route())
    if not isinstance(self.page, Landing):
      self.set_page(Landing(), public=True, nav=None)
      ui.set_meta(SEO_TITLE, SEO_DESC)
    ok = dialogs.auth(mode)
    if ok:
      self.on_login()
    elif state.current_route() in ('login', 'signup') or state.after_login:
      state.after_login = None
      state.go('home')

  def on_login(self):
    state.refresh_me()
    self._start_polling()
    self.update_header()
    target = state.after_login or state.home_route()
    state.after_login = None
    if target in ('login', 'signup', 'home', ''):
      target = state.home_route()
    state.go(target)

  def _logout(self, e=None):
    anvil.users.logout()
    state.me = None
    state.counts = {}
    self.timer.interval = 0
    self.menu.classList.remove('open')
    self.update_header()
    ui.toast("You're signed out. See you soon.")
    state.go('home')

  # ------------------------------------------------------------ routing
  def set_page(self, page, public=False, nav=None):
    if self.page is not None:
      self.page.remove_from_parent()
    self.page = page
    self.shell.classList.toggle('mode-public', public)
    self.shell.classList.toggle('mode-app', not public)
    self.add_component(page, slot='content')
    self.nav_key = nav
    self._mark_nav()
    self._close_menus()
    anvil.js.window.scrollTo(0, 0)

  def _close_menus(self):
    self.menu.classList.remove('open')
    self.shell.classList.remove('nav-open')
    self.node.querySelector('.js-burger').setAttribute('aria-expanded', 'false')

  def route(self):
    r = state.current_route()
    parts = [p for p in r.split('/') if p != '']
    head = parts[0] if parts else ''
    arg = parts[1] if len(parts) > 1 else None
    logged = state.logged_in()
    if logged and state.me is None:
      state.refresh_me()
      self.update_header()
    self._close_menus()

    # ---- public pages
    if head == '' and logged:
      return state.go(state.home_route())
    if head in ('', 'home'):
      if isinstance(self.page, Landing):
        self.nav_key = arg
        self._mark_nav()
        if arg:
          ui.scroll_to(arg)
        else:
          anvil.js.window.scrollTo(0, 0)
        return
      self.set_page(Landing(), public=True, nav=arg)
      ui.set_meta(SEO_TITLE, SEO_DESC)
      if arg:
        ui.scroll_to(arg)
      return
    if head == 'work':
      self.set_page(Work(), public=True, nav='work')
      return ui.set_meta("Work | Apps, platforms and games built by Addanapp, Montréal",
                         "Live products built by Addanapp: PlanPlate reservations API, Varnote, Adorable Science, "
                         "CityCrossers, BusyBun, DoremiRoad, PoundFighter, Parapeet and Dilettante.")
    if head == 'privacy':
      self.set_page(Privacy(), public=True)
      return ui.set_meta("Privacy policy | Addanapp", "How Addanapp collects, uses and protects personal information (Québec Law 25, PIPEDA).")
    if head in ('login', 'signup'):
      return self.open_auth(head)

    # ---- private pages
    if not logged:
      state.after_login = r
      return self.open_auth('login')

    if head == 'portal':
      self.set_page(Portal(), nav='portal')
      title = 'Workspace'
    elif head == 'new':
      self.set_page(NewRequest(), nav='new')
      title = 'New request'
    elif head == 'r' and arg:
      self.set_page(RequestDetail(request_id=arg), nav='admin' if state.is_admin() else 'portal')
      title = 'Request'
    elif head == 'account':
      self.set_page(Account(), nav='account')
      title = 'Account'
    elif head == 'admin':
      if not state.is_admin():
        return state.go('portal')
      tab = arg or 'requests'
      self.set_page(Admin(tab=tab), nav='admin' if tab == 'requests' else 'admin/' + tab)
      title = 'Consultant console'
    else:
      return state.go(state.home_route())
    ui.set_meta(f"{title} | Addanapp", None, private=True)
