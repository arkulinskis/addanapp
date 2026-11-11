from anvil import *
from anvil.js import window

from ._anvil_designer import ApNoteTemplate
from ... import apps_data


class ApNote(ApNoteTemplate):
    """One notification: the app, what's wrong, the prompt for Claude Code, quick actions, Dismiss / Bring back.
    item = a note from apps_core.notes (desc is HTML the server built from escaped text)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        n = self.item
        gone = apps_data.is_dismissed(n)
        box = self.dom_nodes["box"]
        if gone:
            box.classList.add("gone")
        app = self.dom_nodes["app"]
        stage = self.dom_nodes["stage"]
        if n.get('key') and n.get('name'):
            app.textContent = n['name']
            app.setAttribute("href", "#app/" + window.encodeURIComponent(n['key']))
            stage.textContent = n.get('stage_name') or ''
            stage.style.setProperty("--c", apps_data.color(n.get('stage')))
        else:
            app.remove()
            stage.remove()
        self.dom_nodes["title"].textContent = n.get('title') or ''
        self.dom_nodes["desc"].innerHTML = n.get('desc') or ''  # built server-side from escaped text (apps_core.notes)
        self.dom_nodes["prompt"].textContent = n['prompt']
        acts = [dict(a, key=n.get('key') or '') for a in n.get('acts') or []]
        if n.get('key'):
            acts = [{"label": "Refresh", "do": "refresh", "key": n['key']}] + acts
        self.acts.items = acts
        self.dismiss_button.text = "Bring back" if gone else "Dismiss"

    @handle("copy_button", "click")
    def copy_button_click(self, **event_args):
        apps_data.copy(self.item['prompt'], "Copied: paste it into Claude Code")

    @handle("dismiss_button", "click")
    def dismiss_button_click(self, **event_args):
        apps_data.dismiss(self.item)
