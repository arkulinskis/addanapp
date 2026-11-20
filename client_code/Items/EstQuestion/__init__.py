from anvil import *

from ._anvil_designer import EstQuestionTemplate
from ...i18n import tp


class EstQuestion(EstQuestionTemplate):
    """One question of the ballpark estimator: a one-tap segmented choice. item = {key, n, q, choices, value}
    (English texts from client_code/estimate.py, translated here). A pick raises x-answer on the RepeatingPanel."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.dom_nodes["n"].textContent = "%d" % it["n"]
        self.dom_nodes["q"].textContent = tp(it["q"])
        self.seg.label = tp(it["q"])
        self.seg.choices = [(v, tp(label)) for v, label in it["choices"]]
        self.seg.selected_value = it["value"]

    @handle("seg", "change")
    def seg_change(self, **event_args):
        if self.parent is not None:
            self.parent.raise_event("x-answer", key=self.item["key"], value=self.seg.selected_value)

    def set_shown(self, shown):
        self.dom_nodes["row"].style.display = "" if shown else "none"
