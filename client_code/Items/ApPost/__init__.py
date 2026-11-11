from anvil import *

from ._anvil_designer import ApPostTemplate
from ... import apps_data


class ApPost(ApPostTemplate):
    """A suggested LinkedIn post or YouTube script: Copy + a Posted / Published tick (the first tick also ticks the
    app's LinkedIn / YouTube step). Notes for the user (picture ideas) show under it and aren't copied.
    item = {key, post: {id, kind, title, text, note}, on: date or '', closed}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it, x = self.item, self.item["post"]
        yt = x.get('kind') == 'youtube'
        on = it.get("on")
        if on:
            self.dom_nodes["art"].classList.add("posted")
        label = ("▶ Video to sell" if x['id'] == 'yt-sell' else "▶ Video to explain") if yt else "LinkedIn " + x['id'][2:]
        self.dom_nodes["label"].textContent = label
        self.dom_nodes["angle"].textContent = x.get('title') or ''
        self.dom_nodes["copy"].setAttribute("aria-label", "Copy " + label)
        tick = self.dom_nodes["tick"]
        tick.checked = bool(on)
        self.dom_nodes["tick_lbl"].textContent = ("Published" if yt else "Posted") + (" " + on if isinstance(on, str) and on else "")
        text = x.get('text') or ''
        if yt:
            words = len(text.split())
            self.dom_nodes["summary"].textContent = "Script · about %d words (~%d min)" % (words, max(1, round(words / 150)))
            self.dom_nodes["text_in"].textContent = text
            if not (on or it.get("closed")):
                self.dom_nodes["fold"].setAttribute("open", "")
            self.dom_nodes["text"].remove()
        else:
            self.dom_nodes["text"].textContent = text
            self.dom_nodes["fold"].remove()
        note = self.dom_nodes["note"]
        if x.get('note'):
            note.textContent = "💡 " + x['note']
        else:
            note.remove()

    def copy_click(self, event):
        x = self.item["post"]
        apps_data.copy(x.get('text'), "Script copied" if x.get('kind') == 'youtube' else "Post copied")

    def tick_change(self, event):
        apps_data.set_posted(self.item["key"], self.item["post"]["id"], bool(self.dom_nodes["tick"].checked))
