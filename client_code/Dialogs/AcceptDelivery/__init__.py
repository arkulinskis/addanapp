from anvil import *

from ._anvil_designer import AcceptDeliveryTemplate
from ... import i18n, state
from ...i18n import tp


class AcceptDelivery(AcceptDeliveryTemplate):
    """Client: accept a delivery criterion by criterion. Every criterion ticked -> "Accept delivery"; any left unticked
    turns the button into "Request changes" with those criteria written into the message.
    alert() returns {'action': 'accept' | 'changes', 'criteria': [bool], 'comment': str}, or None if cancelled.
    The public sample (#signoff/sample) opens it with demo=True: nothing is sent."""

    def __init__(self, criteria, demo=False, **properties):
        super().__init__(**properties)
        self.demo = demo
        self.crits.items = [{"key": str(i), "text": c, "ok": False} for i, c in enumerate(criteria or [])]
        self._auto = ""
        self.comment_box.placeholder = tp("e.g. The refund email should go to the guest, not the manager.")
        state.set_control_attr(self.comment_box, "aria-label", tp("What should change?"))
        state.live(self.count_label)
        self.crits.add_event_handler("x-tick", self._update)
        i18n.apply(self)
        self._update()

    def _items(self):
        return [getattr(f, "item") for f in self.crits.get_components()]

    def _update(self, **event_args):
        items = self._items()
        missing = [c["text"] for c in items if not c["ok"]]
        done = len(items) - len(missing)
        self.count_label.text = tp("{ok} of {n} criteria ticked", ok=done, n=len(items))
        all_ok = not missing
        self.changes_part.visible = not all_ok and done > 0
        self.ok_button.enabled = done > 0  # nothing ticked yet: nothing tested, nothing to send
        if all_ok or done == 0:
            self.ok_button.text = tp("Accept delivery")
            self.ok_button.role = ["aa-btn", "green"]
        else:
            self.ok_button.text = tp("Request changes ({n})", n=len(missing))
            self.ok_button.role = ["aa-btn", "accent"]
        auto = tp("Not passed yet:") + "\n" + "\n".join("- " + m for m in missing) + "\n\n" if missing else ""
        text = self.comment_box.text or ""
        if text == self._auto or not text.strip():
            self.comment_box.text = auto
        elif self._auto and text.startswith(self._auto):
            self.comment_box.text = auto + text[len(self._auto):]
        self._auto = auto

    @handle("ok_button", "click")
    def ok_button_click(self, **event_args):
        items = self._items()
        ticks = [bool(c["ok"]) for c in items]
        if all(ticks):
            self.raise_event("x-close-alert", value={"action": "accept", "criteria": ticks, "comment": ""})
            return
        comment = (self.comment_box.text or "").strip()
        if len(comment) < 3:
            self.error.text = tp("Please add a few words.")
            self.error.visible = True
            return
        self.raise_event("x-close-alert", value={"action": "changes", "criteria": ticks, "comment": comment})

    @handle("cancel_button", "click")
    def cancel_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
