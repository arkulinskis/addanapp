from anvil import *

from ._anvil_designer import ApNoteGroupTemplate


class ApNoteGroup(ApNoteGroupTemplate):
    """One kind of notification with its notes. item = {type: {id, name, desc, icon}, notes}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        t, notes = self.item["type"], self.item["notes"]
        self.icon.classes["ic-" + (t.get('icon') or 'bell')] = True
        self.dom_nodes["name"].textContent = t['name']
        self.dom_nodes["n"].textContent = str(len(notes))
        self.dom_nodes["desc"].textContent = t['desc']
        self.notes.items = notes
