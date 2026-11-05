from anvil import *

from ._anvil_designer import SegOptionTemplate
from ... import state


class SegOption(SegOptionTemplate):
    """One button of a segmented choice. item = {value, label, on}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.dom_nodes["label"].textContent = self.item["label"]
        self.btn.classes["on"] = bool(self.item.get("on"))
        state.set_attr(self.btn, "data-key", self.item["value"])

    def btn_click(self, event):
        value = self.item["value"]
        seg = self.parent
        if seg is not None:
            seg.raise_event("x-pick", value=value)
            state.refocus_later(seg, value)
