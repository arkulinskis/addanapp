from ._anvil_designer import AccountTemplate
from anvil import *
import anvil.users

from .. import ui, state, i18n
from ..i18n import t
from ..ui import esc


class Account(AccountTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    me = state.refresh_me() or {}
    self.html = f'''
    <div class="app-page"><div class="aa-wrap" style="max-width:720px">
      <div class="page-head"><div><div class="eyebrow">{t('Account')}</div><h1>{t('Your details')}</h1>
        <p>{t('Used on requests, notes and invoices.')}</p></div></div>
      <div class="card card-pad js-form">
        <div class="aa-error hidden"></div>
        <div class="row2" style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
          <div class="f"><label for="ac-name">{t('Name')}</label><input id="ac-name" type="text" name="name" value="{esc(me.get('name'))}"></div>
          <div class="f"><label for="ac-company">{t('Company')}</label><input id="ac-company" type="text" name="company" value="{esc(me.get('company'))}"></div>
        </div>
        <div class="row2" style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
          <div class="f"><label>{t('Email')}</label><input type="email" value="{esc(me.get('email'))}" disabled>
            <div class="hint">{t('Contact us to change your sign-in email.')}</div></div>
          <div class="f"><label for="ac-phone">{t('Phone')} <span class="opt">{t('(optional)')}</span></label><input id="ac-phone" type="text" name="phone" value="{esc(me.get('phone'))}"></div>
        </div>
        <label class="check" style="margin:6px 0 22px"><input type="checkbox" name="email_notifications" {"checked" if me.get('email_notifications') else ""}>
          <span>{t('Email me when a request changes status or gets a new note.')}</span></label>
        <div style="display:flex;gap:10px;justify-content:space-between;flex-wrap:wrap">
          <button type="button" class="aa-btn ghost" data-act="pw">{t('Send password reset email')}</button>
          <button type="button" class="aa-btn" data-act="save">{t('Save changes')}</button>
        </div>
      </div>
      <div class="card card-pad" style="margin-top:18px">
        <div class="f" style="margin:0"><label for="ac-lang">{t('Language')}</label>
          <select id="ac-lang" class="js-lang-select">{ui.options(i18n.LANGS, i18n.lang)}</select>
          <div class="hint">{t('Used for this website, your workspace and the emails we send you. The page reloads to switch.')}</div></div>
      </div>
    </div></div>'''
    ui.bind(self, {'save': lambda a: self.save(), 'pw': lambda a: self.reset_pw()})
    sel = ui.q(self, '.js-lang-select')

    def on_lang(e):
      i18n.set_lang(sel.value)
    sel.addEventListener('change', on_lang)

  def save(self):
    form = ui.q(self, '.js-form')
    v = ui.vals(form)
    res = ui.call('update_me', {'name': v.get('name'), 'company': v.get('company'), 'phone': v.get('phone'),
                                'email_notifications': v.get('email_notifications')})
    if res is not ui.FAIL:
      state.me = res
      if state.main:
        state.main.update_header()
      ui.toast(t("Saved."))

  def reset_pw(self):
    try:
      anvil.users.send_password_reset_email((state.me or {}).get('email'))
      ui.toast(t("Check your inbox for a password reset link."))
    except Exception as e:
      ui.toast(str(e), 'danger')
