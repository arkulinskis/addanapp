"""App health (#apps/health, consultants only): every app's admin status report in one place.

Each app answers GET <app>/_/api/admin/status (APP_MAKER/template-forms/server_code/AppStatus.py) for requests signed
with Addanapp's private key, so no sign-in to 60 apps is needed. The key lives only in this app's App Secret
`status_signing_key` (JSON {"n": hex, "e": 65537, "d": hex}; the user's copy: %USERPROFILE%/.addanapp/status_signing_key.json).
The apps hold the public half in their code (it can check a signature, never make one).

    health_list()        the apps (from the portfolio cards' url) with their last stored check
    health_check(keys)   check up to BATCH apps now (in parallel), store and return the results
    health_report(key)   the full stored report of one app (recent errors with tracebacks)
"""
import concurrent.futures
import datetime as dt
import hashlib
import json
import secrets
import time
import urllib.error
import urllib.request

import anvil.secrets
import anvil.server
from anvil.tables import app_tables

from .common import current_user

SECRET = "status_signing_key"
BATCH = 8
TIMEOUT = 10        # per app (urllib); a slow DNS lookup isn't covered by it, hence DEADLINE
DEADLINE = 20       # per batch: Anvil stops a server call after 30 s; apps still pending count as "unreachable"
_SHA256_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")
HINTS = {
    "ok": "Reporting.",
    "not_installed": "The status report isn't live yet: open the app in the Anvil editor and publish the latest version.",
    "signature": "The app didn't accept Addanapp's signature: publish its latest version in the Anvil editor.",
    "forbidden": "The app refused the request: publish its latest version in the Anvil editor.",
    "app_error": "The app had an error making the report: open it in the Anvil editor (App Logs).",
    "unreachable": "The app didn't answer: check its address and that it's published.",
    "no_key": "Addanapp's signing key is missing: add the App Secret status_signing_key in the Anvil editor.",
}


def _require_admin():
    u = current_user()
    if not u["is_admin"]:
        raise anvil.server.PermissionDenied("Only consultants can see app health.")
    return u


def _now():
    return dt.datetime.now(dt.timezone.utc)


def _host(url):
    v = str(url or "").strip().lower()
    for prefix in ("https://", "http://"):
        if v.startswith(prefix):
            v = v[len(prefix):]
    return v.split("/")[0]


def _signing_key():
    try:
        k = json.loads(anvil.secrets.get_secret(SECRET))
        return int(k["n"], 16), int(k["d"], 16)
    except Exception:
        return None


def sign_headers(url, key):
    """The X-Addanapp-* headers for one request to `url` (RSA PKCS#1 v1.5 / SHA-256, pure Python)."""
    n, d = key
    ts, nonce = str(int(time.time())), secrets.token_hex(8)
    msg = "addanapp-status-v1|%s|%s|%s" % (_host(url), ts, nonce)
    size = (n.bit_length() + 7) // 8
    digest = hashlib.sha256(msg.encode()).digest()
    em = b"\x00\x01" + b"\xff" * (size - 3 - len(_SHA256_PREFIX) - len(digest)) + b"\x00" + _SHA256_PREFIX + digest
    sig = pow(int.from_bytes(em, "big"), d, n)
    return {"X-Addanapp-Ts": ts, "X-Addanapp-Nonce": nonce, "X-Addanapp-Sig": format(sig, "x")}


def fetch(url, key, errors=10):
    """-> (status, http code, ms, report or None). Runs in worker threads: no Anvil calls in here."""
    started = time.time()
    target = url.rstrip("/") + "/_/api/admin/status?errors=%d" % errors
    req = urllib.request.Request(target, headers=dict(sign_headers(url, key), Accept="application/json",
                                                      **{"User-Agent": "Addanapp-AppHealth/1"}))
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read(3_000_000)
            code = r.status
    except urllib.error.HTTPError as e:
        status = {404: "not_installed", 401: "signature", 403: "forbidden"}.get(e.code, "app_error")
        return status, e.code, int((time.time() - started) * 1000), None
    except Exception:
        return "unreachable", 0, int((time.time() - started) * 1000), None
    ms = int((time.time() - started) * 1000)
    try:
        report = json.loads(body.decode("utf-8"))
    except Exception:  # an app without the report can answer 200 with its normal page
        return "not_installed", code, ms, None
    if not isinstance(report, dict) or "app" not in report:
        return "not_installed", code, ms, None
    return "ok", code, ms, report


def _apps():
    """Every app with a live address on any portfolio card, once each, by name."""
    seen = {}
    for r in app_tables.app_projects.search():
        card = r["card"] or {}
        url = card.get("url")
        # every apps.json app is an Anvil app (own domains too: adorablescience.com); websites (arkvital.com) aren't
        anvil_app = card.get("source") == "apps.json" or card.get("anvil_editor") or ".anvil.app" in str(url)
        if r["key"] and url and str(url).startswith("http") and anvil_app and r["key"] not in seen:
            seen[r["key"]] = {"key": r["key"], "name": r["name"] or card.get("name") or r["key"], "url": str(url).rstrip("/"),
                              "editor": card.get("anvil_editor") or None}
    return sorted(seen.values(), key=lambda a: str(a["name"]).lower())


def _num(d, *path):
    for p in path:
        if not isinstance(d, dict):
            return None
        d = d.get(p)
    return d if isinstance(d, (int, float)) and not isinstance(d, bool) else None


def summary(report):
    """The numbers the page draws, from one app's report (any section may be missing)."""
    if not report:
        return None
    users, db, errs = report.get("users") or {}, report.get("database") or {}, report.get("errors") or {}
    tasks = report.get("background_tasks") or {}
    return {
        "users": _num(users, "total"), "admins": _num(users, "admins"),
        "active_7d": _num(users, "active", "7d") if _num(users, "active", "7d") is not None else _num(users, "signed_in", "7d"),
        "signups_7d": _num(users, "signed_up", "7d"), "signups_30d": _num(users, "signed_up", "30d"),
        "signups_by_day": users.get("signups_by_day_30d") or {},
        "rows": _num(db, "total_rows"), "tables": _num(db, "tables"),
        "per_table": {k: (v or {}).get("rows") for k, v in (db.get("per_table") or {}).items()},
        "errors_on": bool(errs.get("available")), "errors_24h": _num(errs, "last_24h"), "errors_7d": _num(errs, "last_7d"),
        "error_sessions_7d": _num(errs, "sessions_with_errors_7d"),
        "top_error": ((errs.get("top_7d") or [{}])[0] or {}).get("message"),
        "tasks_failed": sum(v for k, v in (tasks.get("last_7d") or {}).items() if k in ("failed", "killed", "missing")),
        "secret": (report.get("app") or {}).get("admin_emails_secret"),
        "version": (report.get("app") or {}).get("report_version"),
    }


def _hint(status, s):
    if status != "ok" or not s:
        return HINTS.get(status, "")
    todo = []
    if not s["errors_on"]:
        todo.append("accept the Schema Mismatch (error_log table)")
    if s["secret"] != "set":
        todo.append("add the App Secret admin_emails")
    return ("Reporting. To finish: " + " and ".join(todo) + ".") if todo else HINTS["ok"]


def _row_dict(app, row):
    if row is None:
        return dict(app, status=None, checked=None, summary=None, hint="Not checked yet.", http=None, ms=None)
    s = summary(row["report"])
    return dict(app, status=row["status"], checked=row["checked"].isoformat() if row["checked"] else None,
                http=row["http"], ms=row["ms"], summary=s, hint=_hint(row["status"], s))


@anvil.server.callable(require_user=True)
def health_list():
    _require_admin()
    rows = {r["key"]: r for r in app_tables.app_health.search()}
    return {"apps": [_row_dict(a, rows.get(a["key"])) for a in _apps()], "key_ok": _signing_key() is not None,
            "batch": BATCH}


@anvil.server.callable(require_user=True)
def health_check(keys):
    _require_admin()
    key = _signing_key()
    apps = {a["key"]: a for a in _apps()}
    todo = [apps[k] for k in list(keys or [])[:BATCH] if k in apps]
    if key is None:
        return [dict(a, status="no_key", hint=HINTS["no_key"], summary=None, checked=None, http=None, ms=None) for a in todo]
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=BATCH)
    futures = [pool.submit(fetch, a["url"], key) for a in todo]
    concurrent.futures.wait(futures, timeout=DEADLINE)
    results = [f.result() if f.done() else ("unreachable", 0, DEADLINE * 1000, None) for f in futures]
    pool.shutdown(wait=False)  # don't wait for stragglers
    out = []
    stamp = _now()
    for a, (status, code, ms, report) in zip(todo, results):
        row = app_tables.app_health.get(key=a["key"])
        if row is None:
            row = app_tables.app_health.add_row(key=a["key"], name=a["name"], url=a["url"], checked=stamp,
                                                status=status, http=code, ms=ms, report=report)
        else:
            row.update(name=a["name"], url=a["url"], checked=stamp, status=status, http=code, ms=ms)
            if report is not None:           # a failed check keeps the last good numbers
                row["report"] = report
        out.append(_row_dict(a, row))
    return out


@anvil.server.callable(require_user=True)
def health_report(key):
    _require_admin()
    row = app_tables.app_health.get(key=str(key or ""))
    return None if row is None else row["report"]
