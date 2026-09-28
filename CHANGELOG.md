# Changelog

All notable changes to this repository are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The project had no releases before 0.1.0, so every change to date appears
under that heading.

## [Unreleased]

Nothing yet.

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

### Repository

- `index.md` rewritten as the library's home page with generated category,
  technology, quick-reference, and statistics tables

[Unreleased]: https://github.com/shing1211/prompt-engineering/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/shing1211/prompt-engineering/releases/tag/v0.1.0
