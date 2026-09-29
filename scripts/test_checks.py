#!/usr/bin/env python3
"""Prove each check fails on bad input, not just that it passes on good input.

Every check in this repository was originally validated by mutating a prompt
and observing the exit code. That found five defects in the checks
themselves, including one that passed when it should have failed. It is the
only reason the checks are trustworthy, and it does not survive someone
refactoring a regex.

This makes those negative tests durable. Each case copies the repository to a
temporary directory, breaks one thing, runs the check, and asserts it failed
for the right reason. Nothing outside the temp directory is touched.

    python3 scripts/test_checks.py

Exits 0 when every case behaves as expected, 1 otherwise. Prints each case
and its outcome.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run(check: str, cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, f"scripts/{check}"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout + proc.stderr


# (name, check script, mutation, substring expected in the failure output)
CASES: list[tuple[str, str, object, str]] = [
    (
        "check_prompt_sections: missing guardrails",
        "check_prompt_sections.py",
        lambda r: _strip_section(r / "prompts/security.md", "## Guardrails"),
        "no guardrails section",
    ),
    (
        "check_prompt_sections: missing anti-patterns",
        "check_prompt_sections.py",
        lambda r: _strip_section(r / "prompts/api-design.md", "## Layer 6: Anti-Patterns"),
        "no anti-patterns section",
    ),
    (
        "check_nav: prompt missing from nav",
        "check_nav.py",
        lambda r: _remove_nav_entry(r / "mkdocs.yml", "platform-engineering.md"),
        "not in nav",
    ),
    (
        "check_counts: wrong total in README",
        "check_counts.py",
        lambda r: _replace(r / "README.md", r"\*\*42 prompts\.", "**43 prompts."),
        "total prompt count says 43",
    ),
    (
        "check_counts: wrong financial count",
        "check_counts.py",
        lambda r: _replace(
            r / "README.md",
            r"16 of the 42 prompts cover multi-broker",
            "19 of the 42 prompts cover multi-broker",
        ),
        "multi-broker trading count says 19",
    ),
    (
        "check_vendor_claims: unverified vendor internals",
        "check_vendor_claims.py",
        lambda r: _inject_claim(r / "prompts/sdk-build.md"),
        "sdk-build.md",
    ),
    (
        "check_vendor_claims: risk threshold stated as a rule",
        "check_vendor_claims.py",
        lambda r: _unframe_thresholds(r / "prompts/trading-risk.md"),
        "trading-risk.md",
    ),
    (
        "check_no_fingerprint: venue name seeded into an anti-pattern",
        "check_no_fingerprint.py",
        lambda r: _replace(
            r / "prompts/backend-services.md",
            r"(?m)^## Layer 4: Anti-Patterns \(Never Do These\)$",
            "## Layer 4: Anti-Patterns (Never Do These)\n\n"
            "- ❌ **Per-venue divergence.** The Futu adapter and the Webull\n"
            "  adapter disagreed about deadline handling; only one of the two\n"
            "  ever derived a deadline from the caller's context.",
        ),
        # Only rule 1 emits this. The failure guidance printed on stderr for
        # any failure also contains "venue name", so asserting that would
        # prove only that the run exited non-zero.
        "in prose, with no vendor documentation cited",
    ),
    (
        "check_no_fingerprint: venue name in the register's prose",
        "check_no_fingerprint.py",
        lambda r: _append(
            r / "docs/verification.md",
            "\nThe Futu adapter disagreed with the Webull one, and that was "
            "the finding.",
        ),
        "in prose, with no vendor documentation cited",
    ),
    (
        "check_no_fingerprint: absolute home-directory path in a prompt",
        "check_no_fingerprint.py",
        lambda r: _seed_home_path(r / "prompts/api-design.md"),
        "absolute home-directory path",
    ),
    (
        "check_no_fingerprint: corpus project name in a prompt",
        "check_no_fingerprint.py",
        lambda r: _seed_corpus_name(r / "prompts/api-design.md"),
        "corpus project name",
    ),
    (
        "check_no_fingerprint: commit-hash-shaped token in a prompt",
        "check_no_fingerprint.py",
        lambda r: _seed_hash_token(r / "prompts/api-design.md"),
        "commit-hash-shaped token",
    ),
    (
        "check_no_fingerprint: commit hash in a nested prompt directory",
        "check_no_fingerprint.py",
        lambda r: _seed_nested_prompt(r),
        "commit-hash-shaped token",
    ),
]


# Input that looks like a fingerprint and must not be reported. A guard
# exists to keep a rule off legitimate content, and a guard removed to quiet
# a false positive is invisible from the negative cases alone: the rule it
# belonged to still fires on its own bad input, so the suite stays green
# while it has stopped firing on the good input that guard protected. These
# are the cases that catch that.
MUST_STAY_CLEAN: list[tuple[str, str, object]] = [
    (
        "check_no_fingerprint: digit-only tokens are not commit hashes",
        "check_no_fingerprint.py",
        lambda r: _seed_digits(r / "prompts/api-design.md"),
    ),
    (
        "check_no_fingerprint: a word starting with a home root is not a path",
        "check_no_fingerprint.py",
        lambda r: _seed_home_lookalike(r / "prompts/api-design.md"),
    ),
]


# Checks that must pass on the repository as committed. Without these, a
# check that had been broken into always-exit-1 would look like it was
# working, since every negative case would still "catch" its mutation.
MUST_PASS: list[tuple[str, str]] = [
    ("check_nav.py", "nav"),
    ("check_vendor_claims.py", "vendor claims"),
    ("check_prompt_sections.py", "sections"),
    ("check_counts.py", "counts"),
    ("check_no_fingerprint.py", "corpus fingerprint"),
    ("generate_index.py", "generated index"),
]


def _strip_section(path: Path, heading: str) -> None:
    """Remove a section from a prompt, from its heading to the next heading."""
    text = path.read_text(encoding="utf-8")
    start = text.find(heading)
    if start == -1:
        raise AssertionError(f"{path.name}: heading not found: {heading}")
    rest = text[start:]
    m = re.search(r"^#{1,4}\s+\S", rest[len(heading):], re.M)
    end = start + len(heading) + m.start() if m else len(text)
    path.write_text(text[:start].rstrip("\n") + "\n" + text[end:], encoding="utf-8")


def _remove_nav_entry(path: Path, filename: str) -> None:
    lines = [
        ln for ln in path.read_text(encoding="utf-8").split("\n") if filename not in ln
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _replace(path: Path, pattern: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    new = re.sub(pattern, replacement, text, count=1)
    if new == text:
        raise AssertionError(f"{path.name}: pattern did not match: {pattern}")
    path.write_text(new, encoding="utf-8")


def _seed_home_path(path: Path) -> None:
    """Seed an absolute path under a home directory.

    Assembled with Path() rather than written out, so this file does not
    contain the shape it is proving the check rejects -- it is scanned by
    the same rule, and the only exemption is the check's own source.
    """
    _append(
        path,
        f"- ❌ **Hard-coded home.** Run it from {Path('/', 'Users', 'dev', 'acme')}.",
    )


def _seed_corpus_name(path: Path) -> None:
    """Seed the corpus project name, upper-cased to pin the case folding.

    Read from the same configuration the check reads it from, so this
    case and the check cannot end up testing different names, and so the
    name is never written into a committed file.
    """
    name = os.environ.get("CORPUS_NAME", "").strip()
    if not name:
        config = path.parent.parent / ".corpus-name"
        name = config.read_text(encoding="utf-8").strip() if config.is_file() else ""
    if not name:
        raise AssertionError("the corpus project name is not configured")
    _append(path, f"- ❌ **Internal codename.** The service was called {name.upper()}.")


def _seed_hash_token(path: Path) -> None:
    """Seed a token with the shape of a short commit hash, containing a letter."""
    _append(path, "- ❌ **Pinned to a commit.** Revert to deadbee before merging.")


def _seed_nested_prompt(repo: Path) -> None:
    """Seed a prompt in a subdirectory of prompts/.

    Both the scan and the commit-hash rule are scoped by descent, not by
    "is a direct child of prompts/". A future prompts/ that grows
    subdirectories has to keep both, and this is what notices when it
    does not.
    """
    nested = repo / "prompts" / "nested"
    nested.mkdir(exist_ok=True)
    (nested / "deep.md").write_text(
        "---\ntitle: Deep\n---\n\n# Deep\n\n- ❌ **Pinned.** Revert to badf00d.\n",
        encoding="utf-8",
    )


def _seed_digits(path: Path) -> None:
    """Seed long digit-only tokens, which prompts are legitimately full of.

    Epochs, Go date layouts, account placeholders and loop bounds are all
    seven or more characters of pure digits. The rule requires a letter for
    exactly this reason, and dropping that requirement is the change that
    would turn this check red across the library.
    """
    _append(
        path,
        "- ✅ Epoch 1705315800000, layout 20060102150405, bound 1000000, "
        "account 123456789012 are all fine.",
    )


def _seed_home_lookalike(path: Path) -> None:
    """Seed words that begin with a home directory's name but are not paths."""
    _append(
        path, "- ✅ The /homepage route and the /rootfs/entrypoint table are not paths."
    )


def _append(path: Path, line: str) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(text.rstrip("\n") + "\n" + line + "\n", encoding="utf-8")


def _inject_claim(path: Path) -> None:
    """Add a hard-coded vendor claim and strip the verify wording around it."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"verif\w+", "handle", text, flags=re.I)
    text = text.replace(
        "## Objective",
        "## Objective\n\n"
        "Sign every request with HMAC-SHA256 and emit X-Broker-Id, "
        "X-Timestamp, and X-Signature headers.\n",
        1,
    )
    path.write_text(text, encoding="utf-8")


def _unframe_thresholds(path: Path) -> None:
    """Remove the "this is an example" framing from a config threshold block."""
    text = path.read_text(encoding="utf-8")
    start = text.find("## Layer 8: Risk Limits Configuration")
    if start == -1:
        raise AssertionError("trading-risk.md: Layer 8 not found")
    end = text.find("\n---", start)
    block = text[start:end]
    block = re.sub(r"Example: ", "", block)
    block = re.sub(r"Example limits only\. ", "", block)
    block = re.sub(r"Example only\. ", "", block)
    block = re.sub(r"Example ", "", block)
    block = block.replace("Illustrative values only. ", "")
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def main() -> int:
    print(
        f"proving {len(CASES)} negative cases and {len(MUST_STAY_CLEAN)} "
        f"guards against {REPO.name}\n"
    )

    failures: list[str] = []

    print("  -- positive: checks pass on the repository as committed --")
    with tempfile.TemporaryDirectory() as tmp:
        clean = Path(tmp) / "repo"
        shutil.copytree(
            REPO,
            clean,
            ignore=shutil.ignore_patterns(".git", "site", "__pycache__"),
        )
        for check, label in MUST_PASS:
            args = (
                [sys.executable, "scripts/generate_index.py", "--check"]
                if check == "generate_index.py"
                else [sys.executable, f"scripts/{check}"]
            )
            proc = subprocess.run(
                args, cwd=clean, capture_output=True, text=True, check=False
            )
            if proc.returncode == 0:
                print(f"  passes    {label}")
            else:
                failures.append(
                    f"{label}: exits non-zero on the unmodified repository"
                )
                print(f"  FAILS-CLEAN  {label}")

    print("\n  -- negative: checks fail on deliberately broken input --")
    for name, check, mutate, expect in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "repo"
            shutil.copytree(
                REPO,
                work,
                ignore=shutil.ignore_patterns(".git", "site", "__pycache__"),
            )
            try:
                mutate(work)
            except AssertionError as exc:
                failures.append(f"{name}: could not set up - {exc}")
                print(f"  SETUP-FAIL  {name}")
                continue

            code, output = run(check, work)

        if code == 0:
            failures.append(f"{name}: check exited 0 on broken input")
            print(f"  NOT-CAUGHT  {name}")
        elif expect not in output:
            failures.append(
                f"{name}: failed, but output did not mention {expect!r}"
            )
            print(f"  WRONG-REASON  {name}")
        else:
            print(f"  caught    {name}")

    print("\n  -- guards: lookalikes a check must leave alone --")
    for name, check, mutate in MUST_STAY_CLEAN:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "repo"
            shutil.copytree(
                REPO,
                work,
                ignore=shutil.ignore_patterns(".git", "site", "__pycache__"),
            )
            try:
                mutate(work)
            except AssertionError as exc:
                failures.append(f"{name}: could not set up - {exc}")
                print(f"  SETUP-FAIL  {name}")
                continue

            code, output = run(check, work)

        if code == 0:
            print(f"  ignored   {name}")
        else:
            failures.append(f"{name}: reported input that is not a fingerprint")
            print(f"  FALSE-POSITIVE  {name}")
            for line in output.splitlines():
                if line.startswith("  "):
                    print(f"      {line.strip()}")

    print()
    if failures:
        for failure in failures:
            print(f"  {failure}")
        print(f"\n{len(failures)} case(s) did not behave as expected")
        return 1

    print(f"all {len(CASES)} negative cases caught as expected")
    print(f"all {len(MUST_STAY_CLEAN)} guards held as expected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
