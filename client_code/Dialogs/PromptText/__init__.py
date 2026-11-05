from anvil import *

from ._anvil_designer import PromptTextTemplate
from ... import i18n, state
from ...i18n import tp


class PromptText(PromptTextTemplate):
    """Ask for a few words (a client asking for changes). alert() returns the text, or None if cancelled."""

    def __init__(self, title, text='', placeholder='', ok=None, required=True, **properties):
        super().__init__(**properties)
        self.required = required
        self.heading.text, self.intro.text = title, text
        self.body.placeholder = placeholder
        state.set_control_attr(self.body, "aria-label", title)
        i18n.apply(self)
        self.ok_button.text = ok or tp('Send')

    @handle("ok_button", "click")
    def ok_button_click(self, **event_args):
        body = (self.body.text or '').strip()
        if self.required and len(body) < 3:
            self.error.text = tp('Please add a few words.')
            self.error.visible = True
            return
        self.raise_event("x-close-alert", value=body)

    @handle("cancel_button", "click")
    def cancel_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)

    @handle("", "show")
    def form_show(self, **event_args):
        self.body.focus()
