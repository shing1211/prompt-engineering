#!/usr/bin/env python3
"""Normalise heading hierarchy in prompt files.

Several prompts open with a title H1 and then use further `#` headings for
what are really top-level sections, leaving each document with multiple H1s.
That breaks the generated table of contents, since the site renders one nav
entry per H1.

This keeps the first H1 (the title) as H1 and demotes every later H1 to H2,
shifting the headings nested beneath it down one level so the parent/child
relationship survives. Idempotent: a document with a single H1 is untouched.

Run from the repository root.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROMPTS = Path("prompts")
SCAFFOLD = {"index", "tags"}
MAX_LEVEL = 6

HEADING_RE = re.compile(r"^(#{1,6})(\s+)(.*)$")


def normalise(path: Path) -> tuple[str, int]:
    lines = path.read_text(encoding="utf-8").split("\n")
    out: list[str] = []
    title_seen = False
    # Shift headings only once a demoted H1 has appeared, and keep shifting
    # for the rest of the document: each later H1 is a section whose children
    # need to drop a level to stay nested beneath it. A document with a
    # single H1 is left untouched.
    demoting = False
    shifted = 0

    for line in lines:
        match = HEADING_RE.match(line)
        if not match:
            out.append(line)
            continue

        hashes, space, rest = match.groups()
        level = len(hashes)

        if level == 1:
            if not title_seen:
                title_seen = True
                demoting = False
                out.append(line)
                continue
            # Every H1 after the first is a section, not a document title.
            demoting = True
            shifted += 1
            out.append(f"##{space}{rest}")
            continue

        if demoting:
            new_level = min(level + 1, MAX_LEVEL)
            if new_level != level:
                shifted += 1
            out.append(f"{'#' * new_level}{space}{rest}")
        else:
            out.append(line)

    return "\n".join(out), shifted


def main() -> int:
    changed_files = 0
    total_shifted = 0

    for path in sorted(PROMPTS.glob("*.md")):
        if path.stem in SCAFFOLD:
            continue
        original = path.read_text(encoding="utf-8")
        updated, shifted = normalise(path)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed_files += 1
            total_shifted += shifted
            print(f"  {path}: {shifted} heading(s) adjusted")

    print(
        f"heading hierarchy normalised: {changed_files} file(s) changed, "
        f"{total_shifted} heading(s) adjusted"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
