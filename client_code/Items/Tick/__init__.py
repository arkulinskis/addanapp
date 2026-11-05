from anvil import *

from ._anvil_designer import TickTemplate


class Tick(TickTemplate):
    """A ticked line in a list (what we built, what's in a guide). item = {text} (already translated)."""

    def __init__(self, **properties):
        super().__init__(**properties)
