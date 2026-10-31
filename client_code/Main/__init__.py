from ._anvil_designer import MainTemplate
from anvil import *
import anvil.js
import anvil.users
import anvil.server

from .. import ui, state, dialogs, i18n
from ..i18n import t
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
from .. import legal

SEO_TITLE = t("AddAnApp - triple A software delivery service")
SEO_DESC = t("Montréal software consultancy for web apps, admin panels, client portals and data platforms. "
             "AI-accelerated, human-validated, fixed quotes. Pay for results.")


def _lang_switch():
  items = ''.join(
    f'<button type="button" role="menuitemradio" aria-checked="{"true" if c == i18n.lang else "false"}" lang="{c}" '
    f'class="{"on" if c == i18n.lang else ""}" data-lang="{c}">{name}<span class="code">{c.upper()}</span></button>'
    for c, name in i18n.LANGS)
  return (f'<div class="aa-lang js-lang">'
          f'<button type="button" class="aa-lang-btn js-lang-btn" aria-haspopup="true" aria-label="{t("Language")}: {i18n.NAMES[i18n.lang]}" '
          f'title="{t("Language")}">{icon("globe", "width=16 height=16")}<span>{i18n.lang.upper()}</span></button>'
          f'<div class="aa-menu aa-lang-menu" role="menu">{items}</div></div>')


def _lang_links():
  return ' '.join(f'<a href="javascript:void(0)" data-lang="{c}" lang="{c}" class="{"on" if c == i18n.lang else ""}">{name}</a>'
                  for c, name in i18n.LANGS)


SHELL = f'''
<div class="aa-shell mode-public signed-out">
  <header class="aa-header">
    <div class="aa-wrap aa-header-inner">
      <a class="aa-brand" href="#home" aria-label="{t('Addanapp home')}">{LOGO}{WORDMARK}</a>
      <nav class="aa-nav aa-nav-public" aria-label="{t('Main')}">
        <a href="#home/approach" data-nav="approach">{t('Approach')}</a>
        <a href="#home/services" data-nav="services">{t('Services')}</a>
        <a href="#work" data-nav="work">{t('Work')}</a>
        <a href="#home/workspace" data-nav="workspace">{t('Client workspace')}</a>
        <a href="#home/engage" data-nav="engage">{t('Engagements')}</a>
        <a href="#home/faq" data-nav="faq">{t('FAQ')}</a>
        <a href="#login" class="sm-only js-out-only">{t('Sign in')}</a>
      </nav>
      <nav class="aa-nav aa-nav-app js-appnav" aria-label="{t('Workspace')}"></nav>
      <div class="aa-header-actions">
        {_lang_switch()}
        <span class="when-out">
          <button type="button" class="aa-text-btn hide-sm js-login">{t('Sign in')}</button>
          <a class="aa-btn accent sm" href="#home/contact">{t('Start a project')}</a>
        </span>
        <span class="when-in">
          <a class="aa-btn accent sm public-only hide-sm js-ws" href="#portal">{t('Open workspace')}</a>
          <div class="aa-me">
            <button type="button" class="aa-me-btn js-me-btn" aria-haspopup="true" aria-label="{t('Account menu')}">
              <span class="js-avatar"></span><span class="nm js-first"></span><span class="chev">&#9662;</span></button>
            <div class="aa-menu" role="menu">
              <div class="head"><b class="js-name"></b><span class="small muted js-email"></span></div>
              <hr>
              <a href="#portal" class="js-ws-link" role="menuitem">{t('My workspace')}</a>
              <a href="#admin" class="js-admin-link hidden" role="menuitem">{t('Consultant console')}</a>
              <a href="#new" class="js-client-only" role="menuitem">{t('New request')}</a>
              <a href="#account" role="menuitem">{t('Account settings')}</a>
              <a href="#home" role="menuitem">{t('Addanapp website')}</a>
              <hr>
              <button type="button" class="js-logout" role="menuitem">{t('Sign out')}</button>
            </div>
          </div>
        </span>
        <button class="aa-burger js-burger" type="button" aria-label="{t('Open menu')}" aria-expanded="false"><span></span></button>
      </div>
    </div>
  </header>
  <main class="aa-main" id="main" anvil-slot="content"></main>
  <footer class="aa-footer">
    <div class="aa-wrap">
      <div class="cols">
        <div>
          <a class="aa-brand" href="#home">{LOGO}{WORDMARK}</a>
          <p style="max-width:340px">{t('Custom software, AI-accelerated and human-validated. Web apps, admin panels, client portals and data platforms, built in Montréal.')}</p>
          <address>{t('Montréal, Québec, Canada')}{('<br><a href="mailto:' + CONTACT_EMAIL + '">' + CONTACT_EMAIL + '</a>') if CONTACT_EMAIL else ''}</address>
          <p class="aa-lang-links" aria-label="{t('Language')}">{icon('globe', 'width=15 height=15')}{_lang_links()}</p>
        </div>
        <div><h4>{t('Services')}</h4><ul>
          <li><a href="#home/services">{t('Admin panels &amp; back-offices')}</a></li>
          <li><a href="#home/services">{t('Client portals')}</a></li>
          <li><a href="#home/services">{t('APIs &amp; integrations')}</a></li>
          <li><a href="#home/services">{t('Mobile-first web apps')}</a></li>
          <li><a href="#home/services">{t('AI features')}</a></li></ul></div>
        <div><h4>{t('Company')}</h4><ul>
          <li><a href="#home/approach">{t('Our approach')}</a></li>
          <li><a href="#work">{t('Work')}</a></li>
          <li><a href="#home/engage">{t('Engagements')}</a></li>
          <li><a href="#home/faq">{t('FAQ')}</a></li>
          <li><a href="#privacy">{t('Privacy &amp; Terms')}</a></li></ul></div>
        <div><h4>{t('Clients')}</h4><ul>
          <li><a href="#home/contact">{t('Start a project')}</a></li>
          <li><a href="#signup">{t('Create a workspace')}</a></li>
          <li><a href="#login">{t('Sign in')}</a></li>
          <li><a href="#home/montreal" lang="fr-CA">En français</a></li></ul></div>
      </div>
      <div class="base">
        <span>&copy; <span class="js-year"></span> {t('Addanapp · Custom software development, Montréal')}</span>
        <span>{t('AI-accelerated. Human-validated.')} <a href="javascript:void(0)" data-lk-open="overview">{t('Privacy &amp; Terms')}</a></span>
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
    self.lang_box = self.node.querySelector('.js-lang')
    self.node.querySelector('.js-lang-btn').addEventListener('click', self._toggle_lang)
    for el in ui.qa(self.node, '[data-lang]'):
      self._wire_lang(el)
    anvil.js.window.document.addEventListener('click', self._outside_click)
    legal.setup(lang=i18n.lang)
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
    self.lang_box.classList.remove('open')
    self.menu.classList.toggle('open')

  def _toggle_lang(self, e):
    e.stopPropagation()
    self.menu.classList.remove('open')
    self.lang_box.classList.toggle('open')

  def _wire_lang(self, el):
    def pick(e):
      e.preventDefault()
      code = el.getAttribute('data-lang')
      self.lang_box.classList.remove('open')
      if code != i18n.lang:
        i18n.set_lang(code)
    el.addEventListener('click', pick)

  def _toggle_nav(self, e):
    e.stopPropagation()
    self.shell.classList.toggle('nav-open')
    b = self.node.querySelector('.js-burger')
    b.setAttribute('aria-expanded', 'true' if self.shell.classList.contains('nav-open') else 'false')

  def _outside_click(self, e):
    if not self.menu.contains(e.target):
      self.menu.classList.remove('open')
    if not self.lang_box.contains(e.target):
      self.lang_box.classList.remove('open')

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
    q('.js-first').textContent = (me.get('name') or t('Account')).split(' ')[0]
    q('.js-name').textContent = me.get('name') or ''
    q('.js-email').textContent = me.get('email') or ''
    admin = bool(me.get('is_admin'))
    ui.show(q('.js-admin-link'), admin)
    ui.show(q('.js-client-only'), not admin)
    ui.show(q('.js-ws-link'), not admin)
    q('.js-ws').setAttribute('href', '#admin' if admin else '#portal')
    q('.js-ws').textContent = t('Open console') if admin else t('Open workspace')
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
      nav.innerHTML = (f'<a href="#admin" data-nav="admin">{icon("inbox", "width=16 height=16")}{t("Requests")}{cnt(c.get("unread", 0))}</a>'
                       f'<a href="#admin/clients" data-nav="admin/clients">{icon("users", "width=16 height=16")}{t("Clients")}</a>'
                       f'<a href="#admin/leads" data-nav="admin/leads">{icon("mail", "width=16 height=16")}{t("Leads")}{cnt(c.get("leads", 0))}</a>'
                       f'<a href="#admin/tools" data-nav="admin/tools">{icon("sliders", "width=16 height=16")}{t("Tools")}</a>'
                       f'<a href="#account" data-nav="account" class="sm-only">{icon("user", "width=16 height=16")}{t("Account")}</a>'
                       f'<a href="#home" class="sm-only">{icon("globe", "width=16 height=16")}{t("Website")}</a>')
    else:
      nav.innerHTML = (f'<a href="#portal" data-nav="portal">{icon("grid", "width=16 height=16")}{t("Dashboard")}{cnt(c.get("unread", 0))}</a>'
                       f'<a href="#new" data-nav="new">{icon("plus", "width=16 height=16")}{t("New request")}</a>'
                       f'<a href="#account" data-nav="account">{icon("user", "width=16 height=16")}{t("Account")}</a>'
                       f'<a href="#home" class="sm-only">{icon("globe", "width=16 height=16")}{t("Website")}</a>')
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
    legal.signed_out()
    state.counts = {}
    self.timer.interval = 0
    self.menu.classList.remove('open')
    self.update_header()
    ui.toast(t("You're signed out. See you soon."))
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
    self.lang_box.classList.remove('open')
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
      return ui.set_meta(t("Work | Apps, platforms and games built by Addanapp, Montréal"),
                         t("Live products built by Addanapp: PlanPlate, Prepsto, VitalRPA, ArviStay, ToonyLoony, Subsudo, "
                           "QuickyBricks, MonShop, CityCrossers, OScreenplay and more."))
    if head == 'privacy':
      self.set_page(Privacy(), public=True)
      return ui.set_meta(t("Privacy & Terms | Addanapp"), t("How Addanapp collects, uses and protects personal information (Québec Law 25, PIPEDA, GDPR), and the terms of use."))
    if head in ('login', 'signup'):
      return self.open_auth(head)

    # ---- private pages
    if not logged:
      state.after_login = r
      return self.open_auth('login')

    if head == 'portal':
      self.set_page(Portal(), nav='portal')
      title = t('Workspace')
    elif head == 'new':
      self.set_page(NewRequest(), nav='new')
      title = t('New request')
    elif head == 'r' and arg:
      self.set_page(RequestDetail(request_id=arg), nav='admin' if state.is_admin() else 'portal')
      title = t('Request')
    elif head == 'account':
      self.set_page(Account(), nav='account')
      title = t('Account')
    elif head == 'admin':
      if not state.is_admin():
        return state.go('portal')
      tab = arg or 'requests'
      self.set_page(Admin(tab=tab), nav='admin' if tab == 'requests' else 'admin/' + tab)
      title = t('Consultant console')
    else:
      return state.go(state.home_route())
    ui.set_meta(f"{title} | Addanapp", None, private=True)
