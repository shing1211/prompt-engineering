#!/usr/bin/env python3
"""Regenerate the generated tables inside prompts/index.md.

The region between the BEGIN/END GENERATED markers is rewritten from each
prompt's frontmatter, so category listings and counts cannot drift out of
sync with the files on disk. Everything outside the markers is preserved.

Run from the repository root:

    python3 scripts/generate_index.py          # rewrite prompts/index.md
    python3 scripts/generate_index.py --check  # exit 1 if stale (for CI)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROMPTS = Path("prompts")
INDEX = PROMPTS / "index.md"

INDEX_PAGES = {"index", "tags"}

BEGIN = "<!-- BEGIN GENERATED TABLES -->"
END = "<!-- END GENERATED TABLES -->"

CATEGORY_TITLES: dict[str, str] = {
    "orchestration": "Orchestration and Planning",
    "financial": "Financial Domain — Trading and Broking",
    "broker-sdk": "Broker SDKs",
    "sdk": "SDK Development",
    "architecture": "Architecture and Engineering",
    "platform": "Platform and Infrastructure",
    "protocols": "API Protocols",
    "data": "Data Platforms",
    "application": "Application Development",
    "java": "JVM and Java",
    "documentation": "Documentation",
}

CATEGORY_ORDER = list(CATEGORY_TITLES)

CATEGORY_BLURB: dict[str, str] = {
    "orchestration": "Multi-phase sub-agent execution and project planning",
    "financial": "Trading systems, market data, risk, quant, and compliance",
    "broker-sdk": "One prompt per broker, each a production Go SDK build",
    "sdk": "Reusable patterns for building and documenting SDKs",
    "architecture": "Cross-cutting engineering practice",
    "platform": "Kubernetes, packaging, delivery, and operability",
    "protocols": "GraphQL and gRPC specifics",
    "data": "Lakehouse, contracts, and data quality",
    "application": "Frontend, LLM, events, and data pipelines",
    "java": "Spring Boot, Quarkus, and the JVM",
    "documentation": "Documentation workflows",
}

# Tags surfaced in the Browse by Technology table, in display order.
FEATURED_TAGS: list[tuple[str, str]] = [
    ("Go / Golang", ("go", "golang")),
    ("Python", ("python",)),
    ("TypeScript", ("typescript",)),
    ("AWS", ("aws",)),
    ("Kafka / MSK", ("kafka", "msk")),
    ("Redis", ("redis",)),
    ("PostgreSQL", ("database", "postgresql")),
    ("React / Next.js", ("react", "nextjs")),
    ("GraphQL / Apollo", ("graphql", "apollo")),
    ("gRPC / Protobuf", ("grpc", "protobuf")),
    ("Kubernetes", ("kubernetes",)),
    ("Terraform", ("terraform",)),
    ("CI/CD", ("ci-cd",)),
    ("Security", ("security",)),
    ("Testing", ("testing",)),
    ("LLM / RAG", ("llm", "rag")),
    ("Market data", ("market-data",)),
    ("Trading", ("trading",)),
    ("Compliance", ("compliance", "regulatory")),
    ("Go SDK", ("sdk",)),
]

# Tags that mean "this prompt is written for that language". A prompt with
# none of these assumes no language-specific tooling and applies as-is, which
# is the cross-stack claim the library makes. Keep this list to actual
# implementation languages: framework, platform, and domain tags belong in
# FEATURED_TAGS instead.
LANGUAGE_TAGS: dict[str, tuple[str, ...]] = {
    "Go": ("go", "golang"),
    "Python": ("python",),
    "TypeScript": ("typescript", "javascript"),
    "Java / JVM": ("java", "kotlin", "scala"),
    "Rust": ("rust",),
    "C# / .NET": ("csharp", "dotnet"),
}

# Prompts matching none of the above are language-agnostic.

QUICK_REFERENCE: list[tuple[str, str]] = [
    ("Start a new project", "Orchestrate"),
    ("Plan the next phase", "Plan"),
    ("Design an API", "API Design"),
    ("Set up CI/CD", "DevOps"),
    ("Review code", "Code Review"),
    ("Security audit", "Security"),
    ("Design a database", "Database Design"),
    ("Build a broker SDK", "Broker SDKs"),
    ("Build a trading bot", "Trading Bot"),
    ("Wire up market data", "Market Data Pipeline"),
    ("Manage risk", "Trading Risk"),
    ("Backtest a strategy", "Quant Backtesting"),
    ("Track PnL and positions", "Portfolio Accounting"),
    ("Tune performance", "Performance"),
    ("Write tests", "Testing"),
    ("Plan a migration", "Migration"),
    ("Set up observability", "Observability and SRE"),
    ("Handle an incident", "Incident Response"),
    ("Build a frontend", "Frontend"),
    ("Integrate an LLM", "LLM Integration"),
    ("Build a data pipeline", "Data Engineering"),
]


def parse_frontmatter(text: str) -> dict[str, str]:
    """Return the frontmatter block as a flat string mapping."""
    lines = text.split("\n")
    if lines[0].strip() != "---":
        raise ValueError("missing frontmatter block")
    end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")

    meta: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta


def load() -> list[dict[str, object]]:
    prompts: list[dict[str, object]] = []
    for path in sorted(PROMPTS.glob("*.md")):
        if path.stem in INDEX_PAGES:
            continue
        meta = parse_frontmatter(path.read_text(encoding="utf-8"))
        raw_tags = meta.get("tags", "[]")
        tags = re.findall(r'"([^"]+)"', raw_tags)
        prompts.append(
            {
                "slug": path.stem,
                "title": meta.get("title", path.stem),
                "description": meta.get("description", ""),
                "mode": meta.get("mode", "all"),
                "category": meta.get("category", "application"),
                "tags": tags,
            }
        )
    return prompts


def esc(text: str) -> str:
    return text.replace("|", "\\|")


def render(prompts: list[dict[str, object]]) -> str:
    out: list[str] = [BEGIN, ""]

    by_category: dict[str, list[dict[str, object]]] = {}
    for entry in prompts:
        by_category.setdefault(str(entry["category"]), []).append(entry)

    out.append("## Browse by Category")
    out.append("")
    for category in CATEGORY_ORDER:
        entries = by_category.get(category)
        if not entries:
            continue
        out.append(f"### {CATEGORY_TITLES[category]}")
        out.append("")
        out.append(f"{CATEGORY_BLURB[category]} — {len(entries)} prompt(s).")
        out.append("")
        out.append("| Prompt | Mode | Description |")
        out.append("|---|---|---|")
        for entry in entries:
            title = entry["title"]
            out.append(
                f"| [`{entry['slug']}.md`]({entry['slug']}.md) — {esc(str(title))} "
                f"| {entry['mode']} | {esc(str(entry['description']))} |"
            )
        out.append("")

    out.append("## Browse by Technology")
    out.append("")
    out.append("| Technology | Prompts |")
    out.append("|---|---|")
    for label, keys in FEATURED_TAGS:
        matched = [
            p
            for p in prompts
            if set(p["tags"]) & set(keys)  # type: ignore[operator]
        ]
        if not matched:
            continue
        links = ", ".join(f"[{p['slug']}]({p['slug']}.md)" for p in sorted(matched, key=lambda x: str(x["slug"])))
        out.append(f"| {label} | {links} |")
    out.append("")

    out.append("## Browse by Language")
    out.append("")
    out.append(
        "Prompts written against a specific language's tooling. Everything "
        "not listed here assumes no language-specific tooling and applies "
        "as written."
    )
    out.append("")
    out.append("| Language | Prompts |")
    out.append("|---|---|")
    all_language_keys = {k for keys in LANGUAGE_TAGS.values() for k in keys}
    for label, keys in LANGUAGE_TAGS.items():
        matched = [
            p for p in prompts if set(p["tags"]) & set(keys)  # type: ignore[operator]
        ]
        if not matched:
            continue
        links = ", ".join(
            f"[{p['slug']}]({p['slug']}.md)"
            for p in sorted(matched, key=lambda x: str(x["slug"]))
        )
        out.append(f"| {label} | {links} |")
    agnostic = [
        p
        for p in prompts
        if not (set(p["tags"]) & all_language_keys)  # type: ignore[operator]
    ]
    if agnostic:
        links = ", ".join(
            f"[{p['slug']}]({p['slug']}.md)"
            for p in sorted(agnostic, key=lambda x: str(x["slug"]))
        )
        out.append(f"| **Any stack** | {links} |")
    out.append("")

    out.append("## Quick Reference")
    out.append("")
    out.append("| Task | Prompt |")
    out.append("|---|---|")
    slug_by_title = {str(p["title"]): str(p["slug"]) for p in prompts}
    for task, title in QUICK_REFERENCE:
        slug = slug_by_title.get(title)
        if slug is None:
            continue
        out.append(f"| {task} | [`{slug}.md`]({slug}.md) |")
    out.append("")

    out.append("## Statistics")
    out.append("")
    out.append("| Metric | Count |")
    out.append("|---|---|")
    out.append(f"| **Total prompts** | {len(prompts)} |")
    for category in CATEGORY_ORDER:
        entries = by_category.get(category)
        if entries:
            out.append(f"| **{CATEGORY_TITLES[category]}** | {len(entries)} |")
    unique_tags = {tag for p in prompts for tag in p["tags"]}  # type: ignore[union-attr]
    out.append(f"| **Distinct tags** | {len(unique_tags)} |")
    out.append(f"| **Language-agnostic** | {len(agnostic)} |")
    for mode in sorted({str(p["mode"]) for p in prompts}):
        out.append(f"| **Mode: {mode}** | {sum(1 for p in prompts if p['mode'] == mode)} |")
    out.append("")

    out.append(END)
    return "\n".join(out)


def splice(document: str, generated: str) -> str:
    start = document.find(BEGIN)
    stop = document.find(END)
    if start == -1 or stop == -1:
        raise SystemExit(f"error: {INDEX} is missing the GENERATED markers")
    return document[:start] + generated + document[stop + len(END) :]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the generated region is current instead of rewriting it",
    )
    args = parser.parse_args()

    prompts = load()
    generated = render(prompts)
    current = INDEX.read_text(encoding="utf-8")
    updated = splice(current, generated)

    if args.check:
        if updated != current:
            print(
                "error: prompts/index.md generated tables are stale; "
                "run python3 scripts/generate_index.py",
                file=sys.stderr,
            )
            return 1
        print(f"generated tables are current ({len(prompts)} prompts)")
        return 0

    if updated != current:
        INDEX.write_text(updated, encoding="utf-8")
        print(f"rewrote generated tables in {INDEX} ({len(prompts)} prompts)")
    else:
        print(f"generated tables already current ({len(prompts)} prompts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
