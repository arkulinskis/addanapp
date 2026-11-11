from anvil import *

from ._anvil_designer import ApListBtnTemplate
from ... import state


class ApListBtn(ApListBtnTemplate):
    """A row in a side list (Posts, Biz dev): item = {key, label, cnt?, on?, done?, dot?: ok|bad|'', title?} or a group
    heading {grp: text}. Raises x-pick(key) on its RepeatingPanel."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        if it.get('grp'):
            self.dom_nodes["grp"].textContent = it['grp']
            self.dom_nodes["btn"].remove()
            return
        self.dom_nodes["grp"].remove()
        b = self.dom_nodes["btn"]
        b.setAttribute("data-key", it['key'])
        if it.get('on'):
            b.classList.add("on")
            b.setAttribute("aria-current", "true")
        if it.get('done'):
            b.classList.add("all-done")
        if it.get('title'):
            b.setAttribute("title", it['title'])
        dot = self.dom_nodes["dot"]
        if it.get('dot') is None:
            dot.remove()
        elif it['dot']:
            dot.classList.add(it['dot'])
        self.dom_nodes["nm"].textContent = it['label']
        self.dom_nodes["cnt"].textContent = it.get('cnt') or ''

    def btn_click(self, event):
        if self.parent is not None:
            self.parent.raise_event("x-pick", key=self.item['key'])
            state.refocus_later(self.parent, self.item['key'])
