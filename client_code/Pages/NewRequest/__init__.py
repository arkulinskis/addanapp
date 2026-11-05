from anvil import *

from ._anvil_designer import NewRequestTemplate
from ... import i18n, router, state, ui
from ...i18n import tp


class NewRequest(NewRequestTemplate):
    """#new: a client describes a request; it lands in the console and the client goes to its page."""

    def __init__(self, **properties):
        super().__init__(**properties)
        i18n.apply(self)
        self.submit_button.text = tp('Submit request') + ' →'

    @handle("submit_button", "click")
    def submit_button_click(self, **event_args):
        data = self.form.collect()
        msg = self.form.validate(data)
        self.form.show_error(msg)
        if msg:
            return
        self.submit_button.enabled = False
        self.submit_button.text = tp('Submitting…')
        res = ui.call('create_request', data)
        self.submit_button.enabled = True
        self.submit_button.text = tp('Submit request') + ' →'
        if res is ui.FAIL:
            return
        state.toast(tp("Request submitted. An engineer will scope it shortly."), "ok")
        router.go('r/' + res)
