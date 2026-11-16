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
import anvil.secrets  # noqa: E402
anvil.secrets.SECRETS["admin_emails"] = "admin@example.com"  # the App Secret, faked
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
admin = person("admin@example.com", "The Consultant")
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
# ---------------------------------------------------------------------------------- apps (portfolio board)
import base64  # noqa: E402
S = anvil.server
ep = S.ENDPOINTS["/apps/v1/:action"]


def api(action, body=None, key="aal_local_test_key", origin="http://localhost:3030"):
    S.ORIGIN[0] = origin
    S.request.headers = {"Authorization": "Bearer " + key} if key else {}
    S.request.body = json.dumps(body or {})
    S.request.query_params = {}
    resp = ep(action=action)
    S.ORIGIN[0] = "https://app-test.anvil.app"
    return resp.status, json.loads(resp.body)


as_user(admin)
problem("apps_board", has="No client")
assert api("hello", {"client": "pf@example.com"}, key="")[0] == 401, "no key, no entry"
assert api("hello", {"client": "pf@example.com"}, key="wrong")[0] == 401
assert api("hello", {"client": "pf@example.com"}, origin="https://addanapp.com")[0] == 401, "the test key only works locally"
assert api("hello", {"client": "nobody@example.com"})[0] == 400, "unknown client without create"
PH = [{"id": "build", "name": "Build", "items": [{"id": "github", "label": "Code on GitHub"}]},
      {"id": "promote", "name": "Promote", "items": [{"id": "linkedin", "label": "LinkedIn post"}, {"id": "admin", "label": "Admin tested"}]}]
card = {"name": "Snack App", "desc": "Snack App: orders for cafés", "auto": {"github": True}, "url": "https://snack.example",
        "live": {"ok": False, "status": 502, "checked": now.isoformat()}, "seo": {"missing": ["robots.txt"], "checks": {}},
        "branches": [{"name": "forms", "ahead": 2, "base": "master", "compare_url": "https://github.com/x/compare"}],
        "youtube": {"public": True, "published": "2026-11-02", "url": "https://youtu.be/x"}, "watch": True,
        "commits": [{"msg": "c%d" % i} for i in range(12)]}
st, res = api("push", {"client": "PF@example.com", "create": {"name": "Arkvital", "company": "Arkvital"},
                       "meta": {"phases": PH, "refreshed_at": now.isoformat(), "errors": ["GitHub: rate limited"]},
                       "projects": [{"key": "snack", "name": "Snack App", "card": card, "state_seed": {"notes": "hi", "x": 1},
                                     "promo": {"items": [{"id": "li1", "kind": "linkedin", "title": "a", "text": "Post"}]}},
                                    {"key": "gh:old", "name": "Old", "card": {}}],
                       "docs": [{"name": "bizdev/README", "text": "# Plans\n\n- [Snack](apps/snack.md) **now**\n\n| a | b |\n|---|---|\n| 1 | 2 |"},
                                {"name": "bizdev/apps/snack", "text": "# Snack\n\nSell to cafés."},
                                {"name": "bizdev/index", "data": {"apps": [{"key": "snack", "name": "Snack App", "rank": 1, "wave": "1"}]}},
                                {"name": "worker", "data": {"seen": "spoof"}}]})
assert st == 200 and res["added"] == 2, res
pf = T.users.get(email="pf@example.com")
assert pf is not None and pf["is_admin"] is False and pf["company"] == "Arkvital", "the portfolio's client account is made"
assert T.app_projects.get(key="snack")["state"] == {"notes": "hi"}, "only the browser-owned parts of the old state are seeded"
assert api("push", {"client": "pf@example.com", "projects": [], "keep": ["snack"]})[1]["removed"] == 1
png = base64.b64encode(b"\x89PNG fake").decode()
assert api("media", {"client": "pf@example.com", "key": "snack", "field": "hero", "type": "image/png", "data": png, "v": "1"})[0] == 200
assert api("media", {"client": "pf@example.com", "key": "snack", "field": "evil", "data": png})[0] == 400
assert T.app_projects.get(key="snack")["hero"] is not None

me = call("get_me")
assert me["apps"] is True, "consultants see the Apps menu once a portfolio exists"
b = call("apps_board")
p = b["projects"][0]
assert b["client"]["name"] == "Arkvital" and len(b["clients"]) == 1
assert p["desc"] == "orders for cafés" and p["stage"] == "promote" and p["next"] == "LinkedIn post"
assert p["items"]["github"] == {"v": "done", "auto": True}
assert p["posted"]["yt-video"] == "2026-11-02", "a public pitch video counts as published"
assert p["hero"] is not None and "commits" not in p
types = {n["type"] for n in b["notes"]}
assert {"error", "down", "seo", "merge"} <= types, types
assert "worker" not in b and T.app_docs.get(client=T.users.get(email="pf@example.com"), name="worker") is None, "the worker doc can't be pushed"
full = call("apps_project", "snack")
assert len(full["commits"]) == 8 and full["promo"]["items"][0]["text"] == "Post"
problem("apps_project", "nope", has="isn't in this portfolio")

r = call("apps_tick", "snack", "linkedin")
assert r["project"]["items"]["linkedin"]["v"] == "done" and r["project"]["stage"] == "promote"
r = call("apps_tick", "snack", "admin")
assert r["project"]["stage"] == "launched"
assert call("apps_tick", "snack", "admin")["project"]["items"]["admin"]["v"] == "na"
problem("apps_tick", "snack", "bogus", has="Unknown step")
r = call("apps_set_state", "snack", {"posted": {"li1": True}, "notes": "remember", "parked": True})
assert r["project"]["stage"] == "parked" and r["project"]["posted"]["li1"] and r["project"]["notes"] == "remember"
call("apps_set_state", "snack", {"parked": False, "posted": {"li1": False}})

problem("apps_add_change", "snack", "short", has="sentence")
r = call("apps_add_change", "snack", "Make the order button bigger on phones.")
req = T.requests.get(project="snack")
assert req["status"] == "in_progress" and req["client"] == pf and req["kind"] == "change"
assert r["project"]["changes_todo"][0]["ref"] == req["ref"]
assert any(n["type"] == "changes" and n["prompt"] == "/app-board run snack" for n in r["notes"])

# Refresh from addanapp.com itself (apps_refresh.py): fake web replies, no network
RF = M["apps_refresh"]
WEB = {}
HITS = []


def fake_http(url, headers=None, limit=600000, method="GET", body=None):
    HITS.append((method, url, body))
    for prefix in sorted(WEB, key=len, reverse=True):
        if url.startswith(prefix):
            v = WEB[prefix]
            if isinstance(v, Exception):
                raise v
            st, data = v
            return st, data if isinstance(data, str) else json.dumps(data)
    return 404, ""


RF.http = fake_http
problem("apps_refresh", ["snack"], [], has="Tick")
problem("apps_refresh", ["snack"], ["github"], has="github_token")
anvil.secrets.SECRETS["github_token"] = "ghp_test"
r = T.app_projects.get(key="snack")
r["card"] = dict(r["card"], repo="me/snack", source="apps.json", key="snack")
YAML = "db_schema:\n  orders:\n    client: none\n    columns:\n    - admin_ui: {order: 0, width: 200}\n      name: item\n      type: string\n    - name: qty\n      type: number\n    server: full\n"
WEB.update({
    "https://api.github.com/repos/me/snack/commits": (200, [{"sha": "abc1234567", "html_url": "u", "commit": {"message": "Fix menu\n\nmore",
                                                          "committer": {"date": "2026-11-16T10:00:00Z"}, "author": {"name": "Ark"}}}]),
    "https://api.github.com/repos/me/snack/branches": (200, [{"name": "master", "commit": {"sha": "m1"}}, {"name": "forms", "commit": {"sha": "f1"}},
                                                            {"name": "old", "commit": {"sha": "m1"}}]),
    "https://api.github.com/repos/me/snack/pulls": (200, []),
    "https://api.github.com/repos/me/snack/compare/master...forms": (200, {"ahead_by": 3, "behind_by": 0, "commits": [{"commit": {"message": "Forms", "committer": {"date": "2026-11-15"}}}]}),
    "https://api.github.com/repos/me/snack/compare/master...old": (200, {"ahead_by": 0, "behind_by": 2, "commits": []}),
    "https://api.github.com/repos/me/snack/contents/anvil.yaml": (200, {"content": base64.b64encode(YAML.encode()).decode()}),
    "https://api.github.com/repos/me/snack": (200, {"full_name": "me/snack", "default_branch": "master", "description": "Orders for cafés",
                                                   "html_url": "https://github.com/me/snack", "pushed_at": "2026-11-16T10:00:00Z"}),
    "https://snack.example/robots.txt": (200, "User-agent: *"),
    "https://snack.example/sitemap.xml": (200, "<urlset></urlset>"),
    "https://snack.example/_/api/schema-check": (200, {"tables": {"orders": ["item"]}}),
    "https://snack.example": (200, '<title>Snack</title><meta name="description" content="Orders for cafes, fast and simple">'
                                   '<link rel="canonical" href="x"><meta property="og:title"><meta property="og:image">'),
    "https://arkvital.com/": (200, "<a href='https://snack.example'>Snack</a>"),
    "https://addanapp.com/": (500, ""),
})
res = call("apps_refresh", ["snack"], ["github", "live", "schema", "mentions", "hacked"], True, True, True)
p = res["projects"][0]
assert p["pushed_at"] == "2026-11-16T10:00:00Z" and p["desc"] == "Orders for cafés"
assert [b["name"] for b in p["branches"]] == ["forms"] and p["branches_merged"] == ["old"], p["branches"]
assert p["live"]["ok"] and p["seo"]["missing"] == [] and p["auto"]["seo"] and p["auto"]["anvil"] and p["auto"]["domain"]
assert p["schema"]["state"] == "mismatch" and p["schema"]["missing_columns"] == ["orders.qty"], p["schema"]
assert p["auto"]["arkvital"] is True and "addanapp" not in p["auto"], "a site that doesn't answer isn't counted"
assert RF.tables_of(YAML) == {"orders": ["item", "qty"]}
card = T.app_projects.get(key="snack")["card"]
assert card["server"]["at"] and card["server"]["branches_raw"][0]["sha"] == "f1" and card["server"]["schema_exp"]["tables"]
assert T.app_docs.get(client=pf, name="meta")["data"]["server_refreshed_at"] and call("apps_board")["refreshed_at"]
assert M["apps_core"].latest("2026-01-01T00:00:00+00:00", "2026-02-01T00:00:00+00:00", "") == "2026-02-01T00:00:00+00:00"
n = len(HITS)
call("apps_refresh", ["snack"], ["github"])
assert not any("/compare/" in h[1] for h in HITS[n:]), "unchanged branches aren't compared again"
WEB["https://api.github.com/repos/me/snack"] = (500, "")
res = call("apps_refresh", ["snack"], ["github"], True)
assert res["errors"] and "GitHub answered 500" in res["errors"][0] and res["projects"][0]["pushed_at"], "a failed check keeps the last facts"
assert any(n_["type"] == "error" for n_ in res["notes"])
WEB["https://api.github.com/repos/me/snack"] = (401, "")
assert "github_token" in call("apps_refresh", ["snack"], ["github"], True)["errors"][0]
WEB["https://api.github.com/repos/me/snack"] = (200, {"full_name": "me/snack", "default_branch": "master", "html_url": "h", "pushed_at": "2026-11-16T11:00:00Z"})
call("apps_refresh", ["snack"], ["github"], True)
problem("apps_refresh", ["nope"], ["live"], has="isn't in this portfolio")

# a PC push with older facts keeps what Refresh found; newer facts win
old_card = dict(T.app_projects.get(key="snack")["card"])
api("push", {"client": "pf@example.com", "projects": [{"key": "snack", "name": "Snack App",
                                                         "card": dict(old_card, pushed_at="2020-01-01", facts_at="2020-01-01T00:00:00+00:00", legal={"ok": True})}]})
c2 = T.app_projects.get(key="snack")["card"]
assert c2["pushed_at"] == "2026-11-16T11:00:00Z" and c2["legal"] == {"ok": True} and c2["server"], "older PC facts don't overwrite"
api("push", {"client": "pf@example.com", "projects": [{"key": "snack", "name": "Snack App",
                                                         "card": dict(old_card, pushed_at="2030-01-01", facts_at="2030-01-01T00:00:00+00:00")}]})
assert T.app_projects.get(key="snack")["card"]["pushed_at"] == "2030-01-01", "newer PC facts win"

# links typed on the board: shown at once, cleared once the PC has copied them
problem("apps_save_link", "snack", "url", "not a url", has="web address")
problem("apps_save_link", "snack", "evil", "https://x.example", has="Unknown link")
WEB["https://snack2.example"] = (200, "<title>Snack 2</title>")
r = call("apps_save_link", "snack", "url", "https://snack2.example")
assert r["project"]["url"] == "https://snack2.example" and r["project"]["url_followup"] and r["project"]["live"]["ok"]
assert T.app_projects.get(key="snack")["state"]["links"] == {"url": "https://snack2.example"}
assert api("pull", {"client": "pf@example.com"})[1]["states"]["snack"]["links"]["url"] == "https://snack2.example", "the PC sees it"
api("push", {"client": "pf@example.com", "projects": [{"key": "snack", "name": "Snack App", "card": dict(old_card, url="https://snack2.example")}]})
assert T.app_projects.get(key="snack")["state"]["links"] == {}, "copied into apps.json -> no longer an override"

# Prepsto, with Claude's key as an App Secret
problem("apps_send_idea", "snack", "Save as PDF", has="no Prepsto")
r = T.app_projects.get(key="snack")
r["card"] = dict(r["card"], prepsto="abc123")
problem("apps_send_idea", "snack", "Save as PDF", has="prepsto_key")
anvil.secrets.SECRETS["prepsto_key"] = "pk_test"
problem("apps_send_idea", "snack", "x", has="Write the idea")
WEB["https://prepsto.com/_/api/v1/tickets"] = (200, {"ticket": {"url": "https://prepsto.com/t/1", "kind": "bug"}, "total": 1,
                                                     "tickets": [{"id": "t1", "message": "Broken", "kind": "bug", "status": "open"}]})
WEB["https://prepsto.com/_/api/v1/links"] = (200, {"links": [{"code": "abc123", "id": "L1"}]})
assert call("apps_send_idea", "snack", "Save as PDF", "bug") == {"url": "https://prepsto.com/t/1", "kind": "bug"}
sent = [h for h in HITS if h[0] == "POST" and "prepsto" in h[1]][-1]
assert sent[2]["link"] == "abc123" and sent[2]["kind"] == "bug" and sent[2]["page_url"] == "https://snack2.example"
t = call("apps_tickets", "snack")
assert t["total"] == 1 and t["tickets"][0]["message"] == "Broken" and "link=L1" in HITS[-1][1]
assert call("apps_project", "snack")["ideas"]["total"] == 1, "the last tickets stay on the app"

# YouTube public numbers with an API key
problem("apps_youtube_update", has="No YouTube numbers yet")
api("push", {"client": "pf@example.com", "docs": [{"name": "youtube", "data": {"latest": {"channel": {"id": "UC1", "subscribers": 1},
                                                    "videos": [{"id": "v1", "views": 3, "app": "snack"}, {"id": "v2", "views": 9, "privacy": "private"}]},
                                                    "history": {}, "analytics": {"daily": [1]}}}]})
problem("apps_youtube_update", has="youtube_api_key")
anvil.secrets.SECRETS["youtube_api_key"] = "AIza_test"
WEB["https://www.googleapis.com/youtube/v3/channels"] = (200, {"items": [{"statistics": {"subscriberCount": "12", "viewCount": "400", "videoCount": "2"}}]})
WEB["https://www.googleapis.com/youtube/v3/videos"] = (200, {"items": [{"id": "v1", "statistics": {"viewCount": "50", "likeCount": "4"}, "status": {"privacyStatus": "public"}}]})
y = call("apps_youtube_update")
vids = {v["id"]: v for v in y["latest"]["videos"]}
assert y["latest"]["channel"]["subscribers"] == 12 and vids["v1"]["views"] == 50 and vids["v1"]["app"] == "snack"
assert vids["v2"]["views"] == 9, "a private video keeps the PC's numbers"
assert y["analytics"] == {"daily": [1]} and list(y["history"].values())[0]["videos"]["v1"][0] == 50
WEB["https://www.googleapis.com/youtube/v3/channels"] = (403, {"error": {"message": "API key not valid"}})
problem("apps_youtube_update", has="API key not valid")

d = call("apps_dismiss", "seo:snack", "x")
assert d == {"seo:snack": "x"} and call("apps_dismiss", "seo:snack", "x") == {}
bz = call("apps_bizdev", "README")
assert '<a href="#apps/bizdev/apps.snack">Snack</a>' in bz["html"] and "<b>now</b>" in bz["html"] and "<table>" in bz["html"]
assert call("apps_bizdev", "apps.snack")["html"].startswith("<h2>Snack")
assert call("apps_bizdev", "../../etc")["name"] == "README"
assert "<script>" not in M["apps_core"].markdown("<script>alert(1)</script>"), "plans are escaped"
assert call("apps_bizdev_plan", "snack")["html"] == "<p>Sell to cafés.</p>"
problem("apps_add_outreach", {"date": "2026-11-11"}, has="at least")
problem("apps_add_outreach", {"date": "11/11", "app": "Snack"}, has="date")
assert len(call("apps_add_outreach", {"app": "Snack App", "channel": "Email", "result": "no reply"})["rows"]) == 1

st, pl = api("pull", {"client": "pf@example.com"})
assert pl["states"]["snack"]["notes"] == "remember" and pl["changes"][0]["key"] == "snack" and len(pl["outreach"]["rows"]) == 1
api("push", {"client": "pf@example.com", "outreach_rows": [pl["outreach"]["rows"][0], ["2026-11-01", "Snack App", "Walk-in"]]})
assert len(call("apps_add_outreach", {"app": "x", "who": "y"})["rows"]) == 3, "the PC's rows are merged without doubles"
assert api("state", {"client": "pf@example.com", "key": "snack", "set": {"checks": {"admin": "done"}}})[1]["state"]["checks"]["admin"] == "done"
st, ch = api("changes", {"client": "pf@example.com"})
cid = ch["changes"][0]["id"]
assert api("done", {"client": "pf@example.com", "id": cid, "summary": "Bigger button, pushed to master."})[0] == 200
assert req["status"] == "review" and T.notes.get(request=req, kind="validated") is not None
assert api("changes", {"client": "pf@example.com"})[1]["changes"] == [], "changes in review aren't Claude's to do"
assert api("change", {"client": "pf@example.com", "key": "snack", "text": "Add a French menu to the app."})[1]["ref"]
assert len(api("board", {"client": "pf@example.com"})[1]["projects"]) == 1

as_user(ana)
assert call("get_me")["apps"] is False
problem("apps_board", has="no app portfolio")
problem("apps_tick", "snack", "admin", has="no app portfolio")
as_user(pf)
assert call("apps_board")["client"]["name"] == "Arkvital", "the client sees their own portfolio"
assert call("apps_board", M["common"].rid(ana))["client"]["name"] == "Arkvital", "client_id is ignored for clients"

print("ALL OK")
