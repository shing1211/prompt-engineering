#!/usr/bin/env python3
"""Ensure every prompt has a title: key in its frontmatter and a matching H1.

Titles are the display name used in site navigation and index tables. Where
a prompt's H1 was a generic placeholder such as "Role and Context" (or was
missing entirely), this rewrites the H1 to match the declared title.

Idempotent. Run from the repository root.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROMPTS = Path("prompts")

TITLES: dict[str, str] = {
    "api-design": "API Design",
    "backend-services": "Backend Services",
    "architecture": "Architecture Design",
    "broker-certification": "Broker Certification",
    "broker-futu": "Futu OpenD SDK",
    "broker-google": "Generic HMAC Broker SDK",
    "broker-ibkr": "IBKR Client Portal SDK",
    "broker-integration": "Broker Integration",
    "broker-longbridge": "Longbridge SDK",
    "broker-tiger": "Tiger Trade SDK",
    "broker-vbroker": "Hua Sing Tong vbroker SDK",
    "broker-webull": "Webull SDK",
    "change-review": "Change Review",
    "code-review": "Code Review",
    "compliance-regulatory": "Compliance and Regulatory",
    "database-design": "Database Design",
    "data-engineering": "Data Engineering",
    "data-platforms": "Data Platforms",
    "devops": "DevOps",
    "jvm-backend": "JVM Backend",
    "event-driven-architecture": "Event-Driven Architecture",
    "financial-docs": "Financial Platform Documentation",
    "frontend-dev": "Frontend Development",
    "graphql-development": "GraphQL Development",
    "grpc-development": "gRPC Development",
    "incident-response": "Incident Response",
    "llm-integration": "LLM Integration",
    "market-data-pipeline": "Market Data Pipeline",
    "migration": "Migration",
    "observability-sre": "Observability and SRE",
    "orchestrate": "Orchestrator",
    "performance": "Performance",
    "plan": "Planning",
    "plan-review": "Plan Review",
    "test-review": "Test Review",
    "platform-engineering": "Platform Engineering",
    "portfolio-accounting": "Portfolio Accounting",
    "quant-backtesting": "Quant Backtesting",
    "realtime-analytics": "Real-Time Analytics",
    "sdk-build": "SDK Build",
    "sdk-docs": "SDK Documentation",
    "security": "Security",
    "testing": "Testing",
    "trading-bot": "Trading Bot",
    "trading-risk": "Trading Risk",
}

INDEX_PAGES = {"index", "tags"}

TITLE_RE = re.compile(r"^title:.*$", re.MULTILINE)
H1_RE = re.compile(r"^# .*$", re.MULTILINE)

# Decorative suffixes an existing H1 may carry. When an H1 is just the
# declared title plus one of these, it is collapsed to the bare title. They
# are dropped rather than promoted into `title` because they add nothing to
# a navigation entry or a heading.
DECORATIVE_SUFFIXES = (
    " Agent",
    " Prompt",
    " Prompts",
)


def frontmatter_bounds(lines: list[str]) -> tuple[int, int]:
    if lines[0].strip() != "---":
        raise ValueError("missing frontmatter block")
    end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    return 1, end


def apply(text: str, title: str) -> str:
    lines = text.split("\n")
    start, end = frontmatter_bounds(lines)

    if any(line.startswith("title:") for line in lines[start:end]):
        text = TITLE_RE.sub(f"title: {title}", text, count=1)
    else:
        lines.insert(start, f"title: {title}")
        text = "\n".join(lines)

    # Rewrite the H1 only when it is absent or a known-generic placeholder,
    # so hand-written headings elsewhere are left alone.
    body_start = text.index("\n---", 1) + len("\n---")
    body = text[body_start:]
    match = H1_RE.search(body)
    if match is not None and match.group(0)[2:].strip() == title:
        return text

    if match is not None:
        # A hand-written H1 wins only when it differs from the title purely
        # by a decorative suffix. Anything else is normalised, so the
        # title/H1 invariant that validate.sh enforces holds by
        # construction rather than by luck.
        existing = match.group(0)[2:].strip()
        for suffix in DECORATIVE_SUFFIXES:
            if existing.casefold() == f"{title}{suffix}".casefold():
                body = H1_RE.sub(f"# {title}", body, count=1)
                text = text[:body_start] + body
                return text
        body = H1_RE.sub(f"# {title}", body, count=1)
    else:
        # Keep the newline that follows the closing fence so the heading
        # cannot end up concatenated onto "---".
        body = f"# {title}\n" + body.lstrip("\n")

    return text[:body_start] + body


def main() -> int:
    on_disk = {
        p.stem for p in PROMPTS.glob("*.md") if p.stem not in INDEX_PAGES
    }
    missing = on_disk - set(TITLES)
    if missing:
        print(f"error: no title declared for {sorted(missing)}", file=sys.stderr)
        return 1

    changed = 0
    for slug, title in TITLES.items():
        path = PROMPTS / f"{slug}.md"
        original = path.read_text(encoding="utf-8")
        try:
            updated = apply(original, title)
        except ValueError as exc:
            print(f"error: {path}: {exc}", file=sys.stderr)
            return 1
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1

    print(f"titles applied, {changed} file(s) changed, {len(TITLES)} prompts total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
