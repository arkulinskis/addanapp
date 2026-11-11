"""Apps: small formatting helpers for the dates and numbers the PC sends as text (ISO dates)."""
from anvil.js import window


def _ms(iso):
    if not iso:
        return None
    try:
        v = window.Date.parse(str(iso))
    except Exception:
        return None
    return None if v != v else v  # NaN


def ago(iso):
    """'3h ago' for an ISO date text (or a datetime)."""
    if iso is None or iso == '':
        return ''
    if not isinstance(iso, str):
        from . import ui
        return ui.ago(iso)
    ms = _ms(iso)
    if ms is None:
        return str(iso)[:10]
    s = (window.Date.now() - ms) / 1000
    if s < 90:
        return 'just now'
    if s < 3600:
        return '%dm ago' % round(s / 60)
    if s < 86400:
        return '%dh ago' % round(s / 3600)
    if s < 86400 * 45:
        return '%dd ago' % round(s / 86400)
    return str(iso)[:10]


def num(n):
    try:
        return '{:,}'.format(int(n or 0))
    except Exception:
        return str(n)


def plural(n, word, many=None):
    return '%d %s' % (n, word if n == 1 else (many or word + 's'))


def day_label(day):
    """'Nov 9' for '2026-11-09'."""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    try:
        y, m, d = str(day)[:10].split('-')
        return '%s %d' % (months[int(m) - 1], int(d))
    except Exception:
        return str(day)
