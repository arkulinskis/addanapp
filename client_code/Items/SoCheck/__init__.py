from anvil import *

from ._anvil_designer import SoCheckTemplate


class SoCheck(SoCheckTemplate):
    """A tick box in the sign-off and accept-delivery dialogs. item = {key, text (shown as is), ok}; a tick updates
    item['ok'] and tells the dialog (x-tick on the RepeatingPanel)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.dom_nodes["text"].textContent = self.item.get("text") or ""
        self.dom_nodes["box"].checked = bool(self.item.get("ok"))

    def set_ok(self, ok):
        self.item["ok"] = bool(ok)
        self.dom_nodes["box"].checked = bool(ok)

    def box_change(self, event):
        self.item["ok"] = bool(self.dom_nodes["box"].checked)
        if self.parent is not None:
            self.parent.raise_event("x-tick")
