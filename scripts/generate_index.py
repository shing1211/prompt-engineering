#!/usr/bin/env python3
"""Regenerate the generated tables inside prompts/index.md.

The region between the BEGIN/END GENERATED markers is rewritten from each
prompt's frontmatter, so category listings and counts cannot drift out of
sync with the files on disk. Everything outside the markers is preserved.

The `Verified` column is not read from the prompts. It is read from
docs/verification.md, which is the single place that records which prompts
have been run against a real codebase, and the generator refuses to run if
the two disagree. That direction is deliberate: a column derived from the
prompts would have nothing to say "verified" from, and a column derived from
a default would label a prompt unverified for the one reason that matters —
that nobody recorded a run.

Run from the repository root:

    python3 scripts/generate_index.py          # rewrite prompts/index.md
    python3 scripts/generate_index.py --check  # exit 1 if stale (for CI)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

PROMPTS = Path("prompts")
INDEX = PROMPTS / "index.md"
MKDOCS = Path("mkdocs.yml")
VERIFICATION = Path("docs/verification.md")

INDEX_PAGES = {"index", "tags"}

BEGIN = "<!-- BEGIN GENERATED TABLES -->"
END = "<!-- END GENERATED TABLES -->"

# A row of the register in docs/verification.md: the prompt's file name, then
# whether it has been run. The flag is captured as whatever is written rather
# than as `yes|no`, so a row that says something else is reported as a
# malformed row instead of quietly failing to match and being reported as a
# missing one. Only the first two columns are read; the rest are prose for a
# human and are deliberately not parsed, so the register's table can say more
# than the generator needs without either drifting.
REGISTER_ROW = re.compile(
    r"^\|\s*`(?P<slug>[a-z0-9][a-z0-9-]*)`\s*\|\s*(?P<verified>[^|]*?)\s*\|"
)
REGISTER_FLAGS = {"yes": True, "no": False}

# The cell for a prompt with no run. A literal rather than an empty cell: an
# empty column is read as a rendering accident, and "not verified" is a
# claim the library is prepared to make out loud.
NOT_VERIFIED = "not verified"
VERIFIED_CELL = "verified"

CATEGORY_TITLES: dict[str, str] = {
    "orchestration": "Orchestration and Planning",
    "architecture": "Architecture and Engineering",
    "application": "Application Development",
    "platform": "Platform and Infrastructure",
    "protocols": "API Protocols",
    "sdk": "SDK Development",
    "data": "Data Platforms",
    "java": "JVM and Java",
    "documentation": "Documentation",
    "financial": "Financial Engineering — Trading and Broking",
    "broker-sdk": "Broker SDKs",
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


def repository_url() -> str:
    """The URL a rendered page can reach the register at.

    Absolute, and derived from mkdocs.yml's own repo_url, for two reasons that
    point the same way. The register is a repository document, not a site
    page: mkdocs' docs_dir is prompts/ and this file is not under it, so a
    relative link from a rendered page resolves in the working tree and
    resolves to nothing in the built site. check_links.py cannot catch that,
    because it resolves links against the working tree where the target does
    exist. And the URL is read rather than repeated, so a fork or a rename
    cannot leave a verified link in every row of the index pointing at a
    repository that no longer exists.
    """
    if not MKDOCS.is_file():
        raise SystemExit(f"error: {MKDOCS} not found; run from the repository root")

    config = yaml.safe_load(MKDOCS.read_text(encoding="utf-8")) or {}
    repo = str(config.get("repo_url") or "").strip()
    if not repo:
        raise SystemExit(
            f"error: {MKDOCS} has no repo_url, so the Verified column has nowhere\n"
            f"to point. Add repo_url, or point the column somewhere else."
        )
    return f"{repo.rstrip('/')}/blob/main/"


def verification_register() -> dict[str, bool]:
    """The prompt slug to verified mapping recorded in docs/verification.md.

    Fails loudly in both directions, because the failure this guards against
    is silent in the one place it matters. A prompt that drops out of the
    register and is then rendered as "not verified" is indistinguishable from
    a prompt somebody deliberately decided not to run, and a reader has no
    way to tell which one they are looking at. So an absent row is an error
    rather than a default, and a row naming a prompt that no longer exists is
    an error too — that is a register that has drifted from the library, and
    it fails at the moment it drifts rather than at the moment somebody
    notices the table.
    """
    if not VERIFICATION.is_file():
        raise SystemExit(
            f"error: {VERIFICATION} not found; it is the source of the Verified\n"
            f"column, and a column with no source is a guess."
        )

    register: dict[str, bool] = {}
    for lineno, line in enumerate(VERIFICATION.read_text(encoding="utf-8").split("\n"), 1):
        match = REGISTER_ROW.match(line)
        if not match:
            continue
        slug = match.group("slug")
        flag = match.group("verified").lower()
        if flag not in REGISTER_FLAGS:
            raise SystemExit(
                f"error: {VERIFICATION}:{lineno}: {slug} has "
                f"{match.group('verified').strip()!r} in its Verified column.\n"
                f"Expected yes or no. Anything else is a claim the generator cannot\n"
                f"act on, and guessing which way round it meant is how an unverified\n"
                f"prompt ends up labelled verified."
            )
        if slug in register:
            raise SystemExit(
                f"error: {VERIFICATION}:{lineno}: {slug} is listed twice, so the\n"
                f"register disagrees with itself about whether it was run."
            )
        register[slug] = REGISTER_FLAGS[flag]

    on_disk = {p.stem for p in PROMPTS.glob("*.md")} - INDEX_PAGES

    unknown = sorted(set(register) - on_disk)
    if unknown:
        raise SystemExit(
            f"error: {VERIFICATION} names prompts that do not exist: "
            f"{', '.join(unknown)}\n"
            f"A prompt was renamed, merged or deleted and the register was not\n"
            f"updated. Fix the register, not this script."
        )

    missing = sorted(on_disk - set(register))
    if missing:
        raise SystemExit(
            f"error: {VERIFICATION} has no row for: {', '.join(missing)}\n"
            f"Every prompt needs a row. A prompt with no row has not been run, and\n"
            f"that has to be written down, because the alternative is a column that\n"
            f"reports the same thing for a prompt nobody checked and a prompt\n"
            f"somebody checked and found nothing."
        )

    return register


def verified_cell(slug: str, register: dict[str, bool], url: str) -> str:
    """The Verified cell for one prompt.

    Two states and no third, because the third — a blank — is the one that
    hides an error. Nothing here can return one: a slug that is neither
    verified nor present has already stopped the run.
    """
    if not register[slug]:
        return NOT_VERIFIED
    return f"[{VERIFIED_CELL}]({url}{VERIFICATION.as_posix()})"


def render(prompts: list[dict[str, object]], register: dict[str, bool], url: str) -> str:
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
        out.append("| Prompt | Mode | Description | Verified |")
        out.append("|---|---|---|---|")
        for entry in entries:
            title = entry["title"]
            slug = str(entry["slug"])
            out.append(
                f"| [`{slug}.md`]({slug}.md) — {esc(str(title))} "
                f"| {entry['mode']} | {esc(str(entry['description']))} "
                f"| {verified_cell(slug, register, url)} |"
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
    out.append(f"| **Verified** | {sum(1 for was_run in register.values() if was_run)} |")
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

    # Read the register before doing anything else with the output, including
    # under --check. A drift check that skipped this would report the index
    # as current when the source it is generated from has names in it that
    # the library does not have, which is the one disagreement worth being
    # loud about.
    register = verification_register()
    url = repository_url()

    prompts = load()
    generated = render(prompts, register, url)
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
