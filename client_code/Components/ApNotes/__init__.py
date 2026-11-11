from anvil import *

from ._anvil_designer import ApNotesTemplate
from ... import apps_data, state


class ApNotes(ApNotesTemplate):
    """#apps/notes: everything that needs the user or Claude (refresh problems, schema mismatches, sites down, queued
    changes, links to finish, branches, legal, SEO, standard, videos), grouped by type, each with what it means, a
    prompt to paste into Claude Code and quick actions. Dismissed ones are hidden until their details change."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.type = state.store_get('apps.noteType', '')
        self.chips.add_event_handler("x-pick", self._pick)
        self.show_dismissed.text = "Show dismissed"
        self.redraw()

    def _pool(self):
        b = apps_data.board() or {}
        q = apps_data.query()
        notes = [n for n in b.get('notes') or [] if not q or not n.get('key') or apps_data.project(n['key']) in apps_data.visible()]
        active = [n for n in notes if not apps_data.is_dismissed(n)]
        return notes, active

    def redraw(self, key=None):
        b = apps_data.board() or {}
        notes, active = self._pool()
        pool = notes if self.show_dismissed.checked else active
        hidden = len(notes) - len(active)
        types = b.get('note_types') or []
        if self.type and not any(n['type'] == self.type for n in pool):
            self.type = ''
        self.chips.items = [{"key": "", "label": "All", "count": len(pool), "on": not self.type}] + [
            {"key": t['id'], "label": t['name'], "count": len([n for n in pool if n['type'] == t['id']]), "on": self.type == t['id']}
            for t in types if any(n['type'] == t['id'] for n in pool)]
        shown = [n for n in pool if not self.type or n['type'] == self.type]
        self.shown = shown
        self.copy_all_button.visible = bool(shown)
        self.copy_all_button.text = "Copy all %d for Claude" % len(shown)
        self.show_dismissed.visible = hidden > 0
        self.show_dismissed.text = "Show %d dismissed" % hidden
        self.groups.items = [{"type": t, "notes": [n for n in shown if n['type'] == t['id']]} for t in types
                             if any(n['type'] == t['id'] for n in shown)]
        self.none.visible = not shown
        self.dom_nodes["none_p"].textContent = ("%d dismissed." % hidden) if hidden else "Every app is in good shape."

    def _pick(self, key, **event_args):
        self.type = key
        state.store_set('apps.noteType', key)
        self.redraw()

    @handle("show_dismissed", "change")
    def show_dismissed_change(self, **event_args):
        self.redraw()

    @handle("copy_all_button", "click")
    def copy_all_button_click(self, **event_args):
        text = "\n\n".join("%d. %s" % (i + 1, n['prompt']) for i, n in enumerate(self.shown))
        apps_data.copy(text, "Copied %d prompts" % len(self.shown))
