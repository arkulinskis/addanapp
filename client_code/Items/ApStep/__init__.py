from anvil import *

from ._anvil_designer import ApStepTemplate
from ... import apps_data

WORD = {'done': 'done', 'na': 'not needed', 'todo': 'to do'}


class ApStep(ApStepTemplate):
    """One checklist step: a button that cycles empty -> done -> not needed -> empty.
    item = {key, id, label, v, auto, auto_note}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        b = self.dom_nodes["btn"]
        if it["v"] != 'todo':
            b.classList.add(it["v"])
        b.setAttribute("data-step", it["id"])
        b.setAttribute("aria-label", "%s: %s%s. Click to change." % (it["label"], WORD[it["v"]], " (found automatically)" if it["auto"] else ""))
        self.dom_nodes["mark"].textContent = {'done': '✓', 'na': '–'}.get(it["v"], '')
        self.dom_nodes["label"].textContent = it["label"]
        tag = self.dom_nodes["auto"]
        if it["auto"]:
            tag.setAttribute("title", it["auto_note"] or "Found automatically")
        else:
            tag.remove()

    def btn_click(self, event):
        apps_data._d["refocus"] = self.item["id"]
        apps_data.tick(self.item["key"], self.item["id"])
