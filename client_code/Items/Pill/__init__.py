from anvil import *

from ._anvil_designer import PillTemplate
from ... import state


class Pill(PillTemplate):
    """A filter / view button in a row of pills (.pills, .lp-filter, the leads filter).
    item = {key, label, on, count?, icon?, cls?} -> raises x-pick(key) on its RepeatingPanel."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.dom_nodes["label"].textContent = it["label"]
        has_n = it.get("count") is not None
        self.n.visible = has_n
        if has_n:
            self.dom_nodes["n"].textContent = str(it["count"])
        ic = it.get("icon")
        self.icon.visible = bool(ic)
        if ic:
            self.icon.classes["ic-" + ic] = True
        self.btn.classes["on"] = bool(it.get("on"))
        for c in (it.get("cls") or "").split():
            self.btn.classes[c] = True
        state.set_attr(self.btn, "aria-pressed", "true" if it.get("on") else "false")
        state.set_attr(self.btn, "data-key", it["key"])

    def btn_click(self, event):
        panel = self.parent
        if panel is not None:
            panel.raise_event("x-pick", key=self.item["key"])
            state.refocus_later(panel, self.item["key"])
