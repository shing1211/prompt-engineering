#!/usr/bin/env python3
"""Check that every relative link in the built site resolves.

Run after `mkdocs build`, from the repository root. Absolute URLs and
fragment-only links are skipped; the check is about internal navigation
breaking.

Exits 0 when clean, 1 when any link is broken.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SITE = Path("site")
HREF_RE = re.compile(r'href="([^"#?]+)"')

# Generated 404.html is written for the site root, so its links are absolute
# and would all look broken from inside site/.
SKIP = {"404.html"}


def main() -> int:
    if not SITE.is_dir():
        print("error: site/ not found; run mkdocs build first", file=sys.stderr)
        return 1

    pages = [p for p in SITE.rglob("*.html") if p.name not in SKIP]
    if not pages:
        print("error: site/ contains no HTML pages", file=sys.stderr)
        return 1

    broken: list[tuple[str, str]] = []
    checked = 0

    for page in pages:
        text = page.read_text(encoding="utf-8", errors="ignore")
        for href in HREF_RE.findall(text):
            if href.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            if href.startswith("/"):
                # Root-relative: only valid if it lands inside this project.
                if not href.startswith("/prompt-engineering/"):
                    continue
                target = SITE / href[len("/prompt-engineering/") :]
            else:
                target = page.parent / href
            checked += 1
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                broken.append((str(page.relative_to(SITE)), href))

    if broken:
        print(f"{len(broken)} broken link(s) out of {checked} checked:", file=sys.stderr)
        for page, href in broken[:40]:
            print(f"  {page} -> {href}", file=sys.stderr)
        return 1

    print(f"{checked} relative internal links resolve across {len(pages)} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
