from ._anvil_designer import LandingTemplate
from anvil import *

from .. import ui, state, portfolio
from ..i18n import t
from ..content import HTML


class Landing(LandingTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.html = HTML
    self.node = ui.dom(self)
    ui.bind(self, {
      'signup': lambda a: self._workspace('signup'),
      'login': lambda a: self._workspace('login'),
      'contact': lambda a: state.go('home/contact'),
      'filter': lambda key: portfolio.apply_filter(self.node, key),
      'wstab': self._ws_tab,
      'lead': lambda a: self._send_lead(),
    })
    self.add_event_handler('show', self.form_show)
    ui.reveal(self)

  def form_show(self, **event_args):
    ui.reveal(self)

  def _workspace(self, mode):
    if state.logged_in():
      state.go(state.home_route())
    else:
      state.go(mode)

  def _ws_tab(self, which):
    for b in ui.qa(self.node, '.lp-ws .tabs button'):
      b.classList.toggle('on', b.getAttribute('data-arg') == which)
    for p in ui.qa(self.node, '.lp-ws .panel'):
      p.classList.toggle('on', p.getAttribute('data-panel') == which)

  def _send_lead(self):
    form = self.node.querySelector('#lead-form')
    v = ui.vals(form)
    err = form.querySelector('.aa-error')

    def fail(msg):
      err.textContent = msg
      ui.show(err)

    if len(v.get('name', '')) < 2:
      return fail(t("Please tell us your name."))
    if '@' not in v.get('email', '') or '.' not in v.get('email', ''):
      return fail(t("Please enter a valid email address."))
    if len(v.get('message', '')) < 10:
      return fail(t("A sentence or two about the outcome you're after helps us reply with something useful."))
    if not v.get('consent'):
      return fail(t("Please confirm we may contact you about this request."))
    ui.show(err, False)
    btn = form.querySelector('[data-act=lead]')
    ui.busy(btn, True, t('Sending…'))
    res = ui.call('submit_lead', v)
    ui.busy(btn, False)
    if res is ui.FAIL:
      return
    ui.show(form.querySelector('.form-body'), False)
    ui.show(form.querySelector('.ok'), True)
