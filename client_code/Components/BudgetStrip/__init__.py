from anvil import *

from ._anvil_designer import BudgetStripTemplate
from ... import i18n, ui


class BudgetStrip(BudgetStripTemplate):
    """The Portal's "no surprises" line: what the client approved and is being built, what they accepted, what waits for
    their OK (quotes and change orders), and hours billed (always 0: fixed prices only). Sums come from the server
    (my_requests -> quotes.budget), so they always match the requests."""

    def __init__(self, **properties):
        self._budget, self._ready = None, False
        super().__init__(**properties)
        i18n.apply(self)
        self._ready = True
        self._draw()

    @property
    def budget(self):
        return self._budget

    @budget.setter
    def budget(self, value):
        self._budget = value
        self._draw()

    def _draw(self):
        if not self._ready:
            return
        b = self._budget or {}
        self.visible = bool(b)
        if not b:
            return
        self.dom_nodes["approved"].textContent = ui.money(b.get("approved") or 0)
        self.dom_nodes["accepted"].textContent = ui.money(b.get("accepted") or 0)
        waiting = b.get("waiting") or 0
        self.dom_nodes["waiting"].textContent = ('-' if waiting < 0 else '') + ui.money(abs(waiting))
        self.dom_nodes["hours"].textContent = str(int(b.get("hours") or 0))
        box = self.dom_nodes["wait_box"]
        if b.get("waiting_n"):
            box.classList.add("on")
        else:
            box.classList.remove("on")
