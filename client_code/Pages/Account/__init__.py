from anvil import *
import anvil.users

from ._anvil_designer import AccountTemplate
from ... import i18n, router, state, ui
from ...i18n import tp


class Account(AccountTemplate):
    """#account: name, company, phone, email notifications, password reset and the language."""

    def __init__(self, **properties):
        super().__init__(**properties)
        me = state.refresh_me() or {}
        self.name_box.text = me.get('name') or ''
        self.company_box.text = me.get('company') or ''
        self.email_box.text = me.get('email') or ''
        self.phone_box.text = me.get('phone') or ''
        self.dom_nodes["notify"].checked = bool(me.get('email_notifications'))
        self.lang_dd.items = [(name, code) for code, name in i18n.LANGS]
        self.lang_dd.selected_value = i18n.lang
        for box, auto in ((self.name_box, "name"), (self.company_box, "organization"), (self.phone_box, "tel")):
            state.set_control_attr(box, "autocomplete", auto)
        i18n.apply(self)

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        res = ui.call('update_me', {'name': (self.name_box.text or '').strip(), 'company': (self.company_box.text or '').strip(),
                                    'phone': (self.phone_box.text or '').strip(),
                                    'email_notifications': bool(self.dom_nodes["notify"].checked)})
        if res is not ui.FAIL:
            state.set_me(res)
            sh = router.shell()
            if sh is not None:
                sh.refresh(nav='account', public=False)
            state.toast(tp("Saved."), "ok")

    @handle("reset_button", "click")
    def reset_button_click(self, **event_args):
        try:
            anvil.users.send_password_reset_email((state.me() or {}).get('email') or '')
            state.toast(tp("Check your inbox for a password reset link."), "ok")
        except Exception as e:
            state.toast(str(e), "error")

    @handle("lang_dd", "change")
    def lang_dd_change(self, **event_args):
        i18n.set_lang(self.lang_dd.selected_value)
