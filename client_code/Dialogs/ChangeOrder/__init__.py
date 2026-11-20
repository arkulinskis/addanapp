from anvil import *

from ._anvil_designer import ChangeOrderTemplate
from ... import i18n, state, ui
from ...i18n import tp


def delta_text(delta):
    """+$600 / -$400 in the visitor's language."""
    d = int(round(delta or 0))
    return ('+' if d >= 0 else '-') + ui.money(abs(d))


class ChangeOrder(ChangeOrderTemplate):
    """Consultant: propose a change of price and/or ETA on a request whose quote the client approved (it's locked).
    alert() returns the request payload once sent, or None."""

    def __init__(self, request, **properties):
        super().__init__(**properties)
        r = request
        self.request_id = r["id"]
        self.before = r.get("quote_amount") or 0
        self.eta_before = r.get("eta")
        self.now_label.text = tp("Approved now: {amount}{eta}", amount=ui.money(self.before),
                                 eta=(' · ' + tp('ETA {date}', date=ui.fmt_date(self.eta_before))) if self.eta_before else '')
        state.date_box(self.eta_box)
        state.set_control_attr(self.amount_box, "min", 0)
        state.set_control_attr(self.amount_box, "step", 50)
        state.live(self.preview_label)
        self.amount_box.text = str(int(self.before))
        self.eta_box.text = ui.date_iso(self.eta_before) if self.eta_before else ''
        i18n.apply(self)
        self._preview()

    def _amount(self):
        v = self.amount_box.text
        try:
            return float(v) if v not in (None, '') else None
        except (TypeError, ValueError):
            return None

    def _preview(self, **event_args):
        amount, eta = self._amount(), ui.parse_date(self.eta_box.text)
        parts = []
        if amount is not None and int(round(amount)) != int(round(self.before)):
            parts.append(tp("{delta} (new total {total})", delta=delta_text(amount - self.before), total=ui.money(amount)))
        if eta and eta != self.eta_before:
            parts.append(tp("new ETA {date}", date=ui.fmt_date(eta)))
        self.preview_label.text = (tp("The client will see: change order {what}.", what=", ".join(parts)) if parts
                                   else tp("Change the price or the ETA to make a change order."))

    @handle("amount_box", "change")
    def amount_box_change(self, **event_args):
        self._preview()

    @handle("eta_box", "change")
    def eta_box_change(self, **event_args):
        self._preview()

    @handle("send_button", "click")
    def send_button_click(self, **event_args):
        amount = self._amount()
        if amount is None:
            self.error.text = tp("Enter the new total price.")
            self.error.visible = True
            return
        reason = (self.reason_box.text or '').strip()
        if len(reason) < 10:
            self.error.text = tp("Explain the change in a sentence: the client approves it on that basis.")
            self.error.visible = True
            return
        self.error.visible = False
        self.send_button.enabled = False
        res = ui.call('admin_send_change_order', self.request_id, amount, ui.parse_date(self.eta_box.text), reason)
        self.send_button.enabled = True
        if res is not ui.FAIL:
            self.raise_event("x-close-alert", value=res)

    @handle("cancel_button", "click")
    def cancel_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
