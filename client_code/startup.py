"""The app starts here (anvil.yaml: startup module). The language pack first (i18n waits for the head script's
download), then the Privacy & Terms kit, who is signed in (one server call, Anvil's spinner shows meanwhile), and
the page for the address in the browser bar."""
from . import i18n
from . import legal, router, state
from . import session_guard

session_guard.start()  # an expired server session reloads quietly instead of "Session expired, refresh now"

legal.setup(lang=i18n.lang)
state.refresh_me()
router.start()
