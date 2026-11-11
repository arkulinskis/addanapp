from anvil import *

from ._anvil_designer import ApKitTitleTemplate
from ... import apps_data


class ApKitTitle(ApKitTitleTemplate):
    """One suggested YouTube title with its length and Copy. item = {i, text} (the first one is recommended)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.dom_nodes["mark"].textContent = "⭐" if it["i"] == 0 else "·"
        self.dom_nodes["text"].textContent = it["text"]
        self.dom_nodes["n"].textContent = "%d chars" % len(it["text"])
        self.dom_nodes["copy"].setAttribute("aria-label", "Copy title %d" % (it["i"] + 1))

    def copy_click(self, event):
        apps_data.copy(self.item["text"], "Title copied")
