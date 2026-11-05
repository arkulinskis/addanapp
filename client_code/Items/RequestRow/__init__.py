from anvil import *

from ._anvil_designer import RequestRowTemplate
from ... import ui
from ...i18n import tp


class RequestRow(RequestRowTemplate):
    """A request in a list (the client's dashboard, or the console with the client column when item['_admin'])."""

    def __init__(self, **properties):
        super().__init__(**properties)
        r = self.item
        admin = bool(r.get('_admin'))
        row = self.dom_nodes["row"]
        row.setAttribute("href", "#r/" + r["id"])
        if admin:
            row.classList.add("admin")
        if r.get('unread'):
            row.classList.add("unread")
        bits = [ui.KIND.get(r['kind'], r.get('kind_label'))]
        if r['status'] == 'quoted' and r.get('quote_amount') is not None:
            bits.append(tp('Fixed quote {amount}', amount=ui.money(r['quote_amount'])))
        if r.get('eta') and r['status'] in ('quoted', 'in_progress', 'review'):
            bits.append(tp('ETA {date}', date=ui.fmt_date(r['eta'])))
        c = r.get('client') or {}
        if admin:
            bits.insert(0, c.get('company') or c.get('name') or '')
        self.dom_nodes["ref"].textContent = r["ref"]
        self.dom_nodes["title"].textContent = r["title"]
        self.dom_nodes["sub"].textContent = ' · '.join([b for b in bits if b])
        self.cl.visible = admin
        if admin:
            self.cl_avatar.person = c
            self.dom_nodes["cl_name"].textContent = c.get("name", "")
        ui.status_chip(self.status, r['status'])
        live = r['status'] != 'declined'
        self.progress.visible = live
        self.progress.value = r['progress']
        self.progress.done = r['status'] == 'delivered'
        self.dom_nodes["pct"].textContent = ("%d%%" % r['progress']) if live else ''
        self.dom_nodes["upd"].textContent = ui.ago(r.get('last_activity'))
