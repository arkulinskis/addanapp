from ._anvil_designer import PrivacyTemplate
from anvil import *

from .. import legal
from ..i18n import t


class Privacy(PrivacyTemplate):
  """#privacy: the documents themselves are in the shared Privacy & Terms page (theme/assets/legal-kit.js,
  built from APP_MAKER/legal-kit). This page links to them and opens the Privacy Policy straight away."""

  def __init__(self, **properties):
    self.init_components(**properties)
    self.html = f'''
    <div class="app-page"><div class="aa-wrap legal">
      <div class="eyebrow">{t('Legal')}</div>
      <h1>{t('Privacy &amp; Terms')}</h1>
      <p>{t("Addanapp is operated by Arkvital, Montréal, Québec. We follow Québec's Law 25, Canada's PIPEDA and the GDPR. These documents explain, in plain language, what we collect, why, who helps us, your rights, and the rules for using our website and client workspace.")}</p>
      <ul>
        <li><a href="javascript:void(0)" data-lk-open="overview">{t('Overview')}</a></li>
        <li><a href="javascript:void(0)" data-lk-open="privacy">{t('Privacy Policy')}</a></li>
        <li><a href="javascript:void(0)" data-lk-open="terms">{t('Terms of Use')}</a></li>
        <li><a href="javascript:void(0)" data-lk-open="cookies">{t('Cookies &amp; Storage')}</a></li>
      </ul>
    </div></div>'''
    self.add_event_handler("show", lambda **e: legal.open("privacy"))
