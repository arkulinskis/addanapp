from anvil import *

from ._anvil_designer import PersonCardTemplate
from ... import i18n, ui
from ...i18n import tp


class PersonCard(PersonCardTemplate):
    """A client (or consultant) in the console: contact, activity, numbers, and what a consultant can do.
    item = a person dict from admin_clients (+ _me: it's the signed-in consultant)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        p = self.item
        self.avatar.person = p
        self.dom_nodes["name"].textContent = p["name"]
        self.dom_nodes["company"].textContent = (p.get("company") or "") + (" · " if p.get("company") else "")
        email = self.dom_nodes["email"]
        email.textContent = p.get("email") or ""
        email.setAttribute("href", "mailto:" + (p.get("email") or ""))
        ui.chip(self.c_consultant, tp('Consultant') if p.get('is_admin') else '', 'ink')
        ui.chip(self.c_demo, tp('Demo') if p.get('is_demo') else '', 'amber')
        ui.chip(self.c_disabled, tp('Disabled') if not p.get('enabled') and not p.get('is_demo') else '', 'red')
        ui.chip(self.c_seen, tp('Active {when}', when=ui.ago(p['last_seen'])) if p.get('last_seen') else tp('Never signed in'), 'outline')
        self.dom_nodes["open"].textContent = str(p["open"])
        self.dom_nodes["delivered"].textContent = str(p["delivered"])
        self.dom_nodes["value"].textContent = ui.money(p["value"])
        client = not p.get('is_admin')
        self.request_button.visible = self.view_button.visible = client
        mine = p.get('is_demo') or p.get('_me')
        self.role_button.visible = self.enable_button.visible = not mine
        self.role_button.text = tp('Remove consultant') if p.get('is_admin') else tp('Make consultant')
        self.enable_button.text = tp('Disable') if p.get('enabled') else tp('Enable')
        self.enable_button.role = ['aa-btn', 'sm', 'ghost' if p.get('enabled') else 'green']
        i18n.apply(self)

    @handle("request_button", "click")
    def request_button_click(self, **event_args):
        self.parent.raise_event("x-new-for", client_id=self.item["id"])

    @handle("view_button", "click")
    def view_button_click(self, **event_args):
        self.parent.raise_event("x-client-requests", client_id=self.item["id"])

    @handle("role_button", "click")
    def role_button_click(self, **event_args):
        p = self.item
        make = not p.get('is_admin')
        if make and not confirm(tp("Give {name} consultant access? They'll see every client and request.", name=p['name']),
                                buttons=[(tp('Cancel'), False), (tp('Make consultant'), True)]):
            return
        if ui.call('admin_set_user', p['id'], {'is_admin': make}) is not ui.FAIL:
            self.parent.raise_event("x-changed")

    @handle("enable_button", "click")
    def enable_button_click(self, **event_args):
        p = self.item
        if ui.call('admin_set_user', p['id'], {'enabled': not p.get('enabled')}) is not ui.FAIL:
            self.parent.raise_event("x-changed")
