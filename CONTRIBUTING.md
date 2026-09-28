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

Run these from the repository root. All three are idempotent.

```bash
python3 scripts/apply_titles.py      # sync frontmatter title and H1
python3 scripts/apply_categories.py  # sync the category key
python3 scripts/generate_index.py    # regenerate index.md tables
scripts/validate.sh                  # the same checks CI runs
```

`generate_index.py --check` exits non-zero when `prompts/index.md` is stale,
which is how CI prevents the counts from drifting. If you add a prompt
without regenerating, that check fails.

## Local site preview

```bash
uv run --with mkdocs-material mkdocs serve
```

No install step is needed; `uv` resolves the dependency into a cache.

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
