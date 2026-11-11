from anvil import *

from ._anvil_designer import ApStatTemplate


class ApStat(ApStatTemplate):
    """One number in the Apps header ("61 projects"). item = {value, label}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.dom_nodes["value"].textContent = self.item["value"]
        self.dom_nodes["label"].textContent = self.item["label"]
