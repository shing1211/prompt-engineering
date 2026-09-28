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

# Cited host -> vendor terms that must appear in the same file for the
# citation to actually cover the claims. Guards against a file that cites one
# broker's documentation while asserting a different broker's internals.
KNOWN_VENDOR_HOSTS = {
    "longbridge.com": ("longbridge",),
    "openapi.longbridgeapp.com": ("longbridge",),
    "tigerbroker.com": ("tiger", "itigerup"),
    "tigerfintech.com": ("tiger", "itigerup"),
    "itigerup.com": ("tiger",),
    "webull.com": ("webull",),
    "vbkr.com": ("vbkr", "vbroker"),
    "futu": ("futu", "futunn"),
    "futunn.com": ("futu",),
}

# Scope of the vendor-claim rule. Covers the per-broker SDK prompts and the
# generic SDK prompts, because Phase 1 moves the shared Go SDK skeleton into
# sdk-build.md. If only broker-*.md were scanned, the new home for that
# material would be the one file CI does not inspect.
CLAIM_PROMPTS = sorted(PROMPTS.glob("broker-*.md")) + sorted(PROMPTS.glob("sdk-*.md"))

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

# A discharge note may not cross a list-item boundary. In a config block each
# metric is its own "- metric:" entry, and a neighbouring entry's example
# framing says nothing about this one. Without this, the last entry's
# discharge note silently covers every entry above it.
ENTRY_BOUNDARY = re.compile(r"^\s*[-*]\s+\w+\s*:|^\s*###\s|^\s*##\s")


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
            # Search outward and stop at the first entry boundary on each
            # side, so a discharge note cannot leak across metrics.
            found = False
            for j in range(i, hi):
                if j != i and ENTRY_BOUNDARY.match(lines[j]):
                    break
                if THRESHOLD_DISCHARGE.search(lines[j]):
                    found = True
                    break
            if not found:
                for j in range(i - 1, lo - 1, -1):
                    if ENTRY_BOUNDARY.match(lines[j]):
                        break
                    if THRESHOLD_DISCHARGE.search(lines[j]):
                        found = True
                        break
            if not found:
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

    for path in CLAIM_PROMPTS:
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
            r"not a vendor integration|"
            r"pattern library|"
            # Generic documentation prompts have no vendor of their own. Their
            # source of truth is the target repository's own spec and source.
            r"source of truth is the (?:target )?(?:repo|repository|SDK)|"
            r"this SDK actually supports|"
            r"SDK truth over prose|"
            r"openapi\.ya?ml|swagger\.json",
            body,
            re.I,
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
            continue

        # A verify instruction paired with a doc URL is only meaningful if the
        # URL belongs to the vendor the claims are about. A generic file that
        # cites one broker's docs while asserting another broker's internals
        # is the same defect as asserting with no source at all, so it has to
        # be caught rather than accepted as a pass. Applies to any file, not
        # only ones that call themselves generic, since the defect is the
        # mismatch between the cited source and the claim.
        # Match both the API host form (openapi.vbkr.com) and the docs host
        # form (open.longbridge.com), since vendors use either.
        cited_hosts = {
            m.group(1).lower()
            for m in re.finditer(
                r"https?://(?:openapi\.|open\.|api\.|developer\.|docs-en\.)?([a-z0-9-]+[a-z0-9.-]*\.[a-z]{2,})",
                body,
            )
        }
        for host in cited_hosts:
            expected = KNOWN_VENDOR_HOSTS.get(host)
            if not expected:
                continue
            # Strip URLs before searching for the vendor name, otherwise the
            # cited URL satisfies its own requirement and the check passes on
            # a file that only ever names the broker in a link.
            prose = re.sub(r"https?://\S+", " ", body)
            if not any(re.search(e, prose, re.I) for e in expected):
                problems.append(
                    f"{path.name}: cites {host} documentation but never names "
                    f"{expected[0]} in the text, so the cited source does not "
                    f"cover the claims made"
                )

    print(f"checked {checked} SDK prompts for unverified vendor claims")

    for problem in problems:
        print(f"  {problem}")

    threshold_problems = check_thresholds()
    print(f"checked {len(list(PROMPTS.glob('*.md'))) - 2} prompts for hard-coded risk thresholds")
    for problem in threshold_problems:
        print(f"  {problem}")

    if problems or threshold_problems:
        print(
            "\nSDK prompt auth internals must carry an explicit instruction "
            "to verify them\nagainst current vendor documentation, and cite "
            "where that documentation lives.\n"
            "Risk thresholds must be framed as configurable or illustrative, "
            "not as universal rules.",
            file=sys.stderr,
        )
        return 1

    print("every SDK prompt that asserts vendor internals says to verify them")
    print("every prompt stating a risk threshold says it is configurable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
