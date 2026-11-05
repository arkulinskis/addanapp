from anvil import *

from ._anvil_designer import NewForClientTemplate
from ... import i18n, ui


class NewForClient(NewForClientTemplate):
    """Console: create a request on a client's behalf. alert() returns the new request's id, or None."""

    def __init__(self, clients, client_id=None, **properties):
        super().__init__(**properties)
        self.form.budgets = False
        self.client_dd.items = [((c.get("company") + " · " if c.get("company") else "") + c["name"], c["id"]) for c in clients]
        if client_id:
            self.client_dd.selected_value = client_id
        i18n.apply(self)

    @handle("ok_button", "click")
    def ok_button_click(self, **event_args):
        data = self.form.collect()
        msg = self.form.validate(data)
        self.form.show_error(msg)
        if msg:
            return
        res = ui.call('admin_create_request', self.client_dd.selected_value, data)
        if res is not ui.FAIL:
            self.raise_event("x-close-alert", value=res)

    @handle("cancel_button", "click")
    def cancel_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
