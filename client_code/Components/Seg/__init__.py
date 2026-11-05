from anvil import *

from ._anvil_designer import SegTemplate
from ... import state


class Seg(SegTemplate):
    """Segmented choice: a row of buttons, one chosen (the old .seg). choices = [(value, label)]."""

    def __init__(self, **properties):
        self._choices, self._value, self._label, self._ready = [], "", "", False
        super().__init__(**properties)
        self.options.add_event_handler("x-pick", self._pick)
        self._ready = True
        self._draw()

    def _draw(self):
        if not self._ready:
            return
        self.options.items = [{"value": v, "label": lbl, "on": v == self._value} for v, lbl in (self._choices or [])]
        if self._label:
            state.set_attr(self.group, "aria-label", self._label)

    def _pick(self, value, **event_args):
        self._value = value
        self._draw()
        self.raise_event("change")

    @property
    def choices(self):
        return self._choices

    @choices.setter
    def choices(self, v):
        self._choices = list(v or [])
        self._draw()

    @property
    def selected_value(self):
        return self._value

    @selected_value.setter
    def selected_value(self, v):
        self._value = v or ""
        self._draw()

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, v):
        self._label = v or ""
        self._draw()
