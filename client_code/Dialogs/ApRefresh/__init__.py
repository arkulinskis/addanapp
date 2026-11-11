from anvil import *

from ._anvil_designer import ApRefreshTemplate
from ... import apps_data

NOTES = {'hero': 'About 20 seconds per app (only apps whose site answers)',
         'schema': 'Needs the site to answer',
         'live': 'Also tries the <name>.anvil.app guess for apps with no link'}


class ApRefresh(ApRefreshTemplate):
    """Choose what the PC checks: GitHub, live site + SEO, database schema, mentions, the standard audit, a new
    screenshot. key = one app, or None for every app. alert() returns the ticked action ids, or None."""

    def __init__(self, key=None, **properties):
        super().__init__(**properties)
        b = apps_data.board() or {}
        acts = b.get('actions') or {}
        p = apps_data.project(key) if key else None
        self.heading.text = "Refresh " + (p['name'] if p else "every app")
        self.intro.text = "Tick what to check. Unticked parts keep what the last check found. Your PC does the work."
        defaults = list(acts.keys()) if key else (b.get('all_default') or [])
        self.checks: dict = {}
        for aid, label in acts.items():
            cb = CheckBox(text=label + (" (%s)" % NOTES[aid] if aid in NOTES else ""), checked=aid in defaults)
            self.checks[aid] = cb
            self.boxes.add_component(cb)

    @handle("all_button", "click")
    def all_button_click(self, **event_args):
        for cb in self.checks.values():
            cb.checked = True

    @handle("none_button", "click")
    def none_button_click(self, **event_args):
        for cb in self.checks.values():
            cb.checked = False

    @handle("ok_button", "click")
    def ok_button_click(self, **event_args):
        picked = [aid for aid, cb in self.checks.items() if cb.checked]
        if not picked:
            self.error.text = "Tick at least one thing to check."
            self.error.visible = True
            return
        self.raise_event("x-close-alert", value=picked)

    @handle("cancel_button", "click")
    def cancel_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
