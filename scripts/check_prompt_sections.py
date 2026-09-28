#!/usr/bin/env python3
"""Check that every prompt carries the sections the library promises.

README.md and CONTRIBUTING.md both present two sections as what makes a
prompt worth reading over a wall of prose:

  - Anti-Patterns (Never Do These)
  - Guardrails

Seven prompts had neither when this check was first written, and fourteen
had only one. All 38 now carry both.

This check is structural: it asserts the section exists, not that its
content is good. It cannot tell a specific anti-pattern from a generic one,
and does not try. A prompt can pass this check and still be filler, which
is why the content is written and reviewed by hand. What the check prevents
is the next prompt from shipping without the sections at all, which is how
the gap opened.

Exits 0 when clean, 1 on drift.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROMPTS = Path("prompts")

# Site scaffolding rather than prompts.
SCAFFOLD = {"index", "tags"}

# Heading text, matched loosely so "## Layer 6: Anti-Patterns (Never Do
# These)" and "## Anti-Patterns" both count.
ANTI_PATTERN_RE = re.compile(r"^#{2,4}\s.*anti-?patterns?", re.I | re.M)
GUARDRAIL_RE = re.compile(r"^#{2,4}\s.*\b(guardrails?|validation)\b", re.I | re.M)


def main() -> int:
    missing: list[tuple[str, str]] = []
    checked = 0

    for path in sorted(PROMPTS.glob("*.md")):
        if path.stem in SCAFFOLD:
            continue
        checked += 1
        body = path.read_text(encoding="utf-8").split("\n---", 1)[-1]

        if not ANTI_PATTERN_RE.search(body):
            missing.append((path.name, "anti-patterns"))
        if not GUARDRAIL_RE.search(body):
            missing.append((path.name, "guardrails"))

    print(f"checked {checked} prompts for anti-patterns and guardrails sections")

    for name, section in missing:
        print(f"  {name}: no {section} section")

    if missing:
        print(
            "\nEvery prompt needs an anti-patterns section and a guardrails\n"
            "section. Both are part of what makes a prompt worth reading.\n"
            "Venue-specific content belongs in the prompt; the shared gates\n"
            "live in sdk-build.md under Cross-Cutting Guardrails.",
            file=sys.stderr,
        )
        return 1

    print("every prompt has anti-patterns and guardrails")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
