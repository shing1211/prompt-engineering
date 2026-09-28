# Changelog

All notable changes to this repository are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

0.1.0 was the first public release. 0.1.1 corrects vendor facts that shipped
in it, so if you built an adapter from 0.1.0, read that section before
trusting the values.

## [Unreleased]

Nothing yet.

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
- Removed 62 `[reference:N]` citation artifacts from `financial-docs.md` and
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

[Unreleased]: https://github.com/shing1211/prompt-engineering/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/shing1211/prompt-engineering/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/shing1211/prompt-engineering/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/shing1211/prompt-engineering/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/shing1211/prompt-engineering/releases/tag/v0.1.0
