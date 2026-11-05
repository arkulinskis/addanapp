from anvil import *

from ._anvil_designer import TileTemplate
from ... import state


class Tile(TileTemplate):
    """A count tile that filters the list below it (portal, console). item = {key, value, label, color, on, attn}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.dom_nodes["v"].textContent = str(it["value"])
        self.dom_nodes["label"].textContent = it["label"]
        self.dot.style["background"] = it["color"]
        self.btn.classes["on"] = bool(it.get("on"))
        self.btn.classes["attn"] = bool(it.get("attn"))
        state.set_attr(self.btn, "aria-pressed", "true" if it.get("on") else "false")
        state.set_attr(self.btn, "data-key", it["key"])

    def btn_click(self, event):
        panel = self.parent
        if panel is not None:
            panel.raise_event("x-pick", key=self.item["key"])
            state.refocus_later(panel, self.item["key"])
