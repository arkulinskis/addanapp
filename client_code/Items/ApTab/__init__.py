from anvil import *

from ._anvil_designer import ApTabTemplate


class ApTab(ApTabTemplate):
    """One view tab of the Apps board. item = {href, label, on, count}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        a = self.dom_nodes["link"]
        a.setAttribute("href", it["href"])
        if it.get("on"):
            a.classList.add("on")
            a.setAttribute("aria-current", "page")
        self.dom_nodes["label"].textContent = it["label"]
        n = self.dom_nodes["count"]
        if it.get("count"):
            n.textContent = str(it["count"])
            n.setAttribute("aria-label", "%d to look at" % it["count"])
        else:
            n.remove()
