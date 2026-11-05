from anvil import *

from ._anvil_designer import LeadCardTemplate
from ... import i18n, router, state, ui
from ...i18n import tp

LEAD_STATUSES = [('new', tp('New')), ('contacted', tp('Contacted')), ('won', tp('Won')), ('lost', tp('Lost')), ('archived', tp('Archived'))]


class LeadCard(LeadCardTemplate):
    """A website lead (a project brief, or someone who asked for the free guides): status, reply, delete.
    item = a lead dict from admin_leads."""

    def __init__(self, **properties):
        super().__init__(**properties)
        lead = self.item
        guide = lead['source'].startswith('guide')
        subj = 'Re: your Addanapp guides' if guide else 'Re: your Addanapp project brief'  # goes to the prospect: English
        mailto = "mailto:%s?subject=%s" % (lead["email"], subj)
        self.dom_nodes["name"].textContent = lead["name"]
        ui.chip(self.c_new, tp("New") if lead["status"] == "new" else '', 'accent')
        self.dom_nodes["when"].textContent = ui.ago(lead["created"])
        email = self.dom_nodes["email"]
        email.textContent = lead["email"]
        email.setAttribute("href", mailto)
        self.dom_nodes["company"].textContent = (" · " + lead["company"]) if lead["company"] else ''
        ui.chip(self.c_guide, tp('Free guides') if guide else '', 'ai')
        ui.chip(self.c_tips, tp('Wants tips') if lead['source'] == 'guide+news' else '', 'human')
        ui.chip(self.c_kind, tp(lead["kind"]) if lead["kind"] else '', 'outline')
        ui.chip(self.c_budget, tp('Budget: {budget}', budget=tp(lead["budget"])) if lead["budget"] else '', 'outline')
        self.msg.text = lead["message"]
        self.status_dd.items = ui.dd_items(LEAD_STATUSES)
        self.status_dd.selected_value = lead["status"]
        state.set_control_attr(self.status_dd, "aria-label", tp('Lead status'))
        self.dom_nodes["reply"].setAttribute("href", mailto)
        i18n.apply(self)

    @handle("status_dd", "change")
    def status_dd_change(self, **event_args):
        if ui.call('admin_update_lead', self.item['id'], self.status_dd.selected_value) is not ui.FAIL:
            state.toast(tp("Lead updated."), "ok")
            sh = router.shell()
            if sh is not None:
                sh.poll_timer_tick()

    @handle("delete_button", "click")
    def delete_button_click(self, **event_args):
        if confirm(tp("Delete this lead permanently?"), buttons=[(tp('Cancel'), False), (tp('Delete'), True)]):
            if ui.call('admin_update_lead', self.item['id'], None, True) is not ui.FAIL:
                self.parent.raise_event("x-changed")
