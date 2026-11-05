"""Refresh the theme assets' cache-busting hashes in anvil.yaml (and icons.css).

    python tools/assets.py

native_deps.head_html in anvil.yaml loads the app's own files as _/theme/<file>?v=<hash>. After changing any of them,
run this so browsers fetch the new copy. It also rebuilds icons.css from app-kit.js. Only the ?v= values change, as a
text edit (Addanapp's head holds a large hand-written SEO block, so the YAML is never re-dumped).
The language packs (lang-*.json) are fetched by the head script with i18n.VERSION, not by this.
"""
import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "theme" / "assets"


def main():
    subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "build_icons.py")], check=True)
    path = ROOT / "anvil.yaml"
    text = path.read_text(encoding="utf-8")

    def fresh(m):
        f = ASSETS / m.group(1)
        if not f.exists():
            sys.exit("head_html loads _/theme/%s, but theme/assets/%s doesn't exist" % (m.group(1), m.group(1)))
        return "_/theme/%s?v=%s" % (m.group(1), hashlib.sha1(f.read_bytes()).hexdigest()[:10])

    new = re.sub(r"_/theme/([\w.\-/]+\.(?:css|js))\?v=[0-9a-f]+", fresh, text)
    if new != text:
        path.write_bytes(new.encode("utf-8"))
        print("anvil.yaml: asset hashes updated")
    else:
        print("anvil.yaml: asset hashes already current")


if __name__ == "__main__":
    main()
