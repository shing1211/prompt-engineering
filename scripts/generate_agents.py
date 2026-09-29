#!/usr/bin/env python3
"""Generate harness-native agent definitions from the prompt set.

`prompts/*.md` is the only hand-edited source. This script renders it into the
three directory layouts the supported harnesses actually read, so that a
reader who clones the repository gets named agents rather than 45 loose
Markdown files they have to place themselves:

    .opencode/agents/prompt-<slug>.md       OpenCode  (1.18.x markdown agents)
    .claude/agents/prompt-<slug>.md         Claude Code subagents
    .agents/skills/prompt-<slug>/SKILL.md   Codex skills

The output is committed rather than built. A consumer copies or symlinks one
of the three directories and has a working agent set, with no runtime, no
install step, and no dependency on the rest of the repository. The cost is
about 2 MB of duplicated prompt text and a drift gate to keep it honest; the
benefit is that installation is how a reader discovers what the library
contains, which is the whole point of packaging it.

The bodies are copied verbatim. Nothing is reworded, reordered, or trimmed, so
the file a reader inspects in `prompts/` is byte-for-byte the system prompt
their agent runs, and the authoritative version is never in doubt. The one
thing added is an HTML comment naming the source file, which costs the model a
few tokens and tells a human who opens the generated tree where it came from.

The `mode` field carries a permission policy, and this is where it stops being
a label. `plan` and `review` are documented in README.md as non-mutating, and
OpenCode enforces that here with `permission: edit: deny`; Claude Code gets a
tool allow-list that omits Write and Edit, which is as close as its frontmatter
allows. Codex skills have no permission mechanism, so on that surface the policy
is prose in the prompt body and nothing more. The unevenness is deliberate and
recorded rather than papered over: the library does not claim enforcement it
does not have.

Run from the repository root:

    python3 scripts/generate_agents.py          # write the three trees
    python3 scripts/generate_agents.py --check  # exit 1 on drift (for CI)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_index import INDEX_PAGES, PROMPTS, parse_frontmatter  # noqa: E402

# The namespace every generated agent carries. It is not decoration: without
# it `plan.md` renders as an agent called `plan`, and OpenCode ships a built-in
# primary agent of that name while Claude Code ships a built-in subagent called
# `Plan`. Overriding a built-in is a supported move on both, so shipping an
# unprefixed name would silently replace it. The prefix also makes provenance
# obvious in an agent menu that a user shares with other libraries.
PREFIX = "prompt-"

# Modes that are documented as non-mutating. They get a write restriction;
# every other mode is left at the harness default, which is unrestricted.
READONLY_MODES = {"plan", "review"}

# The tool set for a non-mutating agent. Write and Edit are absent from an
# allow-list rather than denied explicitly, which is how Claude Code spells
# "not allowed". Bash is kept deliberately: README.md says a plan or review
# prompt may run the acceptance command or a test suite, and a reviewer that
# cannot run anything cannot verify anything. The residual gap is that a
# allow-list cannot separate a read-only bash from one that writes, so the shell
# is bounded by the prompt's own guardrails rather than by the harness.
READONLY_TOOLS = "Read, Glob, Grep, Bash"

OPENCODE_AGENTS = Path(".opencode/agents")
CLAUDE_AGENTS = Path(".claude/agents")
CODEX_SKILLS = Path(".agents/skills")

# Directories this script owns outright. Anything inside one of them that it
# did not write is drift, and is removed on write and reported on check. The
# siblings matter: `.opencode/commands` and `.opencode/skills` belong to
# OpenSpec and are deliberately outside every path here.
OWNED: dict[Path, str] = {
    OPENCODE_AGENTS: "agents",
    CLAUDE_AGENTS: "agents",
    CODEX_SKILLS: "skills",
}


def banner(slug: str) -> str:
    """The provenance comment, worded so it cannot read as an instruction.

    A first draft ended this line "do not edit". It is carried into the system
    prompt verbatim, HTML comments included, so a `build` agent read "do not
    edit" as a rule and suppressed the file writing that its mode licenses.
    The banner now describes what it is and stops there.
    """
    return (
        f"<!-- generated from {PROMPTS}/{slug}.md by scripts/generate_agents.py;"
        " provenance only -->"
    )


def read_prompt(path: Path) -> dict[str, str]:
    """Return one prompt's frontmatter and body."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if lines[0].strip() != "---":
        raise SystemExit(f"error: {path} has no frontmatter block")
    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        raise SystemExit(f"error: {path} has no closing frontmatter fence") from None
    body = "\n".join(lines[end + 1 :]).lstrip("\n").rstrip("\n")
    return {"meta": parse_frontmatter(text), "body": body, "slug": path.stem}


def doc(frontmatter: str, slug: str, body: str) -> str:
    """Assemble one generated file: fence, frontmatter, banner, body."""
    return f"---\n{frontmatter}---\n{banner(slug)}\n\n{body}\n"


def opencode(meta: dict[str, str], slug: str, body: str) -> str:
    """OpenCode markdown agent.

    `mode: subagent` is stated rather than inherited. OpenCode 1.18 defaults an
    agent with no `mode` to `all`; 2.0 changes that default to `primary`. Being
    explicit makes the file correct under both.

    `permission` is the map form. OpenCode 1.18 takes it here; 2.0 replaces it
    with a list of `{action, resource, effect}` entries. This pins the output to
    the 1.x surface and the reader of this docstring knows why.
    """
    front = f"description: {meta['description']}\nmode: subagent\n"
    if meta.get("mode") in READONLY_MODES:
        front += "permission:\n  edit: deny\n"
    return doc(front, slug, body)


def claude(meta: dict[str, str], slug: str, body: str) -> str:
    """Claude Code subagent.

    `name` carries the identity, not the path, so the flat layout is what makes
    the generated name match the prefix used by the other two harnesses. Claude
    Code requires it to be lowercase letters and hyphens, which
    `prompt-<slug>` is, given the slugs are kebab-case.

    `model` is deliberately not emitted. Every prompt declares `model: any`,
    which is a statement that the harness default applies, and an emitted
    `model` would pin a provider-specific id into a file meant to be portable.
    """
    front = f"name: {PREFIX}{slug}\ndescription: {meta['description']}\n"
    if meta.get("mode") in READONLY_MODES:
        front += f"tools: {READONLY_TOOLS}\n"
    return doc(front, slug, body)


def codex(meta: dict[str, str], slug: str, body: str) -> str:
    """Codex skill.

    Codex's custom prompts are deprecated and, being local to `~/.codex`,
    cannot carry a shared library at all. Skills are the replacement: they are
    project-scoped and committable, and they use the `skills/<name>/SKILL.md`
    shape. There is no permission field, so the mode policy is prose here.
    """
    front = f"name: {PREFIX}{slug}\ndescription: {meta['description']}\n"
    return doc(front, slug, body)


def targets() -> list[tuple[Path, str]]:
    """Every file this script should exist, as (path, mode) pairs."""
    out: list[tuple[Path, str]] = []
    for path in sorted(PROMPTS.glob("*.md")):
        if path.stem in INDEX_PAGES:
            continue
        prompt = read_prompt(path)
        meta, slug, body = prompt["meta"], prompt["slug"], prompt["body"]
        out.append((OPENCODE_AGENTS / f"{PREFIX}{slug}.md", opencode(meta, slug, body)))
        out.append((CLAUDE_AGENTS / f"{PREFIX}{slug}.md", claude(meta, slug, body)))
        # Joined as one name, not two segments. `PREFIX / slug` would nest
        # every skill under a directory literally called `prompt-`.
        out.append((CODEX_SKILLS / f"{PREFIX}{slug}" / "SKILL.md", codex(meta, slug, body)))
    return out


def existing(root: Path) -> set[Path]:
    """Every file under an owned directory, as a path relative to it."""
    if not root.is_dir():
        return set()
    return {p.relative_to(root) for p in root.rglob("*") if p.is_file()}


def write(path: Path, text: str) -> None:
    """Write UTF-8 with LF endings and a trailing newline.

    Both are load-bearing rather than cosmetic. validate.sh greps every tracked
    Markdown file for CR and asserts a final newline, and the 135 generated
    files are tracked, so a generator that emitted CRLF would turn the whole
    build red for a difference no reader could see.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the generated trees are current instead of rewriting them",
    )
    args = parser.parse_args()

    wanted = targets()
    if not wanted:
        print("error: no prompts found to generate from", file=sys.stderr)
        return 1

    problems: list[str] = []
    for path, text in wanted:
        if not path.is_file():
            problems.append(f"missing: {path}")
        elif path.read_text(encoding="utf-8") != text:
            problems.append(f"stale:   {path}")

    # An extra file in an owned tree is drift in the other direction, and it is
    # the case a plain diff misses: a hand-added agent, or one left behind by a
    # prompt that has since been deleted. Both would otherwise ship silently.
    for root in OWNED:
        expected = {path.relative_to(root) for path, _ in wanted if path.is_relative_to(root)}
        for extra in sorted(existing(root) - expected):
            problems.append(f"extra:   {root / extra}")

    if args.check:
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        if problems:
            print(
                f"\n{len(problems)} generated agent problem(s); "
                "run python3 scripts/generate_agents.py",
                file=sys.stderr,
            )
            return 1
        print(f"generated agents are current ({len(wanted)} files)")
        return 0

    for path, text in wanted:
        write(path, text)

    removed = 0
    for root in OWNED:
        expected = {path.relative_to(root) for path, _ in wanted if path.is_relative_to(root)}
        for extra in sorted(existing(root) - expected):
            (root / extra).unlink()
            removed += 1
        # Codex nests one directory per skill, so removing the files leaves
        # empty skill directories behind. An empty `prompt-<slug>/` still reads
        # as a skill to a harness that lists directories, so they go too.
        # Reverse order visits children before parents, or a parent that is not
        # yet empty would be skipped.
        directories = sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True)
        for directory in directories:
            if not any(directory.iterdir()):
                directory.rmdir()

    print(
        f"wrote {len(wanted)} files across {len(OWNED)} trees"
        + (f", removed {removed} stale" if removed else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
