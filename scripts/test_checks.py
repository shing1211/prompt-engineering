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
        "venue name",
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
    print(f"proving {len(CASES)} negative cases against {REPO.name}\n")

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

    print()
    if failures:
        for failure in failures:
            print(f"  {failure}")
        print(f"\n{len(failures)} case(s) did not behave as expected")
        return 1

    print(f"all {len(CASES)} negative cases caught as expected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
