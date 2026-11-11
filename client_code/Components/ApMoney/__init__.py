from anvil import *
from anvil.js import window

from ._anvil_designer import ApMoneyTemplate
from ... import apps_data, state

NOW = ('focus', 'test', 'service')  # one group: "making money now"
ROLE_COLOR = {'focus': 'var(--ap-ok)', 'test': 'var(--ap-deploy)', 'service': 'var(--ap-merge)', 'earner': 'var(--accent)',
              'traffic': 'var(--ap-promote)', 'engine': 'var(--muted)'}


class ApMoney(ApMoneyTemplate):
    """#apps/money: every app's monetization plan, grouped by role (making money now, earners, traffic drivers...),
    with a role filter and the "who sends people to whom" list."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.role = state.store_get('apps.moneyRole', 'all')
        self.chips.add_event_handler("x-pick", self._pick)
        self.redraw()

    def redraw(self, key=None):
        b = apps_data.board() or {}
        roles = (b.get('money_meta') or {}).get('roles') or {}
        everyone = [p for p in (b.get('projects') or []) if p.get('money')]
        vis = [p for p in apps_data.visible() if p.get('money')]
        self.none.visible = not everyone
        self.chips.items = [{"key": "all", "label": "All", "count": len(everyone), "on": self.role == 'all'}] + [
            {"key": r, "label": (roles[r].get('icon') or '') + ' ' + roles[r].get('label', r), "count": len([p for p in everyone if p['money'].get('role') == r]),
             "on": self.role == r} for r in roles]
        shown = [p for p in vis if self.role == 'all' or p['money'].get('role') == self.role]
        fed = sorted([p for p in everyone if p['money'].get('fed_by')], key=lambda p: -len(p['money']['fed_by']))
        self.flow_list.items = [{"text": "%s %s ← %s" % (p['name'], p['money'].get('role_icon', ''),
                                                       ', '.join((apps_data.project_by_biz(k) or {}).get('name', k) for k in p['money']['fed_by'])),
                                 "href": "#app/" + window.encodeURIComponent(p['key'])} for p in fed]
        if state.store_get('apps.moneyFlow', True):
            self.dom_nodes["flow"].setAttribute("open", "")
        rows = [list(NOW)] + [[r] for r in roles if r not in NOW]
        groups = []
        for rs in rows:
            g = sorted([p for p in shown if p['money'].get('role') in rs], key=lambda p: (rs.index(p['money']['role']), p['name'].lower()))
            if not g:
                continue
            if len(rs) > 1:
                head, sub = "💵 Making money now", "%d · the focus app, the tests and client work" % len(g)
            else:
                R = roles.get(rs[0]) or {}
                head, sub = (R.get('icon') or '') + ' ' + R.get('label', rs[0]), "%d · %s" % (len(g), R.get('meaning', ''))
            groups.append({"head": head, "sub": sub, "color": ROLE_COLOR.get(rs[0], 'var(--muted)'), "projects": g, "now": len(rs) > 1})
        self.groups.items = groups

    def _pick(self, key, **event_args):
        self.role = key
        state.store_set('apps.moneyRole', key)
        self.redraw()
