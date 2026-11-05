import re

from anvil import *
import anvil.server
import anvil.users

from ._anvil_designer import AuthBoxTemplate
from ... import i18n, legal, state, ui
from ...i18n import tp

EMAIL = re.compile(r"^\S+@\S+\.\S+$")


def _google_step_done():
    """After login_with_google() gave None: did the person finish the Google window (they just have no account yet)?"""
    try:
        import anvil.google.auth
        return bool(anvil.google.auth.get_user_email())
    except Exception:
        return True  # can't tell: go on to sign-up, which asks Google again if needed


class AuthBox(AuthBoxTemplate):
    """Sign in (#login) or create a workspace (#signup), shown over the landing page. alert() returns True once
    someone is signed in. Sign-up needs the Privacy & Terms tick box (the legal kit draws it); Continue with Google
    signs in, or makes the workspace on the first visit."""

    def __init__(self, mode='login', **properties):
        super().__init__(**properties)
        self.dom_nodes["consent"].innerHTML = legal.consent_field()
        state.set_control_attr(self.name_box, "autocomplete", "name")
        state.set_control_attr(self.company_box, "autocomplete", "organization")
        state.set_control_attr(self.email_box, "autocomplete", "email")
        img = state.control(self.google_button).querySelector("img")
        if img:
            img.setAttribute("alt", "")
        i18n.apply(self)
        state.heading(self.heading, 2)
        self._set_mode(mode)

    def _set_mode(self, mode):
        self.mode = mode
        signup = mode == 'signup'
        self.heading.text = tp('Create your workspace') if signup else tp('Welcome back')
        self.sub.text = (tp('Submit requests, approve fixed quotes and follow every step of the build.')
                         if signup else tp('Sign in to your Addanapp workspace.'))
        self.go_button.text = tp('Create workspace') if signup else tp('Sign in')
        self.switch_text.text = tp('Already a client?') if signup else tp('New to Addanapp?')
        self.switch_button.text = tp('Sign in') if signup else tp('Create a workspace')
        state.set_control_attr(self.password_box, "autocomplete", "new-password" if signup else "current-password")
        self.signup_fields.visible = signup
        self.legal_box.visible = signup
        self.forgot_box.visible = not signup
        self._error(None)

    def _error(self, msg):
        self.error.text = msg or ''
        self.error.visible = bool(msg)

    @handle("switch_button", "click")
    def switch_button_click(self, **event_args):
        self._set_mode('login' if self.mode == 'signup' else 'signup')

    @handle("email_box", "pressed_enter")
    def email_box_pressed_enter(self, **event_args):
        self.go_button_click()

    @handle("password_box", "pressed_enter")
    def password_box_pressed_enter(self, **event_args):
        self.go_button_click()

    @handle("go_button", "click")
    def go_button_click(self, **event_args):
        email, pw = (self.email_box.text or '').strip(), self.password_box.text or ''
        if not EMAIL.match(email):
            return self._error(tp("Please enter a valid email address."))
        if len(pw) < 8:
            return self._error(tp("Passwords need at least 8 characters."))
        signup = self.mode == 'signup'
        name = (self.name_box.text or '').strip()
        if signup and len(name) < 2:
            return self._error(tp("Please tell us your name."))
        if signup and not legal.consent_ok(self.dom_nodes["consent"]):
            return
        self.go_button.enabled = False
        try:
            if signup:
                anvil.users.signup_with_email(email, pw, remember=True)
                anvil.server.call('update_me', {'name': name, 'company': (self.company_box.text or '').strip()})
            else:
                anvil.users.login_with_email(email, pw, remember=True)
        except anvil.users.UserExists:
            self.go_button.enabled = True
            self._set_mode('login')
            return self._error(tp("You already have a workspace with this email. Sign in instead."))
        except anvil.users.AuthenticationFailed:
            self.go_button.enabled = True
            return self._error(tp("That email and password don't match."))
        except Exception as e:
            self.go_button.enabled = True
            return self._error(str(e).replace('anvil.users.', ''))
        self.raise_event("x-close-alert", value=True)

    @handle("google_button", "click")
    def google_button_click(self, **event_args):
        if self.mode == 'signup' and not legal.consent_ok(self.dom_nodes["consent"]):
            return
        self.google_button.enabled = False
        try:
            if anvil.users.login_with_google(remember=True) is None:
                if not _google_step_done() or anvil.users.signup_with_google(remember=True) is None:
                    self.google_button.enabled = True
                    return self._error(tp("Google sign-in was cancelled."))
                if self.mode == 'signup':
                    changes = {k: v for k, v in (('name', (self.name_box.text or '').strip()),
                                                 ('company', (self.company_box.text or '').strip())) if len(v) >= 2}
                    if changes:
                        anvil.server.call('update_me', changes)
        except Exception as e:
            self.google_button.enabled = True
            return self._error(str(e).replace('anvil.users.', ''))
        self.raise_event("x-close-alert", value=True)

    @handle("forgot_button", "click")
    def forgot_button_click(self, **event_args):
        email = (self.email_box.text or '').strip()
        if '@' not in email:
            return self._error(tp("Type your email above, then click 'Forgot your password?'."))
        try:
            anvil.users.send_password_reset_email(email)
        except anvil.users.AuthenticationFailed:
            pass  # same answer either way, so nobody can find out which emails have accounts
        except Exception as e:
            return self._error(str(e))
        state.toast(tp("If that email has a workspace, a reset link is on its way."), "ok")

    @handle("", "show")
    def form_show(self, **event_args):
        (self.name_box if self.mode == 'signup' else self.email_box).focus()
