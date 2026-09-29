# Contributing

Thanks for improving the library. This document covers the frontmatter
contract, the review criteria, and the commands that keep the generated
files in sync.

## Two kinds of contribution

| You have | Do this |
|---|---|
| An idea for a prompt, not a finished draft | Open an issue using the **Prompt idea** form |
| A finished prompt | Open a pull request |

Proposals first is not bureaucracy. It is easier to agree on scope in an
issue thread than to reject a 900-line file over the shape of it.

## Frontmatter contract

Every file in `prompts/` starts with a YAML block:

```yaml
---
title: Display Name
description: One line, shown in index tables and search results
mode: build
model: any
category: architecture
tags: ["lowercase", "kebab-case"]
---
```

| Field | Rule |
|---|---|
| `title` | Display name. Must match the file's H1 exactly. |
| `description` | One line, no trailing period. This is the search snippet. |
| `mode` | One of `build`, `plan`, `review`, `all`. |
| `model` | `any`, or a pinned model ID. Default to `any`. |
| `category` | A key in `scripts/apply_categories.py`. New key needs a PR. |
| `tags` | Lowercase kebab-case. Reuse an existing tag where one fits. |

A blank line must follow the closing `---`. CI checks all of this.

## Writing a prompt

**Follow the library's structure.** Existing prompts use a layered shape and
it is what makes them skimmable:

1. Identity and core principles
2. Project context — which repo files to load first
3. The domain work, as a checklist or blueprint
4. Anti-patterns, stated explicitly
5. Guardrails and validation
6. A delivery contract defining done

**Be specific about the domain.** The value here is operational detail:
naming the actual failure modes, the actual protocol quirks, the actual
regulatory requirements. A prompt that could describe any project is worth
less than one that only fits this domain.

**Write the anti-patterns.** The most useful section in most prompts. What
does the agent routinely get wrong here, and how do you stop it?

**Make the contract checkable.** "Write good tests" is not a contract.
"Every new function has a table-driven test covering the empty, single, and
bulk cases, and `go test -race ./...` passes" is.

**Ground claims in something verifiable.** Official broker or vendor
documentation, published protocol definitions, or the repository itself. If
you are not sure of a field layout or an endpoint, say to verify it rather
than instructing the agent to guess.

## Commands

Run these from the repository root.

### Generators

Rewrite files, and are idempotent. Commit whatever they change.

```bash
python3 scripts/apply_titles.py           # sync frontmatter title and H1
python3 scripts/apply_categories.py       # sync the category key
python3 scripts/fix_heading_hierarchy.py  # one H1 per document
python3 scripts/generate_index.py         # regenerate index.md tables
```

A new prompt needs a `title` and a `category` registered in the first two
scripts before they will accept the file.

### Checks

Read-only. These are what `scripts/validate.sh` runs, and what CI runs on
every pull request.

```bash
scripts/validate.sh                        # everything below, in one go
python3 scripts/generate_index.py --check  # index.md tables are current
python3 scripts/check_nav.py               # every prompt is in the site nav
python3 scripts/check_prompt_sections.py   # every prompt has both sections
python3 scripts/check_vendor_claims.py     # vendor facts are marked unverified
python3 scripts/check_counts.py            # prose counts match the index
python3 scripts/check_no_fingerprint.py    # no private codebase named
python3 scripts/check_links.py             # internal links in built/ site/
python3 scripts/test_checks.py             # the checks still reject bad input
```

`check_links.py` needs a built site: run `mkdocs build` first, and it skips
itself if `site/` is absent.

What each one catches:

| Check | Catches |
|---|---|
| `generate_index.py --check` | `prompts/index.md` tables stale, so published counts disagree with the files |
| `check_nav.py` | a prompt that builds and is reachable by URL but missing from the sidebar |
| `check_prompt_sections.py` | a prompt shipping without an anti-patterns or guardrails section |
| `check_vendor_claims.py` | broker auth internals, endpoints, or capabilities stated as fact with no verification instruction; a broker-specific risk threshold presented as a universal rule |
| `check_counts.py` | a hand-written count in `README.md` or `docs/strategy.md` that disagrees with the generated index |
| `check_no_fingerprint.py` | a venue name the library already publishes, a home-directory path, the corpus project name (which has to be configured first — see below), or a commit-hash-shaped token under `prompts/` |
| `check_links.py` | a broken relative link in the built site |
| `test_checks.py` | a check that has quietly stopped rejecting the input it exists to reject |

**Every prompt needs both sections.** An anti-patterns section naming failures
the subject can actually produce, and a guardrails section written as checks
that can fail. The venue-independent gates live once in `sdk-build.md` under
**Cross-Cutting Guardrails**; the venue-specific ones belong in the prompt.
`check_prompt_sections.py` is structural — it asserts the sections exist, not
that the content is good, and a prompt can pass it and still be filler.

**Vendor specifics are hypotheses.** If a prompt states an endpoint, an auth
header, a digest algorithm, or a capability for a real vendor, it must also
tell the reader to verify it and cite where the documentation lives.
`check_vendor_claims.py` enforces that, and it is how the four wrong vendor
facts in 0.1.0 were caught. It cannot tell you a fact is *still* right, only
that the claim is not presented without provenance.

### Adding a prompt

Three files need updating, not one:

1. `prompts/<slug>.md` with valid frontmatter
2. `title` and `category` in `apply_titles.py` and `apply_categories.py`
3. an entry in the `nav:` block of `mkdocs.yml`

Skipping the third is the easy mistake: MkDocs still builds an unlisted
page, so the prompt renders and is reachable by URL, but it is missing from
the sidebar and CI logs only an INFO line. `check_nav.py` is what turns that
into a failure.

## Local site preview

```bash
uv run --with-requirements requirements-docs.txt mkdocs serve
```

No install step is needed; `uv` resolves the dependency into a cache. Use
`requirements-docs.txt` rather than naming a package, so the preview matches
the pinned versions CI builds with.

## Review criteria

A pull request is ready when:

- [ ] Frontmatter matches the contract, and `title` matches the H1
- [ ] `mode` and `category` are correct
- [ ] Tags reuse existing vocabulary where one fits
- [ ] Generators have been run and `validate.sh` passes
- [ ] The prompt follows the layered structure
- [ ] Anti-patterns are present and specific to the domain
- [ ] The delivery contract is checkable
- [ ] Technical claims are sourced or flagged for verification
- [ ] No credentials, account identifiers, or private endpoints
- [ ] Findings read from a private codebase are generalised

### Findings travel generalised

Some prompts here were written by running them against a codebase that is
not public, and cannot be made public by publishing about it. A finding
therefore ships as the failure mode with the evidence left in.

Generalising is the useful half, not a tax on the work. An anti-pattern
that names the defect is the part a reader on a different system can
still act on; the codebase it was found in is the part that is noise to
them and a pointer back to someone else's system to everyone.

So state the failure mode in general terms, and leave out three things: a
private codebase by name, a venue the prompt is not about, and a magnitude
from either — a line count, a file count, a service count, or one of those
written out in words. Write the shape rather than the measurement. "A
threshold duplicated across the service" is reusable; "2,400 lines in one
file" is a fingerprint and would have to be unpublished.

[scripts/check_no_fingerprint.py](scripts/check_no_fingerprint.py) enforces
part of the name half: a venue name the library already publishes, a
home-directory path, the corpus project name, and commit-hash-shaped
tokens under `prompts/`. Its venue vocabulary is the set this library
already names, so **a venue it does not publish passes the build** —
naming it in order to ban it would publish it. The venue rule reads
Markdown prose, so a name parked in a code fence or in frontmatter
passes too.

It cannot catch a magnitude, because a count is not distinguishable from
any other number a prompt legitimately uses; a check that banned counts
would ban the library. **Counts are caught in review, so read your own
diff for numbers, not only for names.**

The corpus project name is the one rule that has to be configured before
it can run, and configuring it is the interesting part: the name cannot
be in this repository at all, not in plaintext and not encoded, because
an encoding published next to its decoder publishes the name just as
well. So the check reads it from outside — set `CORPUS_NAME` in the
environment, or write it on the first non-comment line of a
`.corpus-name` file at the repository root. Both are gitignored, and
neither may be committed. **An unconfigured check fails rather than
skipping**, because a check that reports success for a rule it did not
run is worse than a build that stops and says why, so a fresh clone needs
one of the two before `validate.sh` is green. CI sets the `CORPUS_NAME`
repository secret — a secret rather than a variable, since a variable is
readable by anyone who can read the repository.

## House rules

**Keep line endings LF.** `.gitattributes` and `.editorconfig` enforce it.
No `cat -A > file` from a Windows editor.

**No secrets, ever.** Prompt files sometimes contain example credentials.
Use obvious placeholders: `REPLACE_ME`, `your-api-key`, `xxx`. Not a
realistic-looking key that a scanner might flag later.

**Do not widen scope silently.** If your PR changes another prompt, say why
in the description.

## Code of conduct

Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Why this library exists, and where it is going

[docs/strategy.md](docs/strategy.md) records the positioning decision behind
the library, the competitive landscape, and the open work. Read it if you
want to propose a new prompt category, or understand why the library is
organised around a financial trading vertical rather than breadth.
