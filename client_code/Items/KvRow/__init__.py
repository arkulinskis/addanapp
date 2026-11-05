from anvil import *

from ._anvil_designer import KvRowTemplate


class KvRow(KvRowTemplate):
    """A label / value line in a request's Details card. item = {k, v, first}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.dom_nodes["k"].textContent = self.item["k"]
        self.dom_nodes["v"].textContent = self.item["v"]
        if self.item.get("first"):
            self.dom_nodes["row"].classList.add("first")
