#!/usr/bin/env python3
"""Check that every prompt file appears in the mkdocs nav.

MkDocs builds a page even when it is absent from `nav:`; it only logs an
INFO line saying so, which `--strict` does not treat as a failure. The
result is a prompt that renders and is reachable by URL but is missing
from the sidebar, with nothing in CI to notice.

This compares the `.md` leaves in `mkdocs.yml`'s nav against the files in
`prompts/`, and fails on either direction of drift:

  - a prompt file that no nav entry points at (invisible in the sidebar)
  - a nav entry pointing at a file that does not exist (dead nav link)

Run from the repository root. Exits 0 when clean, 1 on drift.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

MKDOCS = Path("mkdocs.yml")
PROMPTS = Path("prompts")

# Site scaffolding rather than prompts, both of which are expected in nav.
SCAFFOLD = {"index.md", "tags.md"}


def nav_targets(node: object, found: list[str]) -> None:
    """Collect every string leaf in the nav tree.

    Nav entries are either ``Title: file.md`` or ``Group:`` followed by a
    nested list, so this walks both shapes.
    """
    if isinstance(node, list):
        for item in node:
            nav_targets(item, found)
    elif isinstance(node, dict):
        for value in node.values():
            nav_targets(value, found)
    elif isinstance(node, str) and node.endswith(".md"):
        found.append(node)


def main() -> int:
    if not MKDOCS.is_file():
        print(f"error: {MKDOCS} not found; run from the repository root", file=sys.stderr)
        return 1

    config = yaml.safe_load(MKDOCS.read_text(encoding="utf-8"))
    nav = config.get("nav")
    if not nav:
        print("error: mkdocs.yml has no nav:", file=sys.stderr)
        return 1

    listed: list[str] = []
    nav_targets(nav, listed)

    on_disk = {
        p.name
        for p in PROMPTS.glob("*.md")
        if p.name not in SCAFFOLD
    }
    in_nav = set(listed)

    print(f"{len(on_disk)} prompt files, {len(in_nav)} nav entries")

    missing = sorted(on_disk - in_nav)
    dangling = sorted(in_nav - on_disk - SCAFFOLD)

    for name in missing:
        print(f"  not in nav: {name}")
    for name in dangling:
        print(f"  nav entry has no file: {name}")

    unlisted_scaffold = sorted(SCAFFOLD - in_nav)

    if missing or dangling:
        print(
            f"\n{len(missing)} prompt(s) missing from nav, "
            f"{len(dangling)} dangling nav entry(ies)",
            file=sys.stderr,
        )
        print(
            "\nnav is hand-maintained by design. Add each missing prompt to the\n"
            "right group in mkdocs.yml, keeping the category order used by\n"
            "scripts/apply_categories.py."
        )
        return 1

    if unlisted_scaffold:
        # Not a failure: index.md and tags.md are reachable regardless, and
        # index.md in particular is linked from the site header.
        print(f"  note: not in nav, but expected: {', '.join(unlisted_scaffold)}")

    print("every prompt file is listed in the nav")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
