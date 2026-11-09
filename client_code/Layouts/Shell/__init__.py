from anvil import *
import anvil.js
import anvil.users
from anvil.js import window

from ._anvil_designer import ShellTemplate
from ... import content, i18n, legal, router, state, ui
from ...i18n import tp
from ...portfolio import PROJECTS

LANG_CODES = ("en", "fr", "ru", "lv")


class Shell(ShellTemplate):
    """The frame around every page: the header (six chapter links for visitors, the workspace menu for signed-in
    people, the language switch, the account menu, the burger on phones), the footer, and a timer that polls the
    unread counts once a minute.

    Anvil keeps ONE Shell while pages come and go (open_form swaps only the "content" slot), so everything that
    depends on who is signed in or which page is open is drawn in refresh(), which the router calls after every page."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self._nav = None
        self.year_label.text = str(ui.now_local().year)
        for link in (self.deck_menu_link, self.deck_footer_link):
            for k, v in content.deck().items():
                state.set_attr(link, k, v)
        self.lang_code.text = i18n.lang.upper()
        state.set_attr(self.lang_btn, "aria-label", tp("Language") + ": " + i18n.NAMES[i18n.lang])
        state.set_attr(self.lang_btn, "title", tp("Language"))
        for code in LANG_CODES:
            on = code == i18n.lang
            menu_item = getattr(self, "lang_" + code)
            menu_item.classes["on"] = on
            state.set_attr(menu_item, "aria-checked", "true" if on else "false")
            getattr(self, "fl_" + code).classes["on"] = on
        for btn in (self.grp_work_btn, self.grp_engage_btn):
            state.set_attr(btn, "aria-label", tp("More in {section}", section=tp("Work" if btn is self.grp_work_btn else "Engagements")))
        i18n.apply(self, products=len(PROJECTS))
        self._outside = anvil.js.report_exceptions(self._close_outside)
        self._keys = anvil.js.report_exceptions(self._key)
        if state.me():
            self.start_polling()
        self.refresh()

    # ---------------------------------------------------------------- drawing
    def refresh(self, nav=None, public=True):
        """Called by the router after every page: public site or workspace look, signed in or not, the lit-up link."""
        me = state.me()
        self._nav = nav
        for name, on in (("mode-public", public), ("mode-app", not public), ("signed-in", bool(me)), ("signed-out", not me)):
            self.shell.classes[name] = on
        self.nav_login.classes["hidden"] = bool(me)
        if me:
            admin = bool(me.get("is_admin"))
            self.me_avatar.person = me
            self.me_first.text = ui.first_name(me) or tp("Account")
            self.me_name.text = me.get("name") or ""
            self.me_email.text = me.get("email") or ""
            self.m_admin.visible = admin
            self.m_ws.visible = not admin
            self.m_new.visible = not admin
            state.set_attr(self.ws_link, "href", "#admin" if admin else "#portal")
            self.ws_label.text = tp("Open console") if admin else tp("Open workspace")
        self._draw_app_nav()
        try:
            window.aa.markNav(router.CHAPTER.get(nav, nav) or "")
        except Exception:
            pass
        self.close_menus()

    def _draw_app_nav(self):
        me = state.me()
        if not me:
            self.app_nav.items = []
            return
        c = state.counts() or {}
        nav = self._nav
        if me.get("is_admin"):
            links = [("#admin", "admin", "inbox", tp("Requests"), c.get("unread", 0), False),
                     ("#admin/clients", "admin/clients", "users", tp("Clients"), 0, False),
                     ("#admin/leads", "admin/leads", "mail", tp("Leads"), c.get("leads", 0), False),
                     ("#admin/tools", "admin/tools", "sliders", tp("Tools"), 0, False),
                     ("#account", "account", "user", tp("Account"), 0, True),
                     ("#home", "", "globe", tp("Website"), 0, True)]
        else:
            links = [("#portal", "portal", "grid", tp("Dashboard"), c.get("unread", 0), False),
                     ("#new", "new", "plus", tp("New request"), 0, False),
                     ("#account", "account", "user", tp("Account"), 0, False),
                     ("#home", "", "globe", tp("Website"), 0, True)]
        self.app_nav.items = [{"href": h, "icon": ic, "label": label, "count": n, "sm_only": sm, "on": bool(key) and key == nav}
                              for h, key, ic, label, n, sm in links]

    # ---------------------------------------------------------------- unread counts
    def start_polling(self):
        self.poll_timer_tick()
        self.poll_timer.interval = 60

    @handle("poll_timer", "tick")
    def poll_timer_tick(self, **event_args):
        if not state.me():
            self.poll_timer.interval = 0
            return
        res = ui.call("poll_counts", _quiet=True)
        if res is not ui.FAIL and res is not None:
            state.set_counts(res)
            self._draw_app_nav()

    def signed_in(self):
        self.start_polling()
        self.refresh(nav=self._nav, public=True)

    # ---------------------------------------------------------------- menus
    def close_menus(self):
        self.me_box.classes["open"] = False
        self.lang_box.classes["open"] = False
        self.shell.classes["nav-open"] = False
        state.set_attr(self.burger, "aria-expanded", "false")
        self._close_groups()

    def _close_groups(self):
        for grp, btn in ((self.grp_work, self.grp_work_btn), (self.grp_engage, self.grp_engage_btn)):
            grp.classes["open"] = False
            state.set_attr(btn, "aria-expanded", "false")

    def group_click(self, event):
        event.stopPropagation()
        which = event.currentTarget.getAttribute("data-grp")
        grp, btn = (self.grp_work, self.grp_work_btn) if which == "work" else (self.grp_engage, self.grp_engage_btn)
        opening = not state.dom(grp).classList.contains("open")
        self._close_groups()
        grp.classes["open"] = opening
        state.set_attr(btn, "aria-expanded", "true" if opening else "false")

    def me_btn_click(self, event):
        event.stopPropagation()
        self.lang_box.classes["open"] = False
        self.me_box.classes["open"] = not state.dom(self.me_box).classList.contains("open")

    def lang_btn_click(self, event):
        event.stopPropagation()
        self.me_box.classes["open"] = False
        self.lang_box.classes["open"] = not state.dom(self.lang_box).classList.contains("open")

    def lang_click(self, event):
        event.preventDefault()
        self.lang_box.classes["open"] = False
        i18n.set_lang(event.currentTarget.getAttribute("data-lang"))

    def burger_click(self, event):
        event.stopPropagation()
        opening = not state.dom(self.shell).classList.contains("nav-open")
        self.shell.classes["nav-open"] = opening
        state.set_attr(self.burger, "aria-expanded", "true" if opening else "false")

    def _close_outside(self, event):
        target = event.target
        if not target.closest(".aa-me"):
            self.me_box.classes["open"] = False
        if not target.closest(".aa-lang"):
            self.lang_box.classes["open"] = False
        if not target.closest(".aa-nav-grp"):
            self._close_groups()
        if target.closest(".aa-nav a") and not target.closest(".aa-nav-more"):
            self.shell.classes["nav-open"] = False  # a link in the phone menu was chosen

    def _key(self, event):
        if getattr(event, "key", None) == "Escape":
            self.close_menus()

    @handle("", "show")
    def form_show(self, **event_args):
        window.document.addEventListener("click", self._outside)
        window.document.addEventListener("keydown", self._keys)

    @handle("", "hide")
    def form_hide(self, **event_args):
        window.document.removeEventListener("click", self._outside)
        window.document.removeEventListener("keydown", self._keys)

    def sign_out_click(self, event):
        anvil.users.logout()
        state.set_me(None)
        state.set_counts({})
        legal.signed_out()
        self.poll_timer.interval = 0
        self.close_menus()
        state.toast(tp("You're signed out. See you soon."))
        router.go("home")
