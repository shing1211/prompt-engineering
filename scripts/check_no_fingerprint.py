#!/usr/bin/env python3
"""Check that no committed file fingerprints the private codebase.

The verification pass read a private codebase and published what it
found. The rule is that a finding is generalised: the failure mode goes
out, the evidence does not. A venue name, an absolute path or a commit
hash taken from that codebase is not a generalised finding, it is a
pointer back to one, and a pointer in a public file cannot be
unpublished.

That rule was a sentence in a plan, which is a promise that breaks the
first time somebody pastes a real line number into an anti-pattern.

Four rules, over Markdown and Python under prompts/, docs/, scripts/ and
the repository root:

   1. A venue name in prose that the file is not allowed to name. The
      vocabulary is check_vendor_claims.KNOWN_VENDOR_HOSTS, imported from
      the check that already owns it rather than copied, because a second
      list of venue names is a list that drifts from the first, and the
      drift is silent. A file may name a venue when it is one of the
      broker or SDK prompts that check already governs, when it
      carries that script's provenance rule -- verification wording plus a
      citation to that vendor's own documentation -- or when it is an
      inventory of this library's own prompt names, which is what
      LIBRARY_VENUE_FILES below is: the front door, the changelog, and
      the generated index, each of which writes out a file name this
      repository already publishes. A venue name inside one of those file
      names is part of the library's catalogue, not a claim about
      anybody's codebase. The verification register is the fourth kind of
      inventory and gets the same allowance, but only in its table rows:
      a register that could not name the broker prompts would omit five
      rows, and a register that could name a venue in prose would be a
      document making a claim about a codebase, which is what this rule
      exists to catch. All four allowances are load-bearing today, so
      this check widens them and never narrows them. Prose only, because
      prose is where a claim lives; a name in a fenced example, a diagram
      or a frontmatter description is the library describing its own
      published coverage. Markdown only, for the same reason: in a Python
      file a venue name is a slug in this library's own prompt inventory,
      not a claim about a codebase.


  Every name, pattern and prefix this check matches a venue with comes
  from check_vendor_claims.py by import: the vocabulary
  (KNOWN_VENDOR_HOSTS), the wording that discharges a claim
  (VERIFY_PATTERNS, DOCS_PRESENT), the documented-URL test
  (CITED_HOST_PATTERN) and the set of prompts that check already governs
  (CLAIM_PROMPTS). None of them is copied here, so this check and that
  one cannot drift into disagreeing about what a file may name or about
  what counts as citing that vendor. What is restated is only the
  condition that combines them, in provenance_terms(), which is that
  script's own condition and deliberately no weaker. The import is the
  coupling: if check_vendor_claims.py moves, this fails loudly at import
  rather than quietly checking a stale list.

  The one place the two differ is a flag. The host pattern is a pattern
  string there, used as written; here it is compiled with re.I, so an
  upper-cased host still counts as a citation. That widens what counts
  as a citation, and widening that can only ever let a file name a vendor
  it has already cited, so this check stays the narrower of the two.

  2. An absolute path under a home directory, whatever the platform:
     the Linux, macOS and root directories, with or without the user
     segment. A macOS path is exactly the fingerprint this is here to
     catch, so the pattern follows the docstring rather than the
     docstring following the pattern.
  3. The corpus project name, in any case. It is not in this file, and
     cannot be: a public file that carries the name in order to forbid
     it publishes the name, and an encoding of it publishes it just as
     effectively, because the decoder ships alongside it. So it is
     configured outside the repository -- the CORPUS_NAME environment
     variable, or a gitignored .corpus-name file at the root -- and read
     from there. Unconfigured is not a pass: this check exits non-zero
     rather than reporting success for a rule it did not run.
  4. A commit-hash-shaped token in a prompt, at any depth under prompts/:
     seven or more consecutive hex characters containing at least one of
     a-f, minus the identifiers a prompt documents on purpose. Requiring a
     letter is what separates a hash from the epoch timestamps, Go date
     layouts and loop bounds that prompts are full of, every one of which
     is pure digits. The scope is descent rather than "a direct child of
     prompts/", because prompts/ is allowed to grow subdirectories and a
     flat-file test would quietly stop covering whatever moved into one.

What it cannot detect, and why:

  It catches names and paths. It does not catch a file count or a line
  count, and it cannot: a count is not distinguishable from any other
  number a prompt legitimately uses, so a check that banned counts would
  ban the library. Counts are caught in review, not here.

  It cannot catch a corpus venue the library does not already publish,
  because naming that venue in order to ban it would publish it. The
  vocabulary is therefore the set of venues the library already names,
  so a fingerprint written with a venue outside that set passes and is
  caught only in review. The same holds for a corpus-relative package
  path: nothing here tells one from any other Go path, and the directory
  names are not knowable without publishing them.

  Rule 1 reads prose in Markdown, so a name parked in a code fence, in
  frontmatter, in a Python file, or in a historical changelog entry is
  not caught.

  The home-directory rule matches the canonical spellings of the three
  roots and is case-sensitive on purpose, so an upper-cased macOS path is
  not caught. It has to be: prompts/api-design.md documents a lowercase
  /users REST resource, and a case-insensitive pattern fails the build
  over the library's own example. Two files are exempt from that rule,
  this one and the plan that specifies the check; both are exempt for
  reasons about this library's description of its own rule, and both are
  named next to the pattern rather than hidden in a flag.

  It scans the working tree rather than asking git for tracked files,
  since a check that shells out to git cannot tell a worktree from a
  tarball. An untracked file in a scanned directory is therefore scanned
  too, which is the stricter direction.

Exits 0 when clean, 1 on drift or on an unconfigured corpus name.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from check_vendor_claims import (
    CITED_HOST_PATTERN,
    CLAIM_PROMPTS,
    DOCS_PRESENT,
    KNOWN_VENDOR_HOSTS,
    VERIFY_PATTERNS,
)

PROMPTS = Path("prompts")
SCAN_DIRS = (PROMPTS, Path("docs"), Path("scripts"))
SUFFIXES = (".md", ".py")

# Venue terms the library already publishes, derived from the vendor hosts
# check_vendor_claims.py knows how to cite. Derived, not listed: a second
# list of venue names is a list that drifts from the first. The venues the
# library does not publish are deliberately absent and must stay absent,
# because adding one here would publish the name this rule forbids.
VENDOR_TERMS = sorted(
    {term for terms in KNOWN_VENDOR_HOSTS.values() for term in terms},
    key=len,
    reverse=True,
)
VENUE = re.compile(r"\b(?:%s)\b" % "|".join(VENDOR_TERMS), re.I)

# The host of a cited URL, imported from check_vendor_claims.py as a
# pattern string and compiled here case-insensitively, so that "this file
# cites that vendor's documentation" means the same thing in both checks
# even when a file upper-cases the host in the URL.
CITED_HOST = re.compile(CITED_HOST_PATTERN, re.I)

# An absolute path under a home directory. Three roots, because a home
# directory has three names: the Linux one, the macOS one, and root's own.
# The user segment is optional so the directory itself is caught too, and
# the trailing boundary is what keeps /rootfs and /homepage out.
#
# Spelled case-sensitively and deliberately so. macOS filesystems are
# case-insensitive, so /USERS/joe is a real path, but prompts/api-design.md
# uses a lowercase /users REST resource and a case-insensitive pattern
# would fail the build over it. Catching a stray capital is worth less
# than not failing over the library's own examples.
#
# Two files are exempt, and the exemption is by identity rather than by
# crippling the pattern, which is the failure mode this replaced: the old
# pattern required a user segment purely so it would not match the sentence
# describing it, which is a rule that quietly stops catching bare home
# directories the moment someone edits the sentence.
#
#   - This file, which names the pattern in order to document it. Today the
#     pattern as spelled does not match its own source, so that exemption
#     is preventive rather than load-bearing; it is here because the first
#     literal home path written into a comment here should not turn the
#     build red.
#   - The plan that specifies the check, which states the rule. That one is
#     load-bearing and is pinned by scripts/test_checks.py: deleting the
#     exemption fails the suite's positive phase.
#
# Both reasons are about this library describing its own rule, not about
# anything in the corpus.
HOME_PATH = re.compile(
    r"/(?:home|Users|root)(?:/[A-Za-z0-9._-]+)?(?![0-9A-Za-z])"
)
SELF_NAME = Path(__file__).name
RULE_DOCS = {
    "docs/superpowers/plans/2026-09-29-prompt-verification.md": (
        "the plan that specifies this check, which states the rule"
    ),
}

# The corpus project name, configured outside the repository rather than
# stored here. See the docstring: a public file that carries the name in
# order to forbid it publishes it, and so does an encoding of it.
CORPUS_NAME_ENV = "CORPUS_NAME"
CORPUS_NAME_FILE = Path(".corpus-name")


def corpus_name() -> str:
    """The corpus project name, from outside the repository.

    The name is returned, never printed: a run reports that the rule was
    live and where it read the name from, so the console shows the rule
    ran without the report becoming the leak. Unconfigured is a hard
    failure, because a check that reports success for a rule it did not
    run is worse than a build that stops and says why.
    """
    configured = os.environ.get(CORPUS_NAME_ENV, "").strip()
    if configured:
        return configured

    if CORPUS_NAME_FILE.is_file():
        for line in CORPUS_NAME_FILE.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped

    raise SystemExit(
        "error: the corpus project name is not configured, so the rule that\n"
        "forbids it cannot run, and this check will not report success for a\n"
        "rule it did not run.\n"
        f"\nSet ${CORPUS_NAME_ENV} in the environment, or write the name on the\n"
        f"first non-comment line of {CORPUS_NAME_FILE} at the repository root.\n"
        "Both are gitignored, and neither may be committed."
    )


CORPUS_NAME_RE = re.compile(re.escape(corpus_name()), re.I)

# A token that could be a short commit hash, bounded so it is a token and
# not a slice of a longer identifier.
HASH_TOKEN = re.compile(r"(?<![0-9A-Za-z])([0-9a-f]{7,})(?![0-9A-Za-z])", re.I)
HEX_LETTER = re.compile(r"[a-f]", re.I)

# Identifiers a prompt is allowed to contain. The GPG fingerprint in
# performance.md is a real published key, shown so a reader can import the
# key that prompt tells them to trust. It is not a commit.
DOCUMENTED_IDENTIFIERS = {"C5AD17C747E3415A3642D57D77C6C491D6AC1D69"}

# Files allowed to name venues, for a reason that is about this library
# and not about the venue. Keyed by relative path, matching RULE_DOCS and
# may_write_home_path, so a file added to a directory this does not list
# cannot inherit an allowance by sharing a name with one that has it.
#
# The first three are a file-wide allowance. The front door, the changelog
# and the index name a broker because they list the library's own prompts.
# The fourth is not: see REGISTER_ALLOWANCE below.
LIBRARY_VENUE_FILES = {
    "README.md": "the front door lists this library's own Broker SDK prompts",
    "CHANGELOG.md": (
        "historical release notes, the same exclusion check_counts.py makes "
        "and states"
    ),
    "prompts/index.md": (
        "generated from frontmatter by generate_index.py, so the prompt is "
        "the file to check and this one only repeats it"
    ),
}

# The verification register is allowed a venue name in its rows and nowhere
# else. It lists every prompt by file name, so the broker prompts are in it
# whether or not they have been run, and a register that could not list them
# would be a register that quietly omitted five rows. That is an inventory,
# and an inventory stops being one the moment the same document makes a claim
# in prose -- so the allowance is keyed to the row lines rather than to the
# file, and a venue claim written next to the table is reported like any
# other. Scoped rather than widened because the register is the file most
# likely to be hand-edited: a whole-file allowance there is an allowance
# nobody is watching.
REGISTER_ALLOWANCE = {
    "docs/verification.md": (
        "the verification register, which lists every prompt by file name "
        "and cannot do that without naming the broker prompts -- in its rows "
        "only, not in its prose"
    ),
}

# A register row: a table line whose first cell is a backticked prompt slug.
# The generator reads the same shape, so a row that stops matching here is a
# row the generator also cannot read.
REGISTER_ROW = re.compile(r"^\|\s*`[a-z0-9][a-z0-9-]*`\s*\|")

# The broker and SDK prompts check_vendor_claims.py already governs. A
# venue name in one of them is that script's business, not this one's. Keyed
# by relative path for the same reason as above: a name-keyed list here is
# a list a new file with the right name could walk into.
CLAIM_PROMPT_PATHS = {path.as_posix() for path in CLAIM_PROMPTS}


def provenance_terms(text: str) -> set[str]:
    """The venue terms whose own documentation this file cites.

    This is check_vendor_claims.py's condition for accepting a vendor
    claim, restated and not widened: verification wording, a citable
    vendor documentation URL, and that URL belonging to the vendor being
    named. A file that satisfies it here satisfies it there, so nothing
    this check reports is something that check permits.
    """
    if not DOCS_PRESENT.search(text):
        return set()
    if not any(re.search(p, text, re.I) for p in VERIFY_PATTERNS):
        return set()
    covered: set[str] = set()
    for match in CITED_HOST.finditer(text):
        covered.update(KNOWN_VENDOR_HOSTS.get(match.group(1).lower(), ()))
    return covered


def prose_of(text: str) -> list[tuple[int, str]]:
    """The lines that make a claim, as (line number, line) pairs.

    Frontmatter and fenced code are dropped. Frontmatter is the library's
    catalogue metadata, which the frontmatter schema check and
    check_counts.py already cover, and a fenced example is hypothetical
    by construction. Line numbers are preserved so a report points at the
    line a reader has to open.
    """
    lines = text.split("\n")
    start = 0
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                start = i + 1
                break

    kept: list[tuple[int, str]] = []
    fenced = False
    for number, line in enumerate(lines[start:], start + 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            kept.append((number, line))
    return kept


def register_rows(text: str) -> set[int]:
    """The line numbers of the register's own rows.

    An inventory is the rows and nothing else, so this is what separates a
    prompt file name a register is obliged to write out from a venue claim a
    register might choose to make.
    """
    return {
        number
        for number, line in enumerate(text.split("\n"), 1)
        if REGISTER_ROW.match(line)
    }


def may_write_home_path(path: Path) -> bool:
    """Whether this file is allowed to write a home-directory path shape.

    Keyed by file name for the check itself and by relative path for the
    plan, both unique. Matching on name means the exemption cannot be
    widened by adding a file to a directory it does not list.
    """
    return path.name == SELF_NAME or path.as_posix() in RULE_DOCS


def scan_files() -> list[Path]:
    """Every Markdown and Python file in the scanned scope."""
    found: list[Path] = []
    for directory in SCAN_DIRS:
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix in SUFFIXES:
                found.append(path)
    # The repository root, where the front door and the checks live. A
    # directory named after a document is not one, so this cannot pick up
    # a scratch tree.
    for path in sorted(Path(".").iterdir()):
        if path.is_file() and path.suffix in SUFFIXES:
            found.append(path)
    return sorted(set(found))


def check(path: Path) -> list[str]:
    """The fingerprints in one file, one report line each."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    problems: list[str] = []

    # 2 and 3 apply to the whole file, frontmatter and examples included.
    exempt_paths = may_write_home_path(path)
    for number, line in enumerate(lines, 1):
        if not exempt_paths and HOME_PATH.search(line):
            problems.append(f"{path}:{number}: absolute home-directory path")
        if CORPUS_NAME_RE.search(line):
            problems.append(
                f"{path}:{number}: corpus project name, which is "
                f"configured outside this repository and must not be "
                f"written into it"
            )

    # 1 applies to Markdown prose, because prose is where a claim lives.
    # In a Python file a venue name is a slug in the library's own prompt
    # inventory -- the title registry, the category registry, and the
    # check that owns the vocabulary -- and a slug is not a claim about
    # anybody's codebase. Rule 1 also cannot reach a venue the library
    # does not already publish, which is most of what a real fingerprint
    # would use; see the docstring.
    if path.suffix == ".md":
        key = path.as_posix()
        may_name = provenance_terms(text)
        if key in LIBRARY_VENUE_FILES or key in CLAIM_PROMPT_PATHS:
            may_name = set(VENDOR_TERMS)
        # The register's rows are an inventory; its prose is not. Only the
        # rows get the file-wide vocabulary, and every other line in the file
        # is judged by the same rule as any other document.
        rows = register_rows(text) if key in REGISTER_ALLOWANCE else set()
        for number, line in prose_of(text):
            allowed = VENDOR_TERMS if number in rows else may_name
            # URLs are removed first, so a cited documentation link does
            # not satisfy the requirement to name the vendor in the text.
            # That is a defect check_vendor_claims.py already guards, kept
            # here so the two checks cannot disagree.
            for match in VENUE.finditer(re.sub(r"https?://\S+", " ", line)):
                if match.group(0).lower() in allowed:
                    continue
                problems.append(
                    f"{path}:{number}: venue name {match.group(0)!r} in "
                    f"prose, with no vendor documentation cited"
                )

    # 4 applies to prompts, where a commit reference has no other reason
    # to appear, at any depth. Tested as a descendant rather than as a
    # direct child, because prompts/ growing a subdirectory must not
    # silently move its files out of scope.
    if path.is_relative_to(PROMPTS):
        for number, line in enumerate(lines, 1):
            for match in HASH_TOKEN.finditer(line):
                token = match.group(1)
                if token.upper() in DOCUMENTED_IDENTIFIERS:
                    continue
                if not HEX_LETTER.search(token):
                    continue
                problems.append(
                    f"{path}:{number}: commit-hash-shaped token {token}"
                )

    return problems


def main() -> int:
    if not PROMPTS.is_dir():
        print(
            f"error: {PROMPTS} not found; run from the repository root",
            file=sys.stderr,
        )
        return 1

    files = scan_files()
    print(
        f"scanned {len(files)} Markdown and Python files "
        f"for corpus fingerprints"
    )

    problems: list[str] = []
    for path in files:
        problems.extend(check(path))

    for problem in problems:
        print(f"  {problem}")

    if problems:
        print(
            f"\n{len(problems)} fingerprint(s) in a public file",
            file=sys.stderr,
        )
        print(
            "\nFindings from a private codebase are published as the failure\n"
            "mode, with the evidence left out. A venue name, an absolute\n"
            "path or a commit hash is the evidence, not the finding, and a\n"
            "public file cannot be unpublished. Rewrite the line in general\n"
            "terms rather than widening this check.",
            file=sys.stderr,
        )
        return 1

    print("no committed file names the corpus, its paths or its commits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
