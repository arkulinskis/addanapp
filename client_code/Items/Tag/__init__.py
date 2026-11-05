from anvil import *

from ._anvil_designer import TagTemplate


class Tag(TagTemplate):
    """A small tag (a project's tech or kind). item = {text} (already translated). Plain text, so the old
    `.tags span` styles apply to it alone."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.dom_nodes["tg"].textContent = self.item["text"]
