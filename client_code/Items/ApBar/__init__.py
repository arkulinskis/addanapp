from anvil import *
import anvil.js

from ._anvil_designer import ApBarTemplate
from ... import apps_data


class ApBar(ApBarTemplate):
    """One bar of a bar list (views by app, traffic sources...). item = {key, label, val, parts: [{w, color}], tip, on?,
    pick?}; pick = clickable (raises x-pick(key) on its RepeatingPanel)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        bar = self.dom_nodes["bar"]
        self.dom_nodes["lbl"].textContent = it["label"]
        self.dom_nodes["val"].textContent = it["val"]
        js = apps_data.js()
        if js:
            js.track(self.dom_nodes["track"], it.get("parts") or [])
            js.hoverTip(bar, it.get("tip") or '')
        bar.setAttribute("aria-label", (it.get("tip") or it["label"]).replace("\n", ", "))
        if it.get("on"):
            bar.classList.add("on")
        if it.get("pick"):
            bar.setAttribute("role", "button")
            bar.setAttribute("tabindex", "0")
            bar.addEventListener("click", anvil.js.report_exceptions(self._pick))
            bar.addEventListener("keydown", anvil.js.report_exceptions(self._key))
        else:
            bar.style.cursor = "default"

    def _pick(self, event):
        if self.parent is not None:
            js = apps_data.js()
            if js:
                js.tipHide()
            self.parent.raise_event("x-pick", key=self.item["key"])

    def _key(self, event):
        if event.key in ("Enter", " "):
            event.preventDefault()
            self._pick(event)
