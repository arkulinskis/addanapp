"""Which template texts have no translation? (Offline; the UI test checks the same thing in the browser.)

    python -I tools/i18n_check.py            -> every data-t text / data-ta attribute / prop:text|placeholder|tooltip
                                                in client_code/**/form_template.html missing from lang-fr/ru/lv.json

The packs are keyed by the English text exactly as the browser serialises it (whitespace collapsed), so a template
text that differs by one character from its key falls back to English. Fix the template (or add the key to all three
packs, and bump i18n.VERSION + the head script's ?v=). Keys listed in KNOWN_UNTRANSLATED were never translated in the
old app either (brand words, tech tags): they are allowed.
"""
import html
import html.parser
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKS = {c: json.loads((ROOT / "theme" / "assets" / ("lang-%s.json" % c)).read_text(encoding="utf-8")) for c in ("fr", "ru", "lv")}
KNOWN_UNTRANSLATED = {'CMS', 'CSV / PDF', 'Canvas', 'ETL', 'LLMs', 'PWA', 'RAG', 'RBAC', 'REST', 'SEO', 'Stripe',
                      'Send brief →'}  # tech words; the Send button's text is set in Python
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Keys(html.parser.HTMLParser):
    """Collect (key, kind) from a template: inner HTML of data-t elements (as written), data-ta attributes, props."""

    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text, self.keys, self.stack = text, [], []
        self.lines = [0]
        for line in text.splitlines(keepends=True):
            self.lines.append(self.lines[-1] + len(line))

    def _pos(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        end = self._pos() + len(self.get_starttag_text())
        if "data-t" in a and not a.get("data-t"):
            self.stack.append((tag, end, True))
        elif tag not in VOID:
            self.stack.append((tag, end, False))
        if a.get("data-t"):
            self.keys.append((a["data-t"], "data-t"))
        for name in (a.get("data-ta") or "").split(","):
            name = name.strip()
            if name and a.get(name):
                self.keys.append((a[name], "attr " + name))
        if tag == "anvil-component":
            for k in ("prop:text", "prop:placeholder", "prop:tooltip"):
                if a.get(k):
                    self.keys.append((a[k], k))

    def handle_endtag(self, tag):
        start = self._pos()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                t, inner_start, marked = self.stack[i]
                del self.stack[i:]
                if marked:
                    inner = self.text[inner_start:start]
                    self.keys.append((re.sub(r"\s+", " ", inner).strip(), "data-t"))
                return


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    missing = {}
    total = 0
    for f in sorted((ROOT / "client_code").rglob("form_template.html")):
        text = f.read_text(encoding="utf-8")
        if text.startswith("---"):
            text = text.split("---", 2)[2]
        p = Keys(text)
        p.feed(text)
        for key, kind in p.keys:
            if "{" in key and "}" in key and not key.strip("{}"):
                continue
            total += 1
            if key in KNOWN_UNTRANSLATED:
                continue
            plain = html.unescape(key) if kind.startswith("prop") or kind.startswith("attr") else key
            for code, pack in PACKS.items():
                if key not in pack and plain not in pack and plain.replace("&", "&amp;") not in pack:
                    missing.setdefault(key, set()).add(code)
                    missing[key].add("@" + str(f.relative_to(ROOT / "client_code").parent))
    for key in sorted(missing):
        where = sorted(x for x in missing[key] if x.startswith("@"))
        langs = sorted(x for x in missing[key] if not x.startswith("@"))
        print("MISSING %-9s %-60s %s" % (",".join(langs), key[:60], " ".join(where)[:80]))
    print("%d template texts, %d without a translation" % (total, len(missing)))
    sys.exit(1 if "--strict" in sys.argv and missing else 0)


if __name__ == "__main__":
    main()
