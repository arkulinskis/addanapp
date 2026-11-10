"""Page addresses (the same as the old app, so shared links keep working):

    #home[/section]   the landing page, scrolled to a section (approach, services, work, youtube, workspace, engage,
                      partners, guides, faq, contact, montreal)
    #work  #guides[/slug]  #privacy                      public pages
    #login  #signup                                      the landing page with the sign-in box on top
    #portal  #new  #r/<request id>  #account             a client's workspace (signed in)
    #admin[/requests|clients|leads|tools]                the consultant console (admins)

Links in templates are plain <a href="#work">; code calls router.go("r/" + rid).
Anvil keeps the Shell layout between pages; show() tells it which page is open (Shell.refresh).
"""
import anvil
import anvil.js
from anvil.js import window

from . import state, ui
from .i18n import tp

SEO_TITLE = tp("Custom Web App Development in Montréal | Addanapp")
SEO_DESC = tp("Montréal software consultancy for web apps, admin panels, client portals and data platforms. "
              "AI-accelerated, human-validated, fixed quotes. Pay for results.")
# Home-page sections that belong to a header link (the "chapter" lit up in the header).
CHAPTER = {'method': 'approach', 'youtube': 'work', 'partners': 'engage', 'guides': 'engage'}
ADMIN_TABS = ('requests', 'clients', 'leads', 'tools')
_r: dict = {"listening": False, "page": None, "name": "", "shell": None}


def current():
    h = window.location.hash or ''
    return h[1:] if h.startswith('#') else h


def go(route):
    """Navigate to a route like 'r/123_456'. The same route again = show it again."""
    route = route or ''
    if current() == route:
        show()
    else:
        window.location.hash = route


def shell():
    return _r["shell"]


def _open(name, page, nav=None, public=False):
    _r["page"], _r["name"] = page, name
    anvil.open_form(page)
    sh = getattr(page, "layout", None)
    if sh is not None and hasattr(sh, "refresh"):
        _r["shell"] = sh
        sh.refresh(nav=nav, public=public)  # Anvil reuses the layout between pages: who is signed in, which page
    window.scrollTo(0, 0)


def _landing(section=None):
    from .Pages.Landing import Landing
    if isinstance(_r["page"], Landing):
        sh = _r["shell"]
        if sh is not None:
            sh.refresh(nav=section, public=True)
        if section:
            ui.scroll_to(section)
        else:
            window.scrollTo(0, 0)
        return
    _open("home", Landing(), nav=section, public=True)
    ui.set_meta(SEO_TITLE, SEO_DESC)
    if section:
        window.setTimeout(lambda: ui.scroll_to(section), 60)


def open_auth(mode):
    """The sign-in / create-workspace box, over the landing page (as on the old site)."""
    from .Dialogs.AuthBox import AuthBox
    if state.me():
        return go(state.home_route())
    _landing(None)
    window.UI_READY = True
    ok = anvil.alert(AuthBox(mode=mode), buttons=[], large=False, role="aa-dialog", dismissible=True)
    if ok:
        after_sign_in()
    elif current() in ('login', 'signup') or state.take_after():
        go('home')


def after_sign_in():
    state.refresh_me()
    sh = _r["shell"]
    if sh is not None:
        sh.signed_in()
    target = state.take_after() or state.home_route()
    if target in ('login', 'signup', 'home', ''):
        target = state.home_route()
    go(target)


def show():
    """Open the page for the current address."""
    window.UI_READY = False
    route = current()
    parts = [window.decodeURIComponent(p) for p in route.split('?')[0].split('/') if p != '']
    head = parts[0] if parts else ''
    arg = parts[1] if len(parts) > 1 else None
    if state.logged_in() and state.me() is None:
        state.refresh_me()
    elif not state.logged_in() and state.me() is not None:
        state.set_me(None)
    sh = _r["shell"]
    if sh is not None:
        sh.close_menus()

    if head == '' and state.me():
        return go(state.home_route())
    if head in ('', 'home'):
        _landing(arg)
    elif head == 'work':
        from .Pages.Work import Work
        _open('work', Work(), nav='work', public=True)
        ui.set_meta(tp("Work | Apps, platforms and games built by Addanapp, Montréal"),
                    tp("Live products built by Addanapp, from restaurant platforms and SaaS to games, VR and learning apps: "
                       "PlanPlate, Prepsto, VitalRPA, ArviStay, Health Booker, AutoAgile, Sheetsmith, Subsudo, City Fun Time and more."))
    elif head == 'guides':
        from .Pages.Guides import Guides
        _open('guides', Guides(focus=arg), nav='guides', public=True)
        ui.set_meta(tp("Free guides for business owners | Addanapp"),
                    tp("Five free PDF guides: when a spreadsheet has become an app, a one-page app brief template, buying AI-built "
                       "software, build vs buy with a 3-year cost worksheet, and a Québec Law 25 checklist."))
    elif head == 'privacy':
        from .Pages.Privacy import Privacy
        _open('privacy', Privacy(), public=True)
        ui.set_meta(tp("Privacy & Terms | Addanapp"),
                    tp("How Addanapp collects, uses and protects personal information (Québec Law 25, PIPEDA, GDPR), and the terms of use."))
    elif head in ('login', 'signup'):
        return open_auth(head)
    elif not state.me():
        state.remember_after(route)
        return open_auth('login')
    else:
        title = _private(head, arg)
        if title is None:
            return
        ui.set_meta(title + " | Addanapp", None, private=True)
    window.UI_READY = True  # tests and screenshots wait for this


def _private(head, arg):
    if head == 'portal':
        from .Pages.Portal import Portal
        _open('portal', Portal(), nav='portal')
        return tp('Workspace')
    if head == 'new':
        from .Pages.NewRequest import NewRequest
        _open('new', NewRequest(), nav='new')
        return tp('New request')
    if head == 'r' and arg:
        from .Pages.RequestDetail import RequestDetail
        _open('r', RequestDetail(request_id=arg), nav='admin' if state.is_admin() else 'portal')
        return tp('Request')
    if head == 'account':
        from .Pages.Account import Account
        _open('account', Account(), nav='account')
        return tp('Account')
    if head == 'admin':
        if not state.is_admin():
            go('portal')
            return None
        from .Pages.Admin import Admin
        tab = arg if arg in ADMIN_TABS else 'requests'
        _open('admin', Admin(tab=tab), nav='admin' if tab == 'requests' else 'admin/' + tab)
        return tp('Consultant console')
    go(state.home_route())
    return None


def _on_hash(event):
    show()


def start():
    if not _r["listening"]:
        window.addEventListener("hashchange", anvil.js.report_exceptions(_on_hash))
        _r["listening"] = True
    show()
