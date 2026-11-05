"""App-wide client state and small helpers every form uses.

    state.me()                 the signed-in person as a dict (serial.me on the server), or None
    state.set_me(me)           after sign in / sign out / a profile change
    state.refresh_me()         ask the server again (also tells it which language to email in)
    state.counts()             unread counts for the header {unread, leads}; set_counts(c)
    state.is_admin(), home_route()   "admin" for consultants, "portal" for clients, "home" for visitors
    state.toast(msg, kind)     a short notification; kind "ok" or "error"
    state.set_attr(c, name, v) an HTML attribute on a component's root (href on a named <a>, aria-label ...)
    state.set_control_attr     the same on the real <input>/<button> inside (autocomplete, aria-pressed, type)
    state.heading(label, 1)    a Label that screen readers treat as a heading; state.live(label) reads it out on change
    state.dom(component)       the component's DOM node
"""
import anvil.js
import anvil.server
import anvil.users
from anvil import Notification
from anvil.js import window

_state: dict = {"me": None, "counts": {}, "after": ""}


def me():
    return _state["me"]


def set_me(value):
    _state["me"] = value or None


def logged_in():
    return anvil.users.get_user() is not None


def is_admin():
    m = _state["me"]
    return bool(m and m.get("is_admin"))


def home_route():
    if not _state["me"]:
        return "home"
    return "admin" if is_admin() else "portal"


def refresh_me():
    """Who is signed in, from the server (None for visitors). Also records the visitor's language for emails."""
    from . import i18n, legal, ui
    if not logged_in():
        set_me(None)
        return None
    res = ui.call("get_me", i18n.lang, _quiet=True)
    if res is not ui.FAIL:
        set_me(res)
    legal.refresh_soon()  # Privacy & Terms: records the sign-up tick, or reminds people to review
    return _state["me"]


def counts():
    return _state["counts"]


def set_counts(c):
    _state["counts"] = c or {}


def remember_after(route):
    _state["after"] = route or ""


def take_after():
    r = _state["after"]
    _state["after"] = ""
    return r


def need_sign_in():
    """A server call said "Please sign in": remember where we were and open the sign-in box."""
    from . import router
    remember_after(router.current())
    router.go("login")


def toast(message, kind=None):
    timeout = 6.5 if kind == "error" else 3.5
    try:
        n = Notification(message, timeout=timeout, role=kind)
    except TypeError:  # the open-source App Server 1.18 has no `role` yet: its older `style` gives the same classes
        n = Notification(message, timeout=timeout, style={"ok": "success", "error": "danger"}.get(kind or "", "info"))
    n.show()


def dom(component):
    return anvil.js.get_dom_node(component)


def set_attr(component, name, value):
    """Set an HTML attribute (href, aria-label, title) on a component's root element.
    (HtmlComponent.attrs does this on hosted Anvil, but the open-source App Server 1.18 doesn't have it yet.)"""
    node = anvil.js.get_dom_node(component)
    if value is None:
        node.removeAttribute(name)
    else:
        node.setAttribute(name, str(value))


def store_get(key, default=None):
    v = window.UI.store.get(key, None)
    return default if v is None else v


def store_set(key, value):
    window.UI.store.set(key, value)


def feedback():
    """Open the Prepsto feedback panel (the app's only feedback channel)."""
    if window.get("Prepsto") and window.Prepsto.open:
        window.Prepsto.open()
    else:
        window.open("https://prepsto.com/#f/e4xsnwm", "_blank", "noopener")


# ---------------------------------------------------------------- accessibility (WCAG AA)
def control(component):
    """The real <input>, <textarea>, <select> or <button> inside an Anvil component (for ARIA attributes and focus)."""
    node = anvil.js.get_dom_node(component)
    if str(node.tagName) in ("INPUT", "TEXTAREA", "SELECT", "BUTTON"):
        return node
    return node.querySelector("input, textarea, select, button") or node


def focus(component):
    """Keyboard focus on a component's real control (Anvil's Button has no focus())."""
    getattr(control(component), "focus")()


def set_control_attr(component, name, value):
    """An HTML attribute on the component's real control: autocomplete on a TextBox, aria-pressed on a Button."""
    el = control(component)
    if value is None:
        el.removeAttribute(name)
    else:
        el.setAttribute(name, str(value))


def heading(component, level=1):
    """Make a Label a real heading for screen readers (an Anvil Label renders as a <div>)."""
    set_attr(component, "role", "heading")
    set_attr(component, "aria-level", level)


def live(component, urgent=False):
    """Have screen readers read a Label out whenever its text changes."""
    set_attr(component, "role", "alert" if urgent else "status")


def refocus_later(component, key):
    """After a click redraws a RepeatingPanel, put the keyboard focus back on the button with the same data-key
    (keyboard users keep their place instead of landing at the top of the page)."""
    def again():
        el = anvil.js.get_dom_node(component).querySelector('[data-key="%s"]' % window.CSS.escape(str(key)))
        if el:
            getattr(el, "focus")()
    window.setTimeout(again, 0)


def date_box(box):
    """A TextBox that shows the browser's date picker (the value stays 'YYYY-MM-DD' text)."""
    set_control_attr(box, "type", "date")
