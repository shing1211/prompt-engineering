#!/usr/bin/env python3
"""Check that vendor-specific claims in the prompts are not stated as fact.

The library's rule, in SECURITY.md, is that a prompt should "ground claims
in something verifiable... if not sure, say to verify rather than instruct
the agent to guess." That rule was being violated by the per-broker adapter
table, which asserted auth header names and endpoints with no provenance
note, three of which were wrong.

This check is deliberately narrow. It cannot verify that a documented URL is
still correct without network access, and it cannot check that a stated
algorithm matches the vendor. What it can do is catch the failure mode
itself: a prompt that hard-codes broker auth internals without anywhere
telling the reader to confirm them first.

Rules:

  1. If a prompt asserts a broker auth header, endpoint, or digest
     algorithm, it must carry an explicit verification instruction.
  2. An unverified vendor claims nothing at all: no public portal, and the
     prompt must say so.
  3. If a prompt states a numeric risk threshold as a rule, it must say the
     value is configurable or an example rather than universal. Broker
     maintenance margin and account-level risk limits are mandates, not
     constants.

Exits 0 when clean, 1 on drift.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROMPTS = Path("prompts")

# Claims that must never be presented as settled fact without a
# verification instruction somewhere in the same file.
CLAIM_PATTERNS = [
    r"\bX-[A-Z][A-Za-z]*-Id\b",              # X-Broker-Id, X-Vbroker-Id, ...
    r"\bHMAC-SHA256\b",
    r"\bHMAC-SHA1\b",
    r"\bopenapi\.[a-z0-9.-]+",
    r"\bwss://[a-z0-9.-]+",
    r"\bTiger-Open-API-Key\b",
    r"\blocalhost:\d+",                     # local gateways: IBKR, Futu OpenD
    r"\b127\.0\.0\.1:\d+",
    r"\bBearer JWT\b",
    r"/v\d+/portal/",
    r"\bPushOrderBookData\b",
    r"\bx-app-key\b",
    r"\bx-signature\b",
]

# Wording that discharges the requirement.
VERIFY_PATTERNS = [
    r"\bverif(?:y|ied|ication)\b",
    r"\bconfirm(?:ed|ation)?\b",
    r"\buntil verified\b",
    r"\bauthoritative\b",
    r"\bdo not assume\b",
    r"\btreat .{0,40}as (?:a )?hypothes[ie]s\b",
    r"\bnot confirmed\b",
    r"\bleast-documented\b",
    r"\bunconfirmed\b",
    r"\bread .{0,30}from the vendor\b",
]

# Vendor domains we can cite as a source, meaning a verification instruction
# is only useful if it points somewhere. Files matching this are exempt from
# the "must cite a doc" expectation but still need the verify wording.
DOCS_PRESENT = re.compile(r"https://(?:open\.longbridge|docs-en\.itigerup|developer\.webull|www\.futunn|www\.interactivebrokers)[a-z0-9./-]*")

BROKER_PROMPTS = sorted(PROMPTS.glob("broker-*.md"))

# A threshold phrased as a rule. The problem is not the number itself, it is
# asserting one as universal when the value is a per-broker or per-account
# mandate.
RULE_THRESHOLD = re.compile(
    r"(should (?:not )?(?:exceed|be below|stay below)|"
    r"must (?:not )?exceed|never exceed|"
    r"\d+\s*%\s*utili[sz]ed|"
    r"maintenance margin|"
    # A threshold declared in config, where the phrasing is a key and a
    # number rather than a sentence.
    r"\b(?:breach|warning|hard|stop|kill)_\w*_?(?:threshold|limit)\w*\s*:\s*[0-9])",
    re.I,
)

THRESHOLD_DISCHARGE = re.compile(
    r"\bconfigurable\b|"
    r"\bexample\b|\billustrative\b|"
    r"\bmandate\b|not a (?:constant|recommendation)\b|"
    r"\bvaries by\b|\bdiffer(?:s)? by\b|"
    r"\bload (?:them|it) from\b|"
    r"\bnot universal\b|"
    r"\brisk appetite\b",
    re.I,
)

# How many lines either side of a rule-threshold a discharge note can sit and
# still count. A note 300 lines away from the claim it qualifies is not
# qualifying it. A blockquote note sits directly above the block it governs,
# so 6 is enough for that shape while keeping unrelated later sections from
# accidentally satisfying an earlier claim.
DISCHARGE_WINDOW = 6


def check_thresholds() -> list[str]:
    problems: list[str] = []
    for path in sorted(PROMPTS.glob("*.md")):
        if path.stem in ("index", "tags"):
            continue
        body = path.read_text(encoding="utf-8").split("\n---", 1)[-1]
        lines = body.split("\n")

        flagged: list[int] = []
        for i, line in enumerate(lines):
            if not RULE_THRESHOLD.search(line):
                continue
            # A line that is itself the discharge note does not need one.
            if THRESHOLD_DISCHARGE.search(line):
                continue
            lo = max(0, i - DISCHARGE_WINDOW)
            hi = min(len(lines), i + DISCHARGE_WINDOW + 1)
            if not any(THRESHOLD_DISCHARGE.search(x) for x in lines[lo:hi]):
                flagged.append(i)

        if flagged:
            first = lines[flagged[0]].strip()[:80]
            problems.append(
                f"{path.name}: {len(flagged)} risk threshold(s) stated as a "
                f"rule with no nearby note that they are configurable "
                f"(first: {first})"
            )
    return problems


def main() -> int:
    problems: list[str] = []
    checked = 0

    for path in BROKER_PROMPTS:
        text = path.read_text(encoding="utf-8")
        body = text.split("\n---", 1)[-1]  # skip frontmatter
        checked += 1

        claims = []
        for pattern in CLAIM_PATTERNS:
            for match in re.finditer(pattern, body):
                claims.append(match.group(0))
        if not claims:
            continue

        has_verify = any(re.search(p, body, re.I) for p in VERIFY_PATTERNS)
        if not has_verify:
            problems.append(
                f"{path.name}: asserts {sorted(set(claims))} with no "
                f"verification instruction"
            )
            continue

        # A verify instruction is only actionable if it names a source. Two
        # exemptions: a file that declares itself a pattern library with no
        # specific vendor, or one that declares the vendor contract
        # unlocatable. Both are honest positions; silently omitting a source
        # is not.
        declares_generic = re.search(
            r"not a vendor integration|pattern library", body, re.I
        )
        declares_unverified = re.search(
            r"no public developer portal|least-documented", body, re.I
        )
        if not DOCS_PRESENT.search(body) and not (
            declares_generic or declares_unverified
        ):
            problems.append(
                f"{path.name}: tells the reader to verify but cites no "
                f"vendor documentation URL"
            )

    print(f"checked {checked} broker prompts for unverified vendor claims")

    for problem in problems:
        print(f"  {problem}")

    threshold_problems = check_thresholds()
    print(f"checked {len(list(PROMPTS.glob('*.md'))) - 2} prompts for hard-coded risk thresholds")
    for problem in threshold_problems:
        print(f"  {problem}")

    if problems or threshold_problems:
        print(
            "\nBroker auth internals must carry an explicit instruction to "
            "verify them against\ncurrent vendor documentation, and cite where "
            "that documentation lives.\n"
            "Risk thresholds must be framed as configurable or illustrative, "
            "not as universal rules.",
            file=sys.stderr,
        )
        return 1

    print("every broker prompt that asserts vendor internals says to verify them")
    print("every prompt stating a risk threshold says it is configurable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
