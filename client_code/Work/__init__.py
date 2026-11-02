from ._anvil_designer import WorkTemplate
from anvil import *

from .. import ui, state, portfolio
from ..i18n import t


class Work(WorkTemplate):
  """Full portfolio: every project, grouped by category; each row opens to show what we built, its film and its link."""

  def __init__(self, **properties):
    self.init_components(**properties)
    self.html = f'''
    <div class="lp">
      <section class="lp-hero" style="padding-bottom:72px" aria-labelledby="work-h">
        <div class="aa-wrap" style="position:relative;z-index:1">
          <div class="eyebrow rv">{t('Selected work')}</div>
          <h1 id="work-h" class="rv d1" style="max-width:900px">{t("Products we've built, <em>shipped and still run.</em>")}</h1>
          <p class="sub rv d2">{t('Working businesses, useful tools, learning apps, games, VR and mobile-first apps. Each one started as a request, went through the same scope, build, validate and accept loop, and is live today.')}</p>
          <p class="sub rv d3" style="margin-top:10px">{t('Open any project to see what we built, try it live or watch its one-minute film.')}</p>
        </div>
      </section>
      <section class="lp-sec" style="padding-top:56px">
        <div class="aa-wrap">
          {portfolio.index()}
        </div>
      </section>
      <section class="lp-sec tight lp-alt">
        <div class="aa-wrap lp-final">
          <div class="eyebrow" style="justify-content:center">{t('Your turn')}</div>
          <h2>{t("Have something that should exist? <em>Let's scope it.</em>")}</h2>
          <p>{t('Send a brief and get a fixed quote from an engineer within two business days.')}</p>
          <div class="ctas">
            <button type="button" class="aa-btn accent lg" data-act="contact">{t('Start a project')} <span class="arr">&rarr;</span></button>
            <button type="button" class="aa-btn ghost lg" data-act="signup">{t('Create a client workspace')}</button>
          </div>
        </div>
      </section>
    </div>'''
    node = ui.dom(self)
    ui.bind(self, {
      'filter': lambda key: portfolio.apply_filter(node, key),
      'contact': lambda a: state.go('home/contact'),
      'signup': lambda a: state.go(state.home_route() if state.logged_in() else 'signup'),
    })
    self.add_event_handler('show', self.form_show)
    ui.reveal(self)

  def form_show(self, **event_args):
    ui.reveal(self)
