## What this changes

<!-- One or two sentences. Which prompt, and what is different. -->

## Why

<!-- What was wrong or missing. If this fixes a reported issue, link it. -->

Closes #

## Checklist

- [ ] Frontmatter matches the contract in [CONTRIBUTING.md](/blob/main/CONTRIBUTING.md)
- [ ] `title` matches the file's H1 exactly
- [ ] `mode` and `category` are correct and, if `category` is new, it was added to `scripts/apply_categories.py`
- [ ] Tags are lowercase kebab-case and reuse existing vocabulary where one fits
- [ ] `python3 scripts/apply_titles.py && python3 scripts/apply_categories.py && python3 scripts/generate_index.py` has been run
- [ ] `scripts/validate.sh` passes locally
- [ ] The prompt follows the layered structure: identity, project context, domain checklist, anti-patterns, guardrails, delivery contract
- [ ] Anti-patterns are present and specific to this domain
- [ ] The delivery contract is checkable, not aspirational
- [ ] Technical claims are sourced, or the prompt instructs the agent to verify them
- [ ] No credentials, account identifiers, private endpoints, or realistic-looking keys
- [ ] Line endings are LF

## Scope

- [ ] This PR only touches the files it needs to
- [ ] Any change to an existing prompt is explained in "Why" above
