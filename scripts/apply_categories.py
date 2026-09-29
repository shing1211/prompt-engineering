#!/usr/bin/env python3
"""Insert a category: key into each prompt's YAML frontmatter.

Idempotent: re-running replaces an existing category line rather than
adding a second one. Run from the repository root.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROMPTS = Path("prompts")

CATEGORIES: dict[str, list[str]] = {
    "orchestration": ["orchestrate", "plan"],
    "financial": [
        "broker-integration",
        "broker-certification",
        "market-data-pipeline",
        "realtime-analytics",
        "trading-bot",
        "trading-risk",
        "quant-backtesting",
        "portfolio-accounting",
        "compliance-regulatory",
    ],
    "broker-sdk": [
        "broker-longbridge",
        "broker-tiger",
        "broker-webull",
        "broker-ibkr",
        "broker-futu",
        "broker-vbroker",
        "broker-google",
    ],
    "sdk": ["sdk-build", "sdk-docs"],
    "architecture": [
        "architecture",
        "backend-services",
        "api-design",
        "database-design",
        "code-review",
        "change-review",
        "plan-review",
        "testing",
        "security",
        "performance",
        "devops",
        "migration",
        "observability-sre",
        "incident-response",
    ],
    "protocols": ["graphql-development", "grpc-development"],
    "data": [
        "data-platforms",
    ],
    "java": [
        "jvm-backend",
    ],
    "platform": [
        "platform-engineering",
    ],
    "application": [
        "frontend-dev",
        "llm-integration",
        "event-driven-architecture",
        "data-engineering",
    ],
    "documentation": ["financial-docs"],
}

NAME_TO_CATEGORY = {
    name: category for category, names in CATEGORIES.items() for name in names
}

ALL = list(NAME_TO_CATEGORY)
INDEX_PAGES = {"index", "tags"}

CATEGORY_RE = re.compile(r"^category:.*$", re.MULTILINE)


def apply(text: str, category: str) -> str:
    """Return text with exactly one category: line inside the frontmatter."""
    if CATEGORY_RE.search(text):
        return CATEGORY_RE.sub(f"category: {category}", text, count=1)

    lines = text.split("\n")
    if lines[0].strip() != "---":
        raise ValueError("no frontmatter block")

    end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    for i in range(1, end):
        if lines[i].startswith("tags:"):
            lines.insert(i, f"category: {category}")
            return "\n".join(lines)

    lines.insert(end, f"category: {category}")
    return "\n".join(lines)


def main() -> int:
    if len(ALL) != len(set(ALL)):
        print("error: a prompt is listed in two categories", file=sys.stderr)
        return 1

    changed = 0
    for name in ALL:
        path = PROMPTS / f"{name}.md"
        if not path.exists():
            print(f"error: missing {path}", file=sys.stderr)
            return 1

        original = path.read_text(encoding="utf-8")
        updated = apply(original, NAME_TO_CATEGORY[name])
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1

    on_disk = {
        p.stem for p in PROMPTS.glob("*.md") if p.stem not in INDEX_PAGES
    }
    unclassified = on_disk - set(ALL)
    if unclassified:
        print(f"error: no category for {sorted(unclassified)}", file=sys.stderr)
        return 1

    print(f"categories applied, {changed} file(s) changed, {len(ALL)} prompts total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
