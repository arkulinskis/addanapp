from anvil import *
from anvil.js import window

from ._anvil_designer import ApStepsTemplate
from ... import apps_data


class ApSteps(ApStepsTemplate):
    """An app's checklist, one box per stage; a click cycles a step: empty -> done -> not needed -> empty.
    show(project) draws it; after a tick the page redraws and the keyboard focus returns to the same step."""

    def __init__(self, project=None, **properties):
        super().__init__(**properties)
        if project:
            self.show(project)

    def show(self, p):
        b = apps_data.board() or {}
        self.phases.items = [{"phase": ph, "project": p} for ph in b.get('phases') or []]
        again = apps_data._d.get("refocus")
        if again:
            apps_data._d["refocus"] = None

            def focus():
                el = self.dom_nodes["box"].querySelector('[data-step="%s"]' % again)
                if el:
                    getattr(el, "focus")()
            window.setTimeout(focus, 0)
