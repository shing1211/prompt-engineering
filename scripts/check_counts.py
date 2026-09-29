#!/usr/bin/env python3
"""Check that hand-written counts agree with the generated index.

The generated statistics block in prompts/index.md is authoritative: it is
produced from frontmatter by scripts/generate_index.py. README.md,
docs/strategy.md, prompts/index.md and docs/verification.md also state counts
in prose and in tables, and those are hand-maintained.

They drifted. README claimed 38 prompts and 19 covering multi-broker
trading when the library held 42 and 16, and the "19" was wrong from the
first release. Nothing detected it, because nothing compared the two.

This reads the generated figures and fails on any hand-written count in the
scanned documents that disagrees. It checks:

  - the total prompt count, including the spelled-out and "N of the M"
    forms, and including the count as a denominator ("16 of the 45 prompts")
  - the language-agnostic count
  - the combined financial-domain count, which sums two categories and so
    has no single generated row to compare against
  - the counts that have no row of their own: distinct tags, the total word
    count, the prompts that have not been run, the prompts that are not
    financial, and the per-category and per-mode cells of a hand-maintained
    table, which are matched against the generated category and mode titles
  - that a table of category counts adds up to the non-financial total, and
    that a table of mode counts lists every mode and adds up to the total

Every pattern is derived from the generated statistics, so adding a prompt
moves the expected value with it and a stale figure fails rather than
drifting. No expected number is written in this file.

Three things it deliberately does not do:

  - It does not look inside a generated region. The block between the markers
    in prompts/index.md is the source of these figures, not a claim about
    them, and the generator owns it. Only the hand-written prose around the
    markers is scanned.
  - It does not read a hyphenated count. "a 45-prompt library read as a
    16-prompt one" states the total and a subset in the same shape, and
    nothing in the sentence says which is which, so matching the form would
    report the subset as the total. Hyphenated figures stay unchecked; the
    forms this file does match say which number is the library.
  - It cannot verify that a hand-written sentence is *true* about anything
    the index does not measure. It only prevents a number from diverging
    from the data it claims to summarise.

Exits 0 when clean, 1 on drift.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# The prompt set, and the two files that are not prompts, are read from the
# generator rather than repeated here: a second copy of that rule is a second
# thing to forget when a prompt is added. The import is side-effect free, and
# it is what makes the word count below the count of the same files the
# statistics table was built from.
import generate_index  # noqa: E402

INDEX = Path("prompts/index.md")

BEGIN = "<!-- BEGIN GENERATED TABLES -->"
END = "<!-- END GENERATED TABLES -->"

# Documents whose prose is scanned.
#
# CHANGELOG.md is deliberately excluded: its counts are historical release
# notes describing the state at a given version, so "38 prompts" under the
# 0.1.0 heading is correct in context.
#
# prompts/index.md is the generated one, and is scanned for the prose it
# carries *outside* the markers only -- see skip_generated(). Its summary
# paragraph states the total, the cross-stack split and the financial split,
# and every one of those moved when prompts were added, with nothing checking
# it, because the file was not in the list at all.
#
# docs/verification.md is the register the generated Verified column is read
# from, and it states the same figures in prose. It is included so a claim
# about the register cannot drift from the column the generator derives from
# it.
DOCUMENTS = [
    Path("README.md"),
    Path("docs/strategy.md"),
    Path("prompts/index.md"),
    Path("docs/verification.md"),
]

# Categories that make up the "financial trading" claim. Kept here rather
# than hardcoded as a number, so the check follows the library instead of
# freezing today's arithmetic.
# These must match the category titles in generate_index.CATEGORY_TITLES.
# They are matched by prefix, so a rename in the generator has to be reflected
# here or the combined count silently becomes the single-category count and
# every document claiming the real number fails.
FINANCIAL_CATEGORIES = ("Financial Engineering", "Broker SDKs")

# Statistics rows that are totals rather than categories or modes. A table
# cell labelled with one of these is checked against the same figure the
# prose patterns use, so the block and the sentence cannot disagree.
TOTAL_LABELS = {
    "Total prompts": "total",
    "Language-agnostic": "agnostic",
    "Distinct tags": "tags",
    "Verified": "verified",
}


# ------------------------------------------------------------------ numbers
#
# The documents spell numbers both ways. "16 of the 45 prompts" and
# "Forty-two of the forty-five prompts have not been run" are the same claim,
# and a check that reads only digits covers whichever one the writer happened
# to use. So one vocabulary of words is defined here, used to build the
# patterns and to parse what they capture: a figure can be stated in either
# form and it is the same check.

UNIT_WORDS = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
)
UNITS = {word_: i for i, word_ in enumerate(UNIT_WORDS)}
TENS_WORDS = (
    "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
)
# "fourteen" and "forty" are separate keys on purpose. One dictionary with
# both is the classic way to turn four into forty.
TENS = {word_: (i + 2) * 10 for i, word_ in enumerate(TENS_WORDS)}

DIGITS_ONLY = re.compile(r"\d{1,3}(?:,\d{3})+|\d+")


def word(n: int) -> str:
    """The English spelling of 0-99, which is as large as these documents go."""
    if n < 20:
        return UNIT_WORDS[n]
    tens, rest = divmod(n, 10)
    return TENS_WORDS[tens - 2] + (f"-{UNIT_WORDS[rest]}" if rest else "")


# Longest first, so "eighteen" is not read as "eight" and "twenty-one" is not
# read as "twenty".
NUMBER = r"(?:\d{1,3}(?:,\d{3})+|\d+|" + "|".join(
    sorted((word(n) for n in range(100)), key=len, reverse=True)
) + r")\b"


def count(token: str) -> int | None:
    """Read a captured figure as an integer, in either form. None if neither."""
    token = token.strip()
    if DIGITS_ONLY.fullmatch(token):
        return int(token.replace(",", ""))
    parts = re.split(r"[- ]+", token.lower())
    if not parts or any(p not in UNITS and p not in TENS for p in parts):
        return None
    if len(parts) == 1:
        first = parts[0]
        return UNITS[first] if first in UNITS else TENS[first]
    if len(parts) == 2 and parts[0] in TENS and parts[1] in UNITS and UNITS[parts[1]] <= 9:
        return TENS[parts[0]] + UNITS[parts[1]]
    return None


# A figure stated to a resolution rather than exactly. "~92,000 words" is a
# claim of three significant figures and a hand-maintained exact word count
# is not a claim anybody can keep, so it is compared at the resolution it is
# written in. The drift this catches is the one that matters: the figure
# moving by a thousand.
ROUNDED = {"words": 1000}


# ------------------------------------------------------------- the figures

def generated_stats(index: Path = INDEX) -> dict[str, int]:
    """Read the statistics block from the generated index.

    The index defaults to the one in the repository root, and takes an
    argument so a caller that is looking at a copy of the repository -- the
    negative-case suite runs checks in a temporary directory -- can say which
    file it means instead of depending on the working directory.
    """
    text = index.read_text(encoding="utf-8")
    block = re.search(
        r"## Statistics\s*\n(.*?)(?:<!-- END GENERATED|\Z)", text, re.S
    )
    if not block:
        raise SystemExit(f"error: no Statistics block in {index}")

    stats: dict[str, int] = {}
    for label, value in re.findall(r"\|\s*\*\*([^*]+)\*\*\s*\|\s*(\d+)\s*\|", block.group(1)):
        stats[label.strip()] = int(value)
    return stats


def word_count(prompts: Path = generate_index.PROMPTS) -> int:
    """Every word of every prompt.

    Over the generator's file list -- the prompts directory minus the two
    files that are not prompts -- rather than a second list written out
    here. Not a statistic the index carries, because a generated table nobody
    reads should not grow a row, but a figure the README states and the
    index is the only place that can supply the other side of it.

    main() refuses to read any figure from a statistics block that disagrees
    with the file list about how many prompts there are, so the words cannot
    be counted over a different set of files than the total they are checked
    against.
    """
    return sum(
        len(path.read_text(encoding="utf-8").split())
        for path in sorted(prompts.glob("*.md"))
        if path.stem not in generate_index.INDEX_PAGES
    )


def expected(
    stats: dict[str, int], prompts: Path = generate_index.PROMPTS
) -> dict[str, int]:
    """Map a key to the value it must hold, for every figure this file checks.

    Keys are "total", "agnostic", "financial", "tags", "verified",
    "unverified", "nonfinancial", "words", "category:<title>" and
    "mode:<name>". None of them is written here: each is read from the
    generated block or derived from it arithmetically, so the set follows the
    library rather than the day it was written.
    """
    total = stats.get("Total prompts")
    agnostic = stats.get("Language-agnostic")
    verified = stats.get("Verified")
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
    if total is not None and verified is not None:
        checks["verified"] = verified
        checks["unverified"] = total - verified
    if total is not None and financial:
        checks["nonfinancial"] = total - financial
    if "Distinct tags" in stats:
        checks["tags"] = stats["Distinct tags"]

    for label, value in stats.items():
        if label.startswith("Mode: "):
            checks[f"mode:{label[len('Mode: '):]}"] = value
        elif label in TOTAL_LABELS or any(
            label.startswith(c) for c in FINANCIAL_CATEGORIES
        ):
            # A total has its own key, and the two financial categories are
            # already summed into "financial": calling either of them a
            # category would let a table row be checked against one of them
            # rather than the figure the document means.
            continue
        else:
            checks[f"category:{label}"] = value

    if total is not None:
        checks["words"] = word_count(prompts)
    return checks


# ------------------------------------------------------- prose count shapes

# (label, pattern, ((group, key), ...), guard). A pattern must capture the
# whole count phrase rather than a fragment, and every number it captures
# must be named against the figure it claims to be -- including the
# denominator of a scoped count, which is the library total and is checked as
# such rather than inferred.
PATTERNS: list[tuple[str, re.Pattern[str], tuple[tuple[str, str], ...], str | None]] = [
    (
        "total prompt count",
        re.compile(rf"\b(?P<n>{NUMBER})\s+prompts\b"),
        (("n", "total"),),
        "not-a-scoped-number",
    ),
    (
        "library total, as the denominator of a scoped count",
        re.compile(
            rf"\b(?:of|out of)\s+the\s+(?P<n>{NUMBER})\s+(?:prompts|rows)\b", re.I
        ),
        (("n", "total"),),
        None,
    ),
    (
        "index listing count",
        re.compile(rf"\blists all\s+(?P<n>{NUMBER})\b", re.I),
        (("n", "total"),),
        None,
    ),
    (
        "language-agnostic count",
        re.compile(
            rf"\b(?P<n>{NUMBER})\s+of\s+the\s+(?P<all>{NUMBER})\s+"
            r"(?:prompts\s+)?(?:are\s+)?language-agnostic",
            re.I,
        ),
        (("n", "agnostic"), ("all", "total")),
        None,
    ),
    (
        "multi-broker trading count",
        re.compile(
            rf"\b(?P<n>{NUMBER})\s+of\s+the\s+(?P<all>{NUMBER})\s+prompts\s+"
            r"(?:here\s+)?cover\s+multi-broker\s+trading",
            re.I,
        ),
        (("n", "financial"), ("all", "total")),
        None,
    ),
    (
        "multi-broker trading count, as a split of the total",
        re.compile(rf"\b(?P<n>{NUMBER})\s+covering\s+multi-broker\s+trading", re.I),
        (("n", "financial"),),
        None,
    ),
    (
        "non-financial prompt count",
        re.compile(rf"\b(?P<n>{NUMBER})\s+cross-stack", re.I),
        (("n", "nonfinancial"),),
        None,
    ),
    (
        "unverified prompt count",
        re.compile(
            rf"\b(?P<n>{NUMBER})\s+of\s+the\s+(?P<all>{NUMBER})\s+"
            r"(?:prompts|rows)\s+(?:have not been run|are not verified|"
            r"are unverified|remain unverified|say no)",
            re.I,
        ),
        (("n", "unverified"), ("all", "total")),
        None,
    ),
    (
        "distinct tag count",
        re.compile(rf"\b(?P<n>{NUMBER})\s+tags\b", re.I),
        (("n", "tags"),),
        None,
    ),
    (
        "total word count",
        re.compile(rf"\b(?P<n>{NUMBER})\s+words\b", re.I),
        (("n", "words"),),
        None,
    ),
]

DENOMINATOR = PATTERNS[1][1]

# The subset patterns, so their numerators can be recognised as subsets. A
# document that says "16 prompts cover multi-broker trading" and then
# "16 of the 45 prompts cover multi-broker trading" has said what 16 is, and
# the bare total pattern must not read the first as a claim about the library.
# Named by label rather than by position: a pattern added to the end of the
# list must not change which figures are scoped.
SUBSET_LABELS = (
    "language-agnostic count",
    "multi-broker trading count",
    "multi-broker trading count, as a split of the total",
    "non-financial prompt count",
    "unverified prompt count",
)
SCOPED = [p for label, p, _g, _guard in PATTERNS if label in SUBSET_LABELS]


def scoped_numbers(region: str) -> set[int]:
    """The figures a region has already said are subsets, not the library.

    Two shapes, and both are scoped counts rather than claims about the
    library. "16 of the 45 prompts" is one: 16 is a subset, 45 is the
    library, and the denominator is checked as the total by the pattern above
    rather than inferred. "16 prompts cover multi-broker trading" is the
    other, where the number in front of "prompts" is the subset and its
    denominator is in the next clause or the next sentence.

    The bare total pattern yields in both. Without that, one number gets read
    by two patterns that disagree about what it means, and the subset is
    reported as a stale total -- the false positive this check is most prone
    to, and the one that has bitten it before. The set is by value rather
    than by position because a writer states a figure more than once in a
    paragraph, and only the first mention carries the shape that says which
    number it is.

    Nothing is lost by yielding. Every figure in the set is checked by the
    scoped pattern that owns it, against its own expected value, and a
    paragraph has one total: a figure a paragraph calls a subset is not the
    library anywhere else in that paragraph.
    """
    values: set[int] = set()
    for pattern in (DENOMINATOR, *SCOPED):
        for match in pattern.finditer(region):
            value = count(match.group("n"))
            if value is not None:
                values.add(value)
    return values


# ------------------------------------------------------- table count shapes

def table_labels(stats: dict[str, int]) -> dict[str, str]:
    """A table cell's first column, normalised, to the key its number is.

    Matched against the generated titles, so a cell can only be checked when
    the library itself says what that row counts. A short label is accepted
    when the generated title ends with it -- "Protocols" is the generated
    "API Protocols" written short -- and dropped when two titles claim it,
    which is what keeps "Development" from matching both "Application
    Development" and "SDK Development". A row the generated titles do not
    describe is not checked: a table is free to group categories under a
    heading of its own, and a check that guessed at that heading would be
    checking the guess.
    """
    votes: dict[str, set[str]] = {}

    def vote(label: str, key: str) -> None:
        votes.setdefault(label, set()).add(key)

    for label, key in TOTAL_LABELS.items():
        if label in stats:
            vote(normalise(label), key)
    for label, value in stats.items():
        if label.startswith("Mode: "):
            vote(normalise(label[len("Mode: "):]), f"mode:{label[len('Mode: '):]}")
        elif label not in TOTAL_LABELS:
            vote(normalise(label), f"category:{label}")
            words = normalise(label).split()
            for i in range(1, len(words)):
                vote(" ".join(words[i:]), f"category:{label}")

    return {label: next(iter(keys)) for label, keys in votes.items() if len(keys) == 1}


def normalise(cell: str) -> str:
    """A table cell reduced to something a generated title can be compared to."""
    return re.sub(r"\s+", " ", cell.replace("*", "").replace("`", "")).strip().lower()


CELL = re.compile(r"^\s*\|(?P<body>.*)\|\s*$")


def cells(line: str) -> list[str] | None:
    match = CELL.match(line)
    if not match:
        return None
    # A pipe inside a cell is escaped, and unescaping it here keeps the
    # description column from splitting a row into columns that are not there.
    return [c.strip() for c in re.split(r"(?<!\\)\|", match.group("body"))]


# ------------------------------------------------------------ the documents

def skip_generated(lines: list[str]) -> set[int]:
    """Line numbers of a generated region, which is not scanned.

    The block between the markers is what the figures are read from. Reading
    it as though it were a claim about them would be checking the source
    against itself, and editing it is the generator's job and not this
    check's.
    """
    skip: set[int] = set()
    inside = False
    for lineno, line in enumerate(lines, 1):
        if line.strip() == BEGIN:
            inside = True
        if inside:
            skip.add(lineno)
        if line.strip() == END:
            inside = False
    return skip


def prose_regions(lines: list[str], skip: set[int]) -> list[tuple[int, str, list[int]]]:
    """The hand-written prose of a document, with the line wrapping removed.

    Prose is wrapped at 80 columns, so a count phrase is routinely split
    across two lines -- "21 of the / 45 are language-agnostic" -- and a
    line-at-a-time scan cannot see a phrase it has already half read. The
    regions are paragraphs, so a phrase that reads as a sentence in the
    rendered document is a phrase here, and the third element maps each
    character back to the line it came from so a report still points at one.

    Table rows are excluded and handled separately: joining two rows of a
    table produces a sentence that was never written.
    """
    regions: list[tuple[int, str, list[int]]] = []
    text: list[str] = []
    owner: list[int] = []
    start = 0

    def flush() -> None:
        if text:
            # Copied, not aliased: this is the buffer the next paragraph
            # reuses, and a region that pointed at it would be emptied the
            # moment the next paragraph started.
            regions.append((start, "".join(text), list(owner)))
            text.clear()
            owner.clear()

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        table = stripped.startswith("|")
        if lineno in skip or table or not stripped:
            flush()
            continue
        if not text:
            start = lineno
        piece = stripped if not text else " " + stripped
        text.append(piece)
        owner.extend([lineno] * len(piece))
    flush()
    return regions


def table_blocks(lines: list[str], skip: set[int]) -> list[list[tuple[int, str]]]:
    """Consecutive table rows, grouped per table."""
    blocks: list[list[tuple[int, str]]] = []
    block: list[tuple[int, str]] = []
    for lineno, line in enumerate(lines, 1):
        if line.lstrip().startswith("|") and lineno not in skip:
            block.append((lineno, line))
        elif block:
            blocks.append(block)
            block = []
    if block:
        blocks.append(block)
    return blocks


# ---------------------------------------------------------------- reporting

def group_label(label: str, key: str) -> str:
    """Name the figure a captured group is, which is not always the pattern's.

    A scoped count captures two: the subset, which the pattern is named
    after, and the library, which the same sentence states as its
    denominator. Reporting a stale total under the name of the subset is how
    a reader ends up looking for sixteen prompts when the sentence is about
    forty-five.
    """
    if key == "total" and label in SUBSET_LABELS:
        return "library total, as the denominator of a scoped count"
    return label


def report(
    problems: list[str], doc: Path, lineno: int, label: str, stated: int, want: int
) -> None:
    problem = f"{doc}:{lineno}: {label} says {stated}, generated index says {want}"
    if problem not in problems:
        problems.append(problem)


def agrees(stated: int, want: int, key: str) -> bool:
    step = ROUNDED.get(key)
    if step is None:
        return stated == want
    return stated // step == want // step


def main() -> int:
    if not INDEX.is_file():
        raise SystemExit(f"error: {INDEX} not found; run from the repository root")

    stats = generated_stats()
    want = expected(stats)
    if not want:
        raise SystemExit(f"error: could not read expected values from {INDEX}")

    if "total" in want and len(generate_index.load()) != want["total"]:
        raise SystemExit(
            f"error: the generated index counts {want['total']} prompts and\n"
            f"{INDEX} lists {len(generate_index.load())}. Run\n"
            "python3 scripts/generate_index.py before reading counts from it."
        )

    labels = table_labels(stats)
    modes = {k.split(":", 1)[1] for k in want if k.startswith("mode:")}

    print(
        f"generated: {want.get('total')} prompts, "
        f"{want.get('agnostic')} language-agnostic, "
        f"{want.get('financial')} in the financial domain, "
        f"{want.get('tags')} tags"
    )

    problems: list[str] = []
    scanned = 0

    for doc in DOCUMENTS:
        if not doc.is_file():
            print(f"  note: {doc} not found, skipping")
            continue
        scanned += 1
        lines = doc.read_text(encoding="utf-8").split("\n")
        skip = skip_generated(lines)

        for _start, region, owner in prose_regions(lines, skip):
            scoped = scoped_numbers(region)
            for label, pattern, groups, guard in PATTERNS:
                for match in pattern.finditer(region):
                    stated = count(match.group("n") if "n" in match.groupdict() else "")
                    if guard == "not-a-scoped-number" and stated in scoped:
                        continue
                    for group, key in groups:
                        want_value = want.get(key)
                        value = count(match.group(group))
                        if want_value is None or value is None:
                            continue
                        if not agrees(value, want_value, key):
                            report(
                                problems,
                                doc,
                                owner[match.start(group)],
                                group_label(label, key),
                                value,
                                want_value,
                            )

        for block in table_blocks(lines, skip):
            check_table(doc, block, labels, modes, want, problems)

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


def check_table(
    doc: Path,
    block: list[tuple[int, str]],
    labels: dict[str, str],
    modes: set[str],
    want: dict[str, int],
    problems: list[str],
) -> None:
    """Check the count cells of one hand-maintained table.

    Three things, and each catches a failure the others cannot. A cell whose
    first column is a generated title is checked against that figure. A table
    of category rows must add up to the non-financial total, which is what
    catches the rows no generated title describes -- a table is free to
    group several categories under one heading of its own, and grouping is
    exactly where a count goes stale unnoticed. A table of mode rows must
    list every mode there is and add up to the total, which is what catches a
    row that was never written.
    """
    rows: list[tuple[int, str, int | None]] = []
    for lineno, line in block:
        parts = cells(line)
        if not parts or len(parts) < 2:
            continue
        value = DIGITS_ONLY.fullmatch(parts[1])
        rows.append(
            (lineno, normalise(parts[0]), int(value.group()) if value else None)
        )

    for lineno, label, value in rows:
        key = labels.get(label)
        if key is None or value is None or key not in want:
            continue
        if not agrees(value, want[key], key):
            report(problems, doc, lineno, f"{label} count", value, want[key])

    counted = [r for r in rows if r[2] is not None]

    categories = [r for r in counted if labels.get(r[1], "").startswith("category:")]
    if categories and "nonfinancial" in want:
        total = sum(r[2] or 0 for r in counted)
        if total != want["nonfinancial"]:
            report(
                problems,
                doc,
                block[0][0],
                "category table total",
                total,
                want["nonfinancial"],
            )

    by_mode = {
        labels[row[1]].split(":", 1)[1]: row
        for row in counted
        if labels.get(row[1], "").startswith("mode:")
    }
    if by_mode:
        missing = sorted(modes - set(by_mode))
        if missing:
            problems.append(
                f"{doc}:{block[0][0]}: mode table has no row for "
                f"{', '.join(missing)}; generated index says "
                f"{', '.join(sorted(modes))}"
            )
        total = sum(r[2] or 0 for r in by_mode.values())
        if total != want["total"]:
            report(problems, doc, block[0][0], "mode table total", total, want["total"])


if __name__ == "__main__":
    raise SystemExit(main())
