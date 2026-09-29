#!/usr/bin/env python3
"""Check that hand-written counts agree with the generated index.

The generated statistics block in prompts/index.md is authoritative: it is
produced from frontmatter by scripts/generate_index.py. README.md and
docs/strategy.md also state counts in prose, and those are hand-maintained.

They drifted. README claimed 38 prompts and 19 covering multi-broker
trading when the library held 42 and 16, and the "19" was wrong from the
first release. Nothing detected it, because nothing compared the two.

This reads the generated figures and fails on any hand-written count in the
scanned documents that disagrees. It checks:

  - the total prompt count
  - the language-agnostic count
  - the combined financial-domain count, which sums two categories and so
    has no single generated row to compare against

It cannot verify that a hand-written sentence is *true* about anything the
index does not measure. It only prevents a number from diverging from the
data it claims to summarise.

Exits 0 when clean, 1 on drift.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

INDEX = Path("prompts/index.md")

# Documents whose prose is scanned. CHANGELOG.md is deliberately excluded:
# its counts are historical release notes describing the state at a given
# version, so "38 prompts" under the 0.1.0 heading is correct in context.
DOCUMENTS = [Path("README.md"), Path("docs/strategy.md")]

# Categories that make up the "financial trading" claim. Kept here rather
# than hardcoded as a number, so the check follows the library instead of
# freezing today's arithmetic.
FINANCIAL_CATEGORIES = ("Financial Domain", "Broker SDKs")


def generated_stats() -> dict[str, int]:
    """Read the statistics block from the generated index."""
    text = INDEX.read_text(encoding="utf-8")
    block = re.search(
        r"## Statistics\s*\n(.*?)(?:<!-- END GENERATED|\Z)", text, re.S
    )
    if not block:
        raise SystemExit(f"error: no Statistics block in {INDEX}")

    stats: dict[str, int] = {}
    for label, value in re.findall(r"\|\s*\*\*([^*]+)\*\*\s*\|\s*(\d+)\s*\|", block.group(1)):
        stats[label.strip()] = int(value)
    return stats


def expected(stats: dict[str, int]) -> dict[str, int]:
    """Map a regex over a hand-written sentence to the value it must equal."""
    total = stats.get("Total prompts")
    agnostic = stats.get("Language-agnostic")
    financial = sum(
        v for k, v in stats.items() if any(k.startswith(c) for c in FINANCIAL_CATEGORIES)
    )

    checks: dict[str, int] = {}
    if total is not None:
        checks["total"] = total
    if agnostic is not None:
        checks["agnostic"] = agnostic
    if financial:
        checks["financial"] = financial
    return checks


# (name, regex, which expected value it must match). Each regex must match
# the whole count phrase, not a fragment, so "19 of the 38" is captured whole.
PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "total prompt count",
        re.compile(r"\b(\d+)\s+prompts\b"),
        "total",
    ),
    (
        "language-agnostic count",
        re.compile(
            r"\b(\d+)\s+of\s+the\s+\d+\s+(?:prompts\s+are\s+)?"
            r"language-agnostic",
            re.I,
        ),
        "agnostic",
    ),
    (
        "multi-broker trading count",
        re.compile(
            r"\b(\d+)\s+of\s+the\s+\d+\s+prompts\s+cover\s+multi-broker\s+trading",
            re.I,
        ),
        "financial",
    ),
    (
        "multi-broker trading count (prose)",
        re.compile(
            r"\b(\d+)\s+of\s+the\s+\d+\s+prompts\s+here\s+cover\s+multi-broker\s+trading",
            re.I,
        ),
        "financial",
    ),
]


def main() -> int:
    if not INDEX.is_file():
        raise SystemExit(f"error: {INDEX} not found; run from the repository root")

    stats = generated_stats()
    want = expected(stats)
    if not want:
        raise SystemExit(f"error: could not read expected values from {INDEX}")

    print(
        f"generated: {want.get('total')} prompts, "
        f"{want.get('agnostic')} language-agnostic, "
        f"{want.get('financial')} in the financial domain"
    )

    problems: list[str] = []
    scanned = 0

    for doc in DOCUMENTS:
        if not doc.is_file():
            print(f"  note: {doc} not found, skipping")
            continue
        scanned += 1
        for lineno, line in enumerate(doc.read_text(encoding="utf-8").split("\n"), 1):
            for label, pattern, key in PATTERNS:
                for match in pattern.finditer(line):
                    stated = int(match.group(1))
                    if want.get(key) is not None and stated != want[key]:
                        problems.append(
                            f"{doc}:{lineno}: {label} says {stated}, "
                            f"generated index says {want[key]}"
                        )

    print(f"checked {scanned} documents for hand-written counts")

    for problem in problems:
        print(f"  {problem}")

    if problems:
        print(
            "\nHand-written counts must match the generated statistics in\n"
            f"{INDEX}, which is produced from frontmatter. Fix the prose, or\n"
            "regenerate the index if the library itself has changed.",
            file=sys.stderr,
        )
        return 1

    print("every hand-written count matches the generated index")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
