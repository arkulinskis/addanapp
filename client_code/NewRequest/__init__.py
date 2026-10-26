from ._anvil_designer import NewRequestTemplate
from anvil import *

from .. import ui, state
from ..i18n import t


def request_form_html(budgets=True):
  return f'''
    <div class="aa-error hidden"></div>
    <div class="f"><label for="nr-title">{t('Title')}</label>
      <input id="nr-title" type="text" name="title" maxlength="140" placeholder="{t('e.g. Let customers pay a deposit when booking')}">
      <div class="hint">{t('One line that describes the outcome.')}</div></div>
    <div class="f"><span class="lbl">{t('Type of request')}</span>{ui.seg('kind', ui.KINDS, 'feature')}</div>
    <div class="f"><label for="nr-desc">{t('What do you need, and why?')}</label>
      <textarea id="nr-desc" name="description" rows="6" placeholder="{t("Describe the problem, who it's for and what should happen. Links and examples help.")}"></textarea></div>
    <div class="f"><label for="nr-acc">{t("How will we know it's done?")} <span class="opt">{t('(optional)')}</span></label>
      <textarea id="nr-acc" name="acceptance" rows="4" placeholder="{t('- Customers can pay a 20% deposit&#10;- Refunds happen automatically 48h before&#10;- Managers see deposits in the day view')}"></textarea>
      <div class="hint">{t('Your acceptance criteria. If you skip this, your engineer will propose them with the quote.')}</div></div>
    <div class="f"><span class="lbl">{t('Priority')}</span>{ui.seg('priority', ui.PRIORITIES, 'normal')}</div>
    <div class="row2" style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
      <div class="f"><label for="nr-proj">{t('App or project')} <span class="opt">{t('(optional)')}</span></label>
        <input id="nr-proj" type="text" name="project" placeholder="{t('e.g. Booking website')}"></div>
      <div class="f"><label for="nr-date">{t('Ideal delivery date')} <span class="opt">{t('(optional)')}</span></label>
        <input id="nr-date" type="date" name="desired_date"></div>
    </div>
    {'<div class="f"><label for="nr-budget">' + t('Budget range') + ' <span class="opt">' + t('(optional)') + '</span></label><select id="nr-budget" name="budget">' + ui.options(ui.BUDGETS) + '</select></div>' if budgets else ''}'''


def collect(component):
  v = ui.vals(component)
  return {
    'title': v.get('title', ''), 'kind': v.get('kind') or 'feature', 'description': v.get('description', ''),
    'acceptance': v.get('acceptance', ''), 'priority': v.get('priority') or 'normal', 'project': v.get('project', ''),
    'desired_date': ui.parse_date(v.get('desired_date')),
    'budget': '' if v.get('budget') in (None, 'Not sure yet') else v.get('budget'),
  }


def validate(data):
  if len(data['title']) < 4:
    return t("Give your request a short title (4+ characters).")
  if len(data['description']) < 10:
    return t("Describe what you need in a sentence or two.")
  return None


class NewRequest(NewRequestTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.html = f'''
    <div class="app-page"><div class="aa-wrap">
      <div class="crumbs"><a href="#portal">{t('Dashboard')}</a><span>/</span><span>{t('New request')}</span></div>
      <div class="page-head"><div><h1>{t('New request')}</h1><p>{t("Describe the outcome. We'll reply with scope, a fixed price and an ETA.")}</p></div></div>
      <div class="nr">
        <div class="card card-pad js-form">
          {request_form_html()}
          <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:8px;flex-wrap:wrap">
            <a class="aa-btn ghost" href="#portal">{t('Cancel')}</a>
            <button type="button" class="aa-btn accent" data-act="submit">{t('Submit request')} <span class="arr">&rarr;</span></button>
          </div>
        </div>
        <aside class="aside card card-pad">
          <h3 style="margin-bottom:16px">{t('What happens next')}</h3>
          <ol>
            <li><div><b>{t('Scoping')}</b>{t('An engineer reads your request and may ask a question or two in the thread.')}</div></li>
            <li><div><b>{t('Fixed quote')}</b>{t('You get the price, acceptance criteria and an ETA. Usually within 2 business days.')}</div></li>
            <li><div><b>{t('Build &amp; validate')}</b>{t('AI-accelerated build, then human review and testing. Follow it live.')}</div></li>
            <li><div><b>{t('Accept, then pay')}</b>{t("Test it on staging. You're invoiced only once you accept.")}</div></li>
          </ol>
        </aside>
      </div>
    </div></div>'''
    ui.wire_segs(self)
    ui.bind(self, {'submit': lambda a: self.submit()})

  def submit(self):
    form = ui.q(self, '.js-form')
    data = collect(form)
    err = form.querySelector('.aa-error')
    msg = validate(data)
    if msg:
      err.textContent = msg
      ui.show(err)
      return
    ui.show(err, False)
    btn = form.querySelector('[data-act=submit]')
    ui.busy(btn, True, t('Submitting…'))
    res = ui.call('create_request', data)
    ui.busy(btn, False)
    if res is ui.FAIL:
      return
    ui.toast(t("Request submitted. An engineer will scope it shortly."))
    state.go('r/' + res)
