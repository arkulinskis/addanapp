from anvil import *

from ._anvil_designer import PrivacyTemplate
from ... import i18n, legal


class Privacy(PrivacyTemplate):
    """#privacy: the documents themselves are in the shared Privacy & Terms page (theme/assets/legal-kit.js, built from
    APP_MAKER/legal-kit). This page links to them and opens the Privacy Policy straight away."""

    def __init__(self, **properties):
        super().__init__(**properties)
        i18n.apply(self)

    @handle("", "show")
    def form_show(self, **event_args):
        legal.open("privacy")
