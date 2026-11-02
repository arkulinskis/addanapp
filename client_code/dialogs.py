"""Modal dialogs: sign in / create workspace, text prompts."""
import anvil
import anvil.users
import anvil.server

from . import ui, legal
from .i18n import t
from .ui import esc
from .icons import LOGO

GOOGLE_G = '<svg viewBox="0 0 48 48" width="18" height="18" aria-hidden="true" style="flex:none"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>'


def _google_step_done():
  """After login_with_google() gave None: did the person finish the Google window (they just have no account yet)?"""
  try:
    import anvil.google.auth
    return bool(anvil.google.auth.get_user_email())
  except Exception:
    return True  # can't tell: go on to sign-up, which asks Google again if needed


# ================================================================== auth

def auth(mode='login'):
  box = _AuthBox(mode)
  return ui.modal(box.component)


class _AuthBox(object):
  def __init__(self, mode):
    self.mode = mode
    self.component = ui.H(f'''
      <div class="auth">
        <div class="head">{LOGO}
          <h2 class="t-title"></h2>
          <p class="t-sub"></p>
        </div>
        <div class="aa-error hidden"></div>
        <div class="f-signup">
          <div class="f"><label>{t('Your name')}</label><input type="text" name="name" autocomplete="name" placeholder="{t('Jane Tremblay')}"></div>
          <div class="f"><label>{t('Company')} <span class="opt">{t('(optional)')}</span></label><input type="text" name="company" autocomplete="organization" placeholder="{t('Acme Inc.')}"></div>
        </div>
        <div class="f"><label>{t('Work email')}</label><input type="email" name="email" autocomplete="email" placeholder="{t('you@company.com')}"></div>
        <div class="f"><label>{t('Password')}</label><input type="password" name="pw" autocomplete="current-password" placeholder="{t('8+ characters')}"></div>
        <div class="f-legal">{legal.consent_field()}</div>
        <button type="button" class="aa-btn block lg t-go" data-act="go"></button>
        <div style="text-align:center;opacity:.6;margin:10px 0;font-size:14px">{t('or')}</div>
        <button type="button" class="aa-btn block lg ghost" data-act="google">{GOOGLE_G}{t('Continue with Google')}</button>
        <div class="switch"><span class="t-switch-text"></span> <button type="button" class="aa-link" data-act="switch"></button>
          <div class="f-forgot" style="margin-top:8px"><button type="button" class="aa-link" data-act="forgot">{t('Forgot your password?')}</button></div>
        </div>
        <p class="fine">{t('Your workspace is private to you and your Addanapp engineer.')}<br>{t('See our <a href="javascript:void(0)" data-lk-open="overview">Privacy &amp; Terms</a>.')}</p>
      </div>''', actions={
        'go': lambda a: self.submit(),
        'google': lambda a: self.google(),
        'switch': lambda a: self.set_mode('login' if self.mode == 'signup' else 'signup'),
        'forgot': lambda a: self.forgot(),
        'privacy': lambda a: ui.close_modal(self.component, None),
      })
    node = ui.dom(self.component)

    def on_key(e):
      if e.key == 'Enter' and e.target.tagName == 'INPUT':
        self.submit()
    node.addEventListener('keydown', on_key)
    self.set_mode(mode)

  def _q(self, sel):
    return ui.q(self.component, sel)

  def set_mode(self, mode):
    self.mode = mode
    signup = mode == 'signup'
    self._q('.t-title').textContent = t('Create your workspace') if signup else t('Welcome back')
    self._q('.t-sub').textContent = (t('Submit requests, approve fixed quotes and follow every step of the build.')
                                     if signup else t('Sign in to your Addanapp workspace.'))
    self._q('.t-go').textContent = t('Create workspace') if signup else t('Sign in')
    self._q('.t-switch-text').textContent = t('Already a client?') if signup else t('New to Addanapp?')
    self._q('[data-act=switch]').textContent = t('Sign in') if signup else t('Create a workspace')
    self._q('[name=pw]').setAttribute('autocomplete', 'new-password' if signup else 'current-password')
    ui.show(self._q('.f-signup'), signup)
    ui.show(self._q('.f-legal'), signup)
    ui.show(self._q('.f-forgot'), not signup)
    self.error(None)

  def error(self, msg):
    el = self._q('.aa-error')
    if msg:
      el.textContent = msg
    ui.show(el, bool(msg))

  def submit(self):
    v = ui.vals(self.component)
    email, pw = v.get('email', ''), v.get('pw', '')
    if '@' not in email or '.' not in email:
      return self.error(t("Please enter a valid email address."))
    if len(pw) < 8:
      return self.error(t("Passwords need at least 8 characters."))
    btn = self._q('.t-go')
    ui.busy(btn, True)
    try:
      if self.mode == 'signup':
        name = v.get('name', '')
        if len(name) < 2:
          ui.busy(btn, False)
          return self.error(t("Please tell us your name."))
        if not legal.consent_ok(ui.dom(self.component)):
          ui.busy(btn, False)
          return
        anvil.users.signup_with_email(email, pw, remember=True)
        anvil.server.call('update_me', {'name': name, 'company': v.get('company', '')})
      else:
        anvil.users.login_with_email(email, pw, remember=True)
    except anvil.users.UserExists:
      ui.busy(btn, False)
      self.set_mode('login')
      return self.error(t("You already have a workspace with this email. Sign in instead."))
    except anvil.users.AuthenticationFailed:
      ui.busy(btn, False)
      return self.error(t("That email and password don't match."))
    except Exception as e:
      ui.busy(btn, False)
      return self.error(str(e).replace('anvil.users.', ''))
    ui.close_modal(self.component, True)

  def google(self):
    """Continue with Google: sign in, or create the workspace on the first visit (sign-up asks for the tick here too)."""
    if self.mode == 'signup' and not legal.consent_ok(ui.dom(self.component)):
      return
    btn = self._q('[data-act=google]')
    ui.busy(btn, True)
    try:
      if anvil.users.login_with_google(remember=True) is None:
        if not _google_step_done() or anvil.users.signup_with_google(remember=True) is None:
          ui.busy(btn, False)
          return self.error(t("Google sign-in was cancelled."))
        v = ui.vals(self.component) if self.mode == 'signup' else {}
        changes = {k: v[k] for k in ('name', 'company') if len(v.get(k) or '') >= 2}
        if changes:
          anvil.server.call('update_me', changes)
    except Exception as e:
      ui.busy(btn, False)
      return self.error(str(e).replace('anvil.users.', ''))
    ui.close_modal(self.component, True)

  def forgot(self):
    email = ui.vals(self.component).get('email', '')
    if '@' not in email:
      return self.error(t("Type your email above, then click 'Forgot your password?'."))
    try:
      anvil.users.send_password_reset_email(email)
      ui.toast(t("If that email has a workspace, a reset link is on its way."))
    except Exception as e:
      self.error(str(e))


# ================================================================== prompts

def prompt_text(title, text='', placeholder='', ok=None, required=True, kind='accent'):
  """Ask for a block of text. Returns the text, or None if cancelled."""
  box = ui.H(f'''
    <div>
      <h3 style="font-size:1.25rem;margin-bottom:6px">{esc(title)}</h3>
      <p class="muted small">{esc(text)}</p>
      <div class="aa-error hidden"></div>
      <div class="f"><textarea name="body" rows="5" placeholder="{esc(placeholder)}"></textarea></div>
      <div style="display:flex;gap:8px;justify-content:flex-end">
        <button type="button" class="aa-btn ghost" data-act="cancel">{t('Cancel')}</button>
        <button type="button" class="aa-btn {kind}" data-act="ok">{esc(ok or t('Send'))}</button>
      </div>
    </div>''')

  def done(_):
    body = ui.vals(box).get('body', '')
    if required and len(body) < 3:
      err = ui.q(box, '.aa-error')
      err.textContent = t('Please add a few words.')
      ui.show(err)
      return
    ui.close_modal(box, body)

  ui.bind(box, {'ok': done, 'cancel': lambda a: ui.close_modal(box, None)})
  return ui.modal(box)
