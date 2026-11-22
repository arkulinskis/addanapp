from anvil import *
from anvil.js import window

from ._anvil_designer import WorkTemplate
from ... import i18n, portfolio, state, ui
from ...i18n import tp, tn
from ...Components.Shot import BY_KEY


SPOTS = 3  # spotlight cards shown side by side


class Work(WorkTemplate):
    """#work: a spotlight of three live projects side by side (a shuffled deck of every live project: Next steps
    through it three at a time, Refresh reshuffles), then every project grouped by category, with a category filter.
    Each index row opens in place to show the preview, what we built, the film and the live link; a spotlight card's
    Details opens its row."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.key = 'all'
        self.filters.add_event_handler("x-pick", self._pick)
        self.spots.add_event_handler("x-open", self._open_row)
        self.deck, self.at = [], 0
        self._shuffle()
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

    # ---------------------------------------------------------------- spotlight
    def _shuffle(self, shown=()):
        """A new random order of every live project; the ones on screen go last, so Refresh always shows new faces."""
        order = [p['key'] for p in portfolio.picks(portfolio.live_count())]
        self.deck = [k for k in order if k not in shown] + [k for k in order if k in shown]
        self.at = 0
        self._draw_spots()

    def _draw_spots(self):
        n = len(self.deck)
        keys = [self.deck[(self.at + j) % n] for j in range(min(SPOTS, n))]
        self.spots.items = [{"key": k, "i": (self.at + j) % n, "n": j} for j, k in enumerate(keys)]
        self.dom_nodes["grid"].scrollLeft = 0  # the swipeable row on phones starts at the first card again
        sets = (n + SPOTS - 1) // SPOTS
        self.dom_nodes["pos"].textContent = tp('Set {a} of {n}', a=self.at // SPOTS + 1, n=sets)

    @handle("refresh_button", "click")
    def refresh_button_click(self, **event_args):
        self._shuffle(shown=[it["key"] for it in self.spots.items])

    @handle("next_button", "click")
    def next_button_click(self, **event_args):
        if self.at + SPOTS >= len(self.deck):
            self._shuffle(shown=[it["key"] for it in self.spots.items])  # seen them all: start a fresh round
        else:
            self.at += SPOTS
            self._draw_spots()

    def _open_row(self, key, **event_args):
        p = BY_KEY.get(key)
        if self.key != 'all' and (p is None or p['cat'] != self.key):
            self._pick('all')
        window.aa.openWork(self.dom_nodes["index"], key)

    # ---------------------------------------------------------------- index
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
