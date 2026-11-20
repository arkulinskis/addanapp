from anvil import *

from ._anvil_designer import SignoffSampleTemplate
from ... import i18n, signoff_data, state
from ...i18n import tp


class SignoffSample(SignoffSampleTemplate):
    """#signoff/sample: a public sign-off record (the hero's AA-1042 from the demo workspace, signoff_data.SAMPLE),
    so visitors see what "signed off by senior engineers" means before they sign up, plus a try-it accept dialog
    that sends nothing. Linked from the hero's "100% human-reviewed" stamp, method step 04 and guide 03's card."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.card.record = signoff_data.sample_record()
        self.try_result.visible = False
        state.live(self.try_result)
        i18n.apply(self)

    @handle("try_button", "click")
    def try_button_click(self, **event_args):
        from ...Dialogs.AcceptDelivery import AcceptDelivery
        crit = [tp(c) for c in signoff_data.SAMPLE["criteria"]]
        res = alert(AcceptDelivery(criteria=crit, demo=True), buttons=[], role="aa-dialog", large=True)
        if not res:
            return
        if res["action"] == "accept":
            msg = tp("In your workspace this would accept the delivery: {n}/{n} criteria passed, and only then the invoice.",
                     n=len(crit))
        else:
            missing = len([x for x in res["criteria"] if not x])
            msg = tp("In your workspace this would send a change request: {n} criteria not passed yet, written into the message for your engineer.",
                     n=missing)
        self.try_result.text = msg
        self.try_result.visible = True
