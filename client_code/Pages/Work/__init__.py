from anvil import *
from anvil.js import window

from ._anvil_designer import WorkTemplate
from ... import i18n, portfolio, state, ui
from ...i18n import tp, tn


class Work(WorkTemplate):
    """#work: every project, grouped by category, with a category filter. Each row opens in place to show the preview,
    what we built, the film and the live link."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.key = 'all'
        self.filters.add_event_handler("x-pick", self._pick)
        groups = []
        for key, label in portfolio.CATEGORIES[1:]:
            group = portfolio.in_category(key)
            if group:
                groups.append({"key": key, "label": label, "keys": [p['key'] for p in group], "first": not groups})
        self.groups.items = groups
        self._draw_filters()
        self.dom_nodes["count"].textContent = (tn(len(portfolio.PROJECTS), '{n} product', '{n} products') + ' · '
                                               + tp('{n} live', n=portfolio.live_count()))
        i18n.apply(self)

    def _draw_filters(self):
        self.filters.items = [{"key": key, "label": label, "on": key == self.key,
                               "count": len(portfolio.PROJECTS) if key == 'all' else len(portfolio.in_category(key))}
                              for key, label in portfolio.CATEGORIES]

    def _pick(self, key, **event_args):
        self.key = key
        self._draw_filters()
        window.aa.filterWork(self.dom_nodes["index"], key)

    @handle("", "show")
    def form_show(self, **event_args):
        ui.reveal(self)
