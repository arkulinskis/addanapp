"""Server tests against the strict mock of Anvil (tools/testing/mock).

    python tools/testing/test_server.py          -> prints ALL OK, or the first failure

call(name, ...) runs a server function the way the browser does: by name, with require_user enforced. Replies must
not contain table rows (dates are fine: Anvil sends them to the browser). Addanapp's server raises
Exception("message") for normal problems (the browser shows the message): problem(...) checks that.
Cover every server function: the happy path, bad input, and someone who isn't allowed.
"""
import datetime as dt
import importlib
import json
import os
import pathlib
import shutil
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
_tmp = pathlib.Path(tempfile.mkdtemp())
shutil.copytree(PROJECT / "server_code", _tmp / "app")
(_tmp / "app" / "__init__.py").write_text("")
os.environ["ANVIL_APP_YAML"] = str(PROJECT / "anvil.yaml")  # the mock's tables follow the app's own schema
sys.path[:0] = [str(HERE / "mock"), str(_tmp)]
import anvil.email  # noqa: E402
import anvil.server  # noqa: E402
import anvil.users  # noqa: E402
from anvil.tables import app_tables as T  # noqa: E402

M = {p.stem: importlib.import_module("app." + p.stem) for p in sorted((PROJECT / "server_code").glob("*.py"))}
now = dt.datetime.now(dt.timezone.utc)


def _plain(x):
    if type(x).__name__ == "Row":
        raise AssertionError("a table row reached the browser")
    return str(x)


def call(name, *args):
    r = anvil.server.call(name, *args)
    json.dumps(r, default=_plain)
    return r


def problem(name, *args, has=""):
    try:
        call(name, *args)
    except anvil.server.PermissionDenied:
        raise AssertionError("%s: permission denied, expected a message" % name)
    except Exception as e:
        assert has in str(e), (name, str(e))
        return str(e)
    raise AssertionError("%s should have refused %r" % (name, args))


def as_user(row):
    anvil.users.CURRENT[0] = row
    anvil.server.session.use(row.get_id() if row is not None else None)


def person(email, name=None, **kw):
    return T.users.add_row(email=email, enabled=True, signed_up=now, name=name, **kw)


# ---------------------------------------------------------------------------------- accounts
admin = person("arkulinskis@gmail.com", "The Consultant")
ana = person("ana@example.com", "Ana Client", company="Bistro Ana")
bob = person("bob.stone@example.com")

as_user(None)
problem("get_me", has="sign in")
assert call("poll_counts") == {}
as_user(admin)
me = call("get_me", "fr")
assert me["is_admin"] is True and admin["lang"] == "fr", "ADMIN_EMAILS become consultants; the language is kept for emails"
as_user(bob)
assert call("get_me")["name"] == "Bob Stone", "a name comes from the email when none is set"
problem("update_me", {"name": "x"}, has="name")
assert call("update_me", {"name": "  Bob  ", "phone": "514", "email_notifications": False})["phone"] == "514"
assert bob["email_notifications"] is False

# ---------------------------------------------------------------------------------- website: project brief
as_user(None)
good = {"name": "Jane", "email": "jane@company.com", "message": "We need a dashboard with roles.", "consent": True,
        "kind": "A client portal", "budget": "Under $10k"}
problem("submit_lead", dict(good, name="J"), has="name")
problem("submit_lead", dict(good, email="nope"), has="email")
problem("submit_lead", dict(good, message="short"), has="sentence")
problem("submit_lead", dict(good, consent=False), has="confirm")
assert call("submit_lead", dict(good, website="spam")) is True and not T.leads.search(), "the honeypot stores nothing"
n_mail = len(anvil.email.OUTBOX)
assert call("submit_lead", good) is True
lead = T.leads.search()[0]
assert lead["status"] == "new" and lead["source"] == "website" and len(anvil.email.OUTBOX) > n_mail, "consultants get an email"

# ---------------------------------------------------------------------------------- website: free guides
problem("request_guides", {"email": "bad"}, has="email")
res = call("request_guides", {"email": "reader@example.com", "name": "Rea", "situation": "Just curious", "newsletter": True,
                              "guide": "one-page-app-brief", "lang": "en"})
assert len(res["links"]) == 5 and res["emailed"] is True
g = T.leads.get(email="reader@example.com")
assert g["source"] == "guide+news" and "Newsletter: yes" in g["message"]
again = call("request_guides", {"email": "reader@example.com", "newsletter": False})
assert len(T.leads.search(email="reader@example.com")) == 1 and again["emailed"] is False, "one row, one email a day"
assert call("request_guides", {"email": "bot@example.com", "website": "x"})["emailed"] is False

# ---------------------------------------------------------------------------------- client workspace
as_user(ana)
problem("create_request", {"title": "abc", "description": "long enough text"}, has="title")
problem("create_request", {"title": "Deposits", "description": "short"}, has="Describe")
rid = call("create_request", {"title": "Deposits for parties", "description": "Parties of 8+ pay a deposit.", "kind": "feature",
                              "priority": "high", "budget": "Under $2,500", "desired_date": dt.date(2026, 12, 1)})
mine = call("my_requests")
assert mine["stats"]["open"] == 1 and mine["requests"][0]["id"] == rid and mine["requests"][0]["priority"] == "high"
detail = call("get_request", rid)
assert detail["is_admin"] is False and detail["request"]["status"] == "new"
assert call("client_action", rid, "comment", "One more detail")["notes"][-1]["body"] == "One more detail"
as_user(bob)
problem("get_request", rid, has="another workspace")
problem("client_action", rid, "withdraw", has="another workspace")
assert call("my_requests")["stats"]["total"] == 0

# ---------------------------------------------------------------------------------- consultant console
for fn, args in [("admin_overview", ()), ("admin_clients", ()), ("admin_leads", ()), ("admin_seed_demo", ()),
                 ("admin_update_request", (rid, {"status": "scoping"})), ("admin_set_user", (M["common"].rid(ana), {"is_admin": True})),
                 ("admin_newsletter_csv", ())]:
    problem(fn, *args, has="consultants")
as_user(admin)
ov = call("admin_overview")
assert any(r["id"] == rid for r in ov["requests"]) and ov["requests"][0]["client"]["email"] == "ana@example.com"
r = call("admin_update_request", rid, {"status": "quoted", "quote_amount": 2400, "quote_note": "Stripe deposits", "progress": 10}, None)
assert r["request"]["status"] == "quoted" and r["request"]["quote_amount"] == 2400
r = call("admin_update_request", rid, {}, {"body": "Internal only", "kind": "internal", "internal": True})
assert r["notes"][-1]["internal"] is True
as_user(ana)
assert call("poll_counts")["unread"] >= 1, "the quote shows as unread in the client's header"
seen = call("get_request", rid)
assert all(not n["internal"] for n in seen["notes"]), "clients never see internal notes"
r = call("client_action", rid, "approve_quote", "")
assert r["request"]["status"] == "in_progress"
as_user(admin)
assert call("admin_update_request", rid, {"status": "review", "progress": 100}, None)["request"]["status"] == "review"
as_user(ana)
assert call("client_action", rid, "accept", "")["request"]["status"] == "delivered"

as_user(admin)
people = call("admin_clients")
anas = next(p for p in people if p["email"] == "ana@example.com")
assert anas["delivered"] == 1 and anas["value"] == 2400
problem("admin_set_user", M["common"].rid(admin), {"is_admin": False}, has="own access")
assert call("admin_set_user", M["common"].rid(bob), {"enabled": False}) is True and bob["enabled"] is False
as_user(bob)
problem("get_me", has="disabled")
as_user(admin)
call("admin_set_user", M["common"].rid(bob), {"enabled": True})
other = call("admin_create_request", M["common"].rid(bob), {"title": "Weekly report", "description": "A PDF every Monday morning."})
assert call("get_request", other)["request"]["client"]["email"] == "bob.stone@example.com"
assert call("admin_delete_request", other) is not None
leads = call("admin_leads")
assert {x["source"] for x in leads} == {"website", "guide+news"}
lid = next(x["id"] for x in leads if x["source"] == "website")
assert call("admin_update_lead", lid, "contacted") is True and T.leads.get(source="website")["status"] == "contacted"
csv = call("admin_newsletter_csv")
assert b"reader@example.com" in csv.get_bytes()
assert call("admin_update_lead", lid, None, True) is True and not T.leads.search(source="website")
assert "Demo data loaded" in call("admin_seed_demo")
assert "already" in call("admin_seed_demo")
assert len(call("admin_overview")["requests"]) >= 9
assert "Removed demo data" in call("admin_clear_demo")
print("ALL OK")
