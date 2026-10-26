from ._anvil_designer import PrivacyTemplate
from anvil import *

from ..content import CONTACT_EMAIL


class Privacy(PrivacyTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.html = f'''
    <div class="app-page"><div class="aa-wrap legal">
      <div class="eyebrow">Legal</div>
      <h1>Privacy policy</h1>
      <p class="muted">Last updated: October 2026</p>
      <p>Addanapp ("we") builds custom software from Montréal, Québec. This policy explains what personal information we
        collect, why, and the choices you have. We follow Québec's <i>Act respecting the protection of personal information in
        the private sector</i> (Law 25) and Canada's PIPEDA.</p>
      <h2>What we collect</h2>
      <ul>
        <li><b>Project briefs</b> sent through our website: name, email, company, budget range and your message.</li>
        <li><b>Workspace accounts</b>: name, company, email, a securely hashed password, and the requests, comments and files
          you submit.</li>
        <li><b>Basic technical data</b> needed to run the service, such as sign-in times.</li>
      </ul>
      <h2>Why we use it</h2>
      <p>Only to answer your enquiry, deliver and support the work you request, send you updates about your requests, and
        invoice accepted work. We do not sell personal information and we do not use your project data to train AI models.</p>
      <h2>AI tools</h2>
      <p>We use AI-assisted development tools to draft code and documentation. We share only what is needed to do the work,
        prefer providers that do not retain or train on submitted data, and a person reviews every output.</p>
      <h2>Retention and security</h2>
      <p>Connections are encrypted, access is limited to the people working on your account, and passwords are never stored in
        plain text. Leads that don't become projects are deleted after 24 months. You can ask us to delete your workspace at any time.</p>
      <h2>Your rights</h2>
      <p>You can request access to, correction of, or deletion of your personal information, and withdraw consent to being
        contacted. Our person in charge of the protection of personal information can be reached at
        <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>
    </div></div>'''
