# Changelog

All notable changes to this repository are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

0.1.0 was the first public release. 0.1.1 corrects vendor facts that shipped
in it, so if you built an adapter from 0.1.0, read that section before
trusting the values.

## [Unreleased]

Nothing yet.

## [0.4.0] - 2026-09-29

Three of the forty-two prompts in this library have been run against a real
codebase. That number is now on every row of the generated index, and this
release publishes the process behind it — including the parts of the process
that went wrong.

### Verification state

`docs/verification.md` is a new register with one row per prompt, recording
whether the prompt has been run against a real codebase and what came of it.
"Verified" means exactly that: the run produced anti-patterns the prompt did
not already contain. It is not a score, and a prompt nobody has run is not a
suspect one.

Three prompts are verified:

- `platform-engineering` — run against two existing Kubernetes repositories in
  an earlier pass and published in 0.3.1. Three anti-patterns, one guardrail.
- `backend-services` — run against production code in which many services
  implement a single contract. Four anti-patterns.
- `data-platforms` — run against a private production system whose data path is
  an operational streaming plane rather than a warehouse. Four anti-patterns.

**The other thirty-nine have not been run.** Each is named individually in the
register, so the absence is on the record rather than inferred from a summary.
`jvm-backend` is the one that is not simply waiting on time: no codebase with a
JVM service layer was available to run it against, and the row says that
instead of leaving it indistinguishable from a prompt nobody has got round to.

Two of the three verified rows carry a caveat worth more than the tick.
`data-platforms` was run against a streaming system, so the warehouse half of
that prompt — columnar storage, file formats, compaction, query plans,
per-dataset cost — has no evidence behind it and nothing was written about it.
The absence of findings there is not coverage. And `platform-engineering`'s
corpus was public rather than private, which is a different kind of evidence,
and is the reason the register records what was run and not only whether.

The register is a repository document rather than a site page, because
`mkdocs.yml` builds from `prompts/`. The site's front page links to it, and so
does the `Verified` column on every verified row.

### The findings

Four anti-patterns in `backend-services.md` and four in `data-platforms.md`,
appended to the existing sections; nothing already published was edited or
removed. The generalisable result is that both prompts named symptoms and
missed the design decision behind them — duplicated retry loops, a shared error
taxonomy that is not shared, and per-implementation timeouts are all what you
get when a shared definition is written out by hand again in each place that
needs it.

The findings were read out of a private codebase and are published in
generalised form. The failure mode goes out, the evidence stays in. That
is a constraint rather than a style preference: a public file cannot be
unpublished, and a name that survives a generalisation is a pointer back
to one codebase rather than a finding anyone else can use.

What that means here is specific rather than absolute, and it is worth
being exact about which part a check can hold and which part a reader has
to hold. The check scans the Markdown and Python in this repository, and
it holds this: no venue name this library already publishes appears in
Markdown prose, no absolute home-directory path appears anywhere, no
commit-hash-shaped token appears in a prompt, and the corpus project name
appears in none of it — not in plaintext, and not encoded, which is why
that rule reads the name from outside the repository and exits non-zero
when it is not configured rather than reporting success for a rule it did
not run. Two classes no check here can hold, because holding them would
mean publishing them: a magnitude, since a count is not distinguishable
from any other number a prompt legitimately uses, and the corpus's own
vocabulary — the venues and product names this library does not already
publish. Both were removed by reading, and both are caught in review
rather than by a build. The claim is therefore about the specific classes
above, and not about "nothing private" in the abstract.

### The worked example

`docs/worked-example.md` takes one prompt end to end: what it was given, what
it produced, the diff that was actually committed, and then what the prompt got
wrong. That last section is the longest one in the file, and it is the one
worth reading. It records a scope caveat that told the smallest reader to skip
the one entry that applies to them unconditionally; a safety claim about the
fingerprint check that was checked by reading its imports rather than its
source, and was wrong; a leak in a commit message rather than in a file; and
the two strongest findings in the report, neither of which fitted the prompt it
was found in.

### Verification

- `scripts/check_no_fingerprint.py`, new. Fails on a venue name in prose, an
  absolute home-directory path, the corpus project name, and a
  commit-hash-shaped token in a prompt. Its own docstring is explicit about
  what it cannot catch — counts and product names — because a count is not
  distinguishable from any other number a prompt legitimately uses. Both passes
  in this release were cleared for those by reading, not by the script.
  Two details are worth a line each. The corpus name is configured outside
  the repository, and the check exits non-zero when it is not, so the rule
  that forbids the name cannot be turned off by leaving it out. And the
  verification register's venue allowance is keyed to the slug cell of a row,
  which is where a prompt file name goes, and not to the row: the other cells
  are prose, and a claim about what was run is written there.
- `generate_index.py` reads the register and emits the `Verified` column, and
  refuses to run when the two disagree. A prompt with no row is an error rather
  than a default, because a prompt rendered "not verified" for want of a row is
  indistinguishable from one somebody decided not to run.
- 42 prompts, 44 pages, 2816 internal links resolve.
  `generate_index.py --check` exits 0; `mkdocs build --strict` succeeds.

## [0.3.1] - 2026-09-29

Maintenance, and a repositioning.

### The library is no longer presented as a trading library

26 of the 42 prompts are non-trading, across eight areas, and the audience is
anyone wiring an agent into a codebase. The README led with "built around
financial trading systems", the site nav led with the financial categories,
and the site's own front page did the same. A 42-prompt library was reading as
a 16-prompt one.

- README leads with the count, the eight areas, and the agent-tool audience
- Nav leads with architecture and application; Financial Engineering moves last
- The site front page (`prompts/index.md`) was the real front door and had been
  missed by the first pass, so it is repositioned too
- New framing for what these are: system prompts rather than user prompts, how
  to pick one by mode, and how to compose several for multi-area work
- Generated category tables reordered to match the nav
- `docs/strategy.md` argued for the opposite and won. The reversal is recorded
  there rather than deleted, because the original reasoning was sound for a
  single-domain library

The financial prompts are unchanged and still the depth differentiator, which
is what no other public library has. Only the framing moved.

### A confidential name removed from all history

A project name was in 2,016 file instances across 4 commits, in 3 commit
messages, and in one filename. The current tree was cleaned in `0.3.0`; this
release finishes the job. The name is not written out here, for the same
reason it is not written out anywhere else.

`git filter-repo` rewrote all 5 affected commits and 4 tags. The interesting
part is what a text replace alone would have missed:

- **Commit messages.** `--replace-text` does not touch them. Three messages
  still carried the name.
- **The filename.** The prompt's own filename carried the name and needed a
  path rewrite, done via a `fast-export`/`fast-import` pass.
- **A prefix collision.** Renaming the `DocSmith-Fin` persona to
  `DocSmith-FinOps` also matched the two pre-existing `DocSmith-FinOps`,
  producing `DocSmith-FinOpsOps`. Needed a placeholder and
  longest-match-first ordering.

Verified zero occurrences across every commit, message, path, and tag. The four
release notes were already clean. All 42 prompts, 2,816 links, and
`mkdocs build --strict` verified after the rewrite.

### Corrections

- Mode table said 30 `build` / 7 `all` against an actual 32 / 8
- The browse section still said 38 prompts, a figure wrong in every release
  since `0.1.0`
- Tag count said 222 against an actual 244
- Repository description said "19 cross-stack, 19 finance/trading" — the
  old 38-prompt split, with the financial half never right
- Topics rebalanced toward the agent-tooling audience

### CI

- The Pages guard added while the repository was private has been removed. It
  probed the Pages API with the workflow's `GITHUB_TOKEN`, which cannot read
  that endpoint, so it reported a green run for a deploy that never happened

## [0.3.0] - 2026-09-28

Broadens the library. Four new prompts, three new categories, and metadata
that finally reflects what was already there.

### Added

- **`platform-engineering.md`** (new `platform` category). Kubernetes,
  packaging, GitOps, networking, policy, secrets, progressive delivery, and
  cost, written around what breaks when an agent writes it: drift from a
  hand-mutated cluster, secrets in a ConfigMap or an image layer, a change
  reaching 100% in one step, a PDB ignored during a node upgrade.
- **`backend-services.md`** (`architecture`). Language-neutral by design. Makes
  the cross-stack claim concrete rather than asserted: idempotency is a
  property of the operation, a timeout means unknown rather than failed,
  retries need a budget and jitter, and a shared write needs a precondition.
- **`data-platforms.md`** (new `data` category). The principles behind the
  tool-heavy `data-engineering.md`: contracts enforced at write time, late and
  out-of-order data, idempotency demonstrated rather than assumed, quality
  checks that can fail the run, and a metric with a stated grain.
- **`jvm-backend.md`** (new `java` category). Spring Boot, Quarkus, and
  Micronaut compared against each other rather than a Spring manual, with the
  JVM-specific failure modes: virtual threads without a bounded pool, H2 in
  place of the real engine, `@Transactional` on a self-invoked method, a heap
  larger than the container limit.
- A generated **Browse by Language** table, split on implementation languages
  only, with an "Any stack" row for the 16 prompts that assume none.

### Changed

- Repository description and topics broadened: 15 topics became 20, adding
  `java`, `python`, `typescript`, `software-architecture`, and `kubernetes`.
  The description leads with cross-stack practice rather than Go.
- README leads with the language split and points at the table.
- `llm-integration.md` tagged `python`. It carries 15 Python code blocks and
  had no language tag, which is what the generated table is there to surface.
- Site word count corrected to ~80,000 after 0.2.0.

### Verification

All four prompts carry anti-patterns and guardrails from the start, so
`check_prompt_sections.py` gates them. Verified by injection: stripping the
guardrails section from `jvm-backend.md` produces a non-zero exit naming the
file. 42 prompts, 44 pages, 2815 internal links resolve.

## [0.2.0] - 2026-09-28

Every prompt now carries the two sections README.md and CONTRIBUTING.md
present as what makes a prompt worth reading. No new prompts, and no
existing guidance removed: this release adds the judgement that was missing.

### Added

- **Anti-patterns sections in all 38 prompts.** Seven broker SDK prompts, the
  two documentation prompts, and six others had none; fourteen had only one
  of the two sections.
- **Guardrails sections in all 38 prompts.** The cross-cutting gates —
  quality, provenance, telemetry, order safety — are stated once in
  `sdk-build.md` under Cross-Cutting Guardrails rather than restated seven
  times with seven different wordings. Each broker prompt keeps its
  venue-specific gates.
- `scripts/check_prompt_sections.py`, wired into `validate.sh`, asserting both
  sections exist in every prompt. It is structural only: a prompt can pass
  this check and still be filler, and the check says so.
- `check_nav.py` and `check_vendor_claims.py`, also in `validate.sh`. The
  first catches a prompt that renders but is missing from the site nav; the
  second catches vendor internals asserted as fact.

### Fixed

- Four wrong vendor facts corrected in `broker-integration.md` — Longbridge
  uses OAuth 2.0, Tiger uses private-key signing, and two cited hosts do not
  resolve. See the 0.1.1 section.
- Broker-specific risk limits in `trading-risk.md` reframed as configurable
  mandates. Maintenance margin varies by broker, account type, and market.
- `broker-webull.md` corrected from SHA256 to SHA1 and from Hong Kong to the
  published US-market coverage.
- `sdk-docs.md` told the agent to document all auth schemes as a flat
  checklist, inventing documentation for an SDK that may use none of them.
- `broker-vbroker.md` now states plainly that no public developer portal
  could be located and its specifics are unverified.
- MD029 no longer false-positives on the prompts' per-section ordered lists.

### Enforcement

Every check is proven to fail by injection, not merely to pass. Stripping a
verification instruction, a doc citation, a risk threshold's framing, a nav
entry, or either required section each produces a non-zero exit naming the
file. Five of the defects found in the checks themselves were found this
way, including one that passed when it should have failed.

## [0.1.1] - 2026-09-28

### Fixed

- Corrected four wrong vendor facts in `broker-integration.md`: Longbridge
  uses OAuth 2.0 rather than HMAC, Tiger uses private-key signing rather
  than header-based HMAC, and both Tiger and Webull were pointing at hosts
  that do not resolve. Two corrections were independently confirmed against
  working Go clients in this workspace
- Retracted the claim that Webull does not support order cancellation over
  the API. The current API exposes place, replace, and cancel together
- Corrected `broker-webull.md`, which carried the same SHA256 error and was
  framed as a Hong Kong API when the published OpenAPI is US-market
- Marked vbroker honestly as the least-documented adapter, with no public
  developer portal located
- Reframed broker-specific risk limits in `trading-risk.md` as configurable
  mandates rather than universal constants. Maintenance margin varies by
  broker, account type, instrument, and market
- Corrected `sdk-docs.md`, which told the agent to document "all supported
  auth schemes" as a flat checklist, inventing auth documentation for an SDK
  that may use none of them

### Added

- `scripts/check_vendor_claims.py`, wired into `validate.sh`, which fails a
  prompt that asserts vendor internals without a verification instruction or
  that states a risk threshold as a rule. It covers the per-broker prompts
  and the generic SDK prompts, verifies a cited doc URL belongs to the vendor
  the file names, and will not let one config entry's example framing
  discharge a neighbour's hard-coded value

### Audit scope

The vendor-fact audit covered every prompt that hard-codes broker or exchange
specifics: the nine `broker-*` prompts (seven per-broker SDKs plus the
integration guide and the certification guide), the two `sdk-*` prompts, and
the risk-management prompt, 12 in total. The remaining 26 prompts were
reviewed and carry no vendor claims; they are principle-based rather than
tied to a particular API, so this audit says nothing about the correctness of
their technical judgement.

## [0.1.0] - 2026-09-28

First public release. 38 prompts, a browsable site, and CI.

### Added

- 38 agentic-AI prompts under `prompts/`, each with a layered structure:
  identity, project context, domain checklist, anti-patterns, guardrails,
  and a delivery contract
- 19 prompts covering multi-broker trading systems, including one per broker
  venue (Longbridge, Tiger Trade, Webull, IBKR Client Portal, Futu OpenD,
  Hua Sing Tong vbroker, plus a generic HMAC pattern)
- MkDocs Material site with full-text search across ~67,000 words, a tag
  index over 222 tags, dark and light themes, and per-category navigation
- Frontmatter contract on every prompt: `title`, `description`, `mode`,
  `model`, `category`, `tags`
- Generator scripts that keep derived files in sync:
  `scripts/apply_titles.py`, `scripts/apply_categories.py`,
  `scripts/generate_index.py`
- Validation CI: frontmatter schema, generator freshness, markdown lint,
  internal link check, and a strict MkDocs build
- Pages deploy workflow
- Governance files: `LICENSE` (MIT), `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `SECURITY.md`
- Issue forms for bug reports, prompt ideas, new prompts, and site feedback;
  a pull request template

### Fixed

- Normalized line endings to LF across all 39 files. 15 of them had been
  committed with CRLF endings, which is now prevented by `.gitattributes` and
  `.editorconfig`
- Removed 62 `[reference:N]` citation artifacts from the financial documentation prompt and
  `sdk-docs.md`, artifacts of an earlier generation pass that read as broken
  citations on a rendered page
- Replaced generic placeholder headings with real ones. Ten prompts were
  headed "Role and Context" or had no H1 at all, which left their navigation
  entries unlabelled
- Unpinned `model: claude-sonnet-4-20250514` in two files to `model: any`, so
  all 38 prompts resolve the model at run time rather than naming a 2025
  model ID
- Made the prompt counts in `index.md` generated from frontmatter rather than
  maintained by hand, after they drifted out of sync with the files on disk
- Normalised heading hierarchy in 19 prompts. Several used `#` for what were
  really top-level sections, so each document had multiple H1s and the
  generated table of contents listed the title three times over. Fixed by
  `scripts/fix_heading_hierarchy.py`, 455 headings adjusted
- Labelled 24 unlabelled code fences. They were ASCII diagrams and directory
  trees, now tagged `text` so they render correctly
- Disambiguated two identical "Anti-Patterns" headings in
  `graphql-development.md`, the first now scoped to error handling
- Trailing whitespace, missing final newlines, inconsistent list markers,
  spaces inside code spans, and blank-line issues around fences and tables
- Set `MD025.front_matter_title` in the markdownlint config. The
  `title:` frontmatter key was being read as the document H1, so every real
  heading was reported as a duplicate

### Repository

- `index.md` rewritten as the library's home page with generated category,
  technology, quick-reference, and statistics tables
- Discussions is disabled for now. Every reference to it was repointed at
  issues, and a **Prompt idea** issue form replaces the scoping flow that
  CONTRIBUTING had promised Discussions would provide

  [Unreleased]: https://github.com/shing1211/prompt-engineering/compare/v0.4.0...HEAD
  [0.4.0]: https://github.com/shing1211/prompt-engineering/compare/v0.3.1...v0.4.0
  [0.3.1]: https://github.com/shing1211/prompt-engineering/compare/v0.3.0...v0.3.1
  [0.3.0]: https://github.com/shing1211/prompt-engineering/compare/v0.2.0...v0.3.0
  [0.2.0]: https://github.com/shing1211/prompt-engineering/compare/v0.1.1...v0.2.0
  [0.1.1]: https://github.com/shing1211/prompt-engineering/compare/v0.1.0...v0.1.1
  [0.1.0]: https://github.com/shing1211/prompt-engineering/releases/tag/v0.1.0
