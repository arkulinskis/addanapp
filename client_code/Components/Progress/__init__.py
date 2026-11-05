from anvil import *

from ._anvil_designer import ProgressTemplate
from ... import state
from ...i18n import tp


class Progress(ProgressTemplate):
    """A progress bar (blue while in progress, green when done)."""

    def __init__(self, **properties):
        self._value, self._done, self._ready = 0, False, False
        super().__init__(**properties)
        self._ready = True
        state.set_attr(self.bar, "aria-label", tp("Progress"))
        self._draw()

    def _draw(self):
        if not self._ready:
            return
        pct = max(0, min(100, int(self._value or 0)))
        self.fill.style["width"] = "%d%%" % pct
        self.bar.classes["done"] = bool(self._done) or pct >= 100
        state.set_attr(self.bar, "aria-valuenow", pct)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
        self._draw()

    @property
    def done(self):
        return self._done

    @done.setter
    def done(self, v):
        self._done = v
        self._draw()
