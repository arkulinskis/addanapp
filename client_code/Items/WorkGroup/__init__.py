from anvil import *

from ._anvil_designer import WorkGroupTemplate


class WorkGroup(WorkGroupTemplate):
    """A category of the Work index: its heading and its projects. item = {key, label, keys, first}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        head = self.dom_nodes["head"]
        head.setAttribute("data-cat", it["key"])
        if it.get("first"):
            head.classList.add("first")
        self.dom_nodes["label"].textContent = it["label"]
        self.dom_nodes["n"].textContent = "%02d" % len(it["keys"])
        self.rows.items = [{"key": k, "cat": it["key"]} for k in it["keys"]]
