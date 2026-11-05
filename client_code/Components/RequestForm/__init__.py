from anvil import *

from ._anvil_designer import RequestFormTemplate
from ... import i18n, state, ui
from ...i18n import tp

ACCEPTANCE_HINT = '- Customers can pay a 20% deposit&#10;- Refunds happen automatically 48h before&#10;- Managers see deposits in the day view'


class RequestForm(RequestFormTemplate):
    """The fields of a new request (#new, and the console's "New request for a client" dialog)."""

    def __init__(self, **properties):
        self._budgets = True
        super().__init__(**properties)
        self.kind_seg.choices = ui.KINDS
        self.kind_seg.selected_value = 'feature'
        self.kind_seg.label = tp('Type of request')
        self.prio_seg.choices = ui.PRIORITIES
        self.prio_seg.selected_value = 'normal'
        self.prio_seg.label = tp('Priority')
        self.budget_dd.items = ui.dd_items(ui.BUDGETS)
        state.date_box(self.date_box)
        state.set_control_attr(self.title_box, "maxlength", 140)
        i18n.apply(self)
        # the example criteria: three lines (the translation keeps &#10; for the line breaks)
        self.acc_box.placeholder = i18n.t(ACCEPTANCE_HINT).replace('&#10;', '\n')
        self.budget_field.visible = self._budgets

    @property
    def budgets(self):
        return self._budgets

    @budgets.setter
    def budgets(self, v):
        self._budgets = bool(v)
        try:
            self.budget_field.visible = self._budgets
        except AttributeError:
            pass  # set before the template exists: __init__ applies it

    def collect(self):
        budget = self.budget_dd.selected_value if self._budgets else ''
        return {
            'title': (self.title_box.text or '').strip(), 'kind': self.kind_seg.selected_value or 'feature',
            'description': (self.desc_box.text or '').strip(), 'acceptance': (self.acc_box.text or '').strip(),
            'priority': self.prio_seg.selected_value or 'normal', 'project': (self.project_box.text or '').strip(),
            'desired_date': ui.parse_date(self.date_box.text),
            'budget': '' if budget in (None, 'Not sure yet') else budget,
        }

    @staticmethod
    def validate(data):
        if len(data['title']) < 4:
            return tp("Give your request a short title (4+ characters).")
        if len(data['description']) < 10:
            return tp("Describe what you need in a sentence or two.")
        return None

    def show_error(self, msg):
        self.error.text = msg or ''
        self.error.visible = bool(msg)
        if msg:
            ui.scroll_into_view(self.error)
