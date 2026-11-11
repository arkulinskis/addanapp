from anvil import *
from anvil.js import window

from ._anvil_designer import ApMoneyBodyTemplate
from ... import apps_data


def app_links(keys):
    out = []
    for k in keys or []:
        p = apps_data.project_by_biz(k)
        out.append({"label": p['name'] if p else k, "href": "#app/" + window.encodeURIComponent(p['key']) if p else "#apps/money"})
    return out


class ApMoneyBody(ApMoneyBodyTemplate):
    """An app's monetization plan (APP_MAKER/money): role, timing, why, what's free, the paywall, 2-3 ways to charge,
    and which apps send people to it. money = the plan dict; head=False leaves out the role/timing tags."""

    def __init__(self, money=None, head=True, **properties):
        super().__init__(**properties)
        m = money or {}
        self.head.visible = bool(head)
        self.dom_nodes["role"].textContent = (m.get('role_icon') or '') + ' ' + (m.get('role_label') or '')
        self.dom_nodes["when"].textContent = m.get('when_label') or ''
        self.dom_nodes["why"].textContent = m.get('why') or ''
        self.dom_nodes["free"].textContent = m.get('free') or ''
        self.dom_nodes["paywall"].textContent = m.get('paywall') or ''
        self.strategies.items = [{"text": "%d. %s · %s — %s" % (i + 1, s.get('name', ''), s.get('price', ''), s.get('how', ''))}
                                 for i, s in enumerate(m.get('strategies') or [])]
        js = apps_data.js()
        self.feeds_row.visible = bool(m.get('feeds'))
        self.fed_row.visible = bool(m.get('fed_by'))
        if js:
            js.links(self.dom_nodes["feeds"], app_links(m.get('feeds')))
            js.links(self.dom_nodes["fed"], app_links(m.get('fed_by')))
