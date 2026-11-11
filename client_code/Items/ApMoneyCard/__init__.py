from anvil import *
from anvil.js import window

from ._anvil_designer import ApMoneyCardTemplate
from ...Components.ApMoneyBody import ApMoneyBody
from ...Components.ApMoney import ROLE_COLOR


class ApMoneyCard(ApMoneyCardTemplate):
    """One app's plan on the Money view. item = {project, now} (now = show its role tag)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        p = self.item["project"]
        m = p['money']
        self.dom_nodes["card"].style.setProperty("--mc", ROLE_COLOR.get(m.get('role'), 'var(--muted)'))
        a = self.dom_nodes["name"]
        a.textContent = p['name']
        a.setAttribute("href", "#app/" + window.encodeURIComponent(p['key']))
        role = self.dom_nodes["role"]
        if self.item["now"]:
            role.textContent = (m.get('role_icon') or '') + ' ' + (m.get('role_label') or '')
        else:
            role.remove()
        self.dom_nodes["when"].textContent = m.get('when_label') or ''
        self.body.add_component(ApMoneyBody(money=m, head=False))
