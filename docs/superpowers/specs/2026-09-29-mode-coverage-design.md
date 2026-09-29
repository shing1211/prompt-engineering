# Mode Coverage and Verification Design

**Date:** 2026-09-29
**Status:** Approved for planning
**Scope:** Fill the two thin non-mutating modes, then verify the prompts that phase produces.

---

## Goal

The library aims at people wiring an agent into a codebase. Its weakest axis is
exactly that audience's axis.

```text
32 build    8 all    1 plan    1 review
```

For a coding agent, `plan` and `review` are the modes that matter most. They are
the non-mutating ones, the ones where agents differ most, and the ones where a
wrong prompt is cheapest. Two of forty-two prompts serve them.

Success means:

- `review` goes from one prompt to four, each answering a question the others
  do not, and `plan` stops being a project-specific artefact.
- Every prompt this project adds is verified before it ships, which is the
  correction for the last pass, where three prompts were added and never run.
- Every limit found during verification is recorded, not smoothed away.

`plan` mode stays at one prompt, and that is a deliberate non-goal rather than
an oversight. The problem with the current one is that it is a project artefact
wearing a prompt's clothes, not that it is alone. A second `plan` prompt would
either overlap the first or answer a question this design has not identified.
Adding one to reach a count is the failure mode the previous project already
recorded, and it is worse than a thin axis with an honest note.

## Context

The library is 42 prompts, public, CI green, 3 of 42 verified. The previous
project verified two prompts against a private codebase and produced a register,
a worked example, and a CI gate. It also left two things unfinished.

**The `plan` prompt is a project-coupled outlier.** It is 824 words against a
~1,200-word norm, and it is not the house six-layer structure — it is `A. Prompt
for Implementation Planning`, `B. Prompt for Project Review`, `C. Prompt for
Project Planning`, `D. Prompt for Project Implementation`. It assumes a `pending
phase` / `phase items` / `todo` backlog exists in the repository. A reader without
one is told to invent it. It passes `check_prompt_sections` only because the
headings happen to exist, not because it follows the contract the other 41
follow.

**The `review` prompt reviews a codebase, not a change.** One mention of a diff
across 1,480 words, though it does emit a `PR approval recommendation`, so it
gestures at changes without being built for them. For a coding agent, reviewing
*the change it just made* is a different and far more common task than auditing a
repository.

## Phase 1: mode coverage

Four prompts, in dependency order. One replacement, three additions.

### 1. `plan.md` — replace

Rewrite to the house six-layer structure. Keep what is genuinely valuable:
planning that dispatches sub-agents so the main session holds a plan rather than
a transcript, which is what `orchestrate.md` builds on.

Remove the backlog assumption. A plan derived from an imagined `pending phase`
list is worse than no plan, because it looks like the repository's plan. Where
there is no backlog, the prompt should work from the code and the request.

### 2. `change-review.md` — new, `mode: review`

Reviews a specific change: a diff, a branch, a commit range. The question it
answers is *did this change do what it claimed, correctly, and without breaking
its contract.*

Distinct from `code-review.md`, which stays the whole-codebase auditor answering
*is this codebase sound*. The two are complementary, and the existing prompt is
not modified.

### 3. `plan-review.md` — new, `mode: review`

Reviews a plan before it is implemented. This is the highest-value addition for a
coding-agent audience: plans fail before any code is written, and a bad plan
costs a full implementation cycle to discover. The `plan` mode has no reviewer
today, so the one mode that most needs a review step has the least support for it.

### 4. `test-review.md` — new, `mode: review`

Reviews tests: whether they assert behaviour or restate the implementation, what
is tautological, what the change leaves untested, what a failing test would not
have caught. No other prompt covers test quality, and it is where an agent's
output most often looks finished and is not.

### What this phase costs

Each prompt is roughly 1,200 words, plus a nav entry, an index row, a register
row, and a mode-count update. The count propagates into `README.md`,
`docs/strategy.md`, and the mode table, and `check_counts.py` fails the build if
prose and generated figures disagree. Breadth is expensive here by design; the
gates are the reason the last count drift was caught.

## Phase 2: verification

Runs after Phase 1, not alongside it. A prompt verified before it is rewritten
is verified against the wrong text.

Corpora are **non-mutating** — `plan.md` and the three new review prompts all
analyse and report without writing. That removes the entire safety constraint
that shaped the previous pass: no sealed-secret boundary, no read-only execution
rule, no fingerprint gate for corpus specifics, because nothing is executed and
no finding is derived from a system that cannot be named.

The two strongest non-trading repositories on hand — one Go, one Python, both
with commit histories in the hundreds — are named at execution time rather than
here. A public spec should not carry the paths to somebody's local checkouts.

**Out of scope: `jvm-backend`.** The JVM code available is a trading bot with no
Spring, Quarkus, Micronaut, or JPA, while the prompt is tagged with all of them.
The register's "no corpus available" is correct and stays.

## Sequencing

```text
Phase 1:  plan.md replacement
          change-review.md
          plan-review.md
          test-review.md
Phase 2:  verify each against a named corpus
          record in docs/verification.md
```

Each prompt is one commit with its own review, following the pattern the
previous project established.

## Global constraints

- **Every prompt this project adds is verified before it ships.** A prompt that
  has never been run is not marked verified, and the register says so
  individually rather than in aggregate.
- **No corpus fingerprint.** These corpora are non-mutating and non-trading, so
  the risk class does not arise. The existing `check_no_fingerprint.py` still
  runs and must stay green.
- **The house structure.** Every prompt carries the six layers, frontmatter with
  all six required fields, and both an anti-patterns section and a guardrails
  section. A prompt that does not is a defect, whatever it contains.
- **Existing checks are the harness.** `scripts/validate.sh` green at the end of
  every task; `generate_index.py --check` shows no drift; markdownlint clean at
  the pinned version CI uses.
- **No prompt is added unverified to hit a count.** If a prompt turns out not to
  earn its place, it is cut and the count goes back down.

## Known limits

**One corpus shape, again.** Both corpora are application code. A review prompt
verified against them has been tested on one kind of codebase, and a prompt for
reviewing, say, a compiler or a protocol implementation is unverified.

**Verifying a review prompt is easier than verifying a build prompt, and worth
correspondingly less.** Nothing is written, so nothing can be wrong in a
container. What a review prompt can be wrong about — missing a real defect — is
not established by the same evidence. The register's definition of "verified"
should be read as applying with that asymmetry in mind.

**Three new review prompts in one pass is a lot of new surface.** If two of them
turn out to overlap, the honest outcome is to merge or cut them, not to keep
three to protect a count.

**No evaluator, still.** "Good" means the run surfaced gaps a knowledgeable
reviewer had not already named. Unchanged from the previous project, and still
the strongest available claim without building an evaluator.

## Not in scope

- Verifying the remaining unverified prompts from the library's existing set.
- Adding prompts in any mode other than `plan` and `review`.
- Changing `code-review.md`.
- An automated quality evaluator.
- Any change to how the site builds or what it publishes.

`orchestrate.md` was out of scope here and was changed anyway. Running `plan.md`
against a real codebase found a defect in the rule `plan.md` itself states: it
demanded a command that fails when the work is wrong, and no such command exists
for work that can only be shown by running it somewhere the session cannot reach.
The fix is a four-element alternative — name the substituted condition, the
environment, who runs it, what stays unverified until it does — and every layer
that states the rule has to carry it. `plan.md` and `orchestrate.md` state it in
each of their own layers, and `plan.md` names `orchestrate.md` as its partner.
Fixing one and not the other would have left the library self-contradicting, so
the paired edit was made deliberately. See `plan.md:29-35` for the contract and
`.superpowers/sdd/2026-09-29-mode-coverage/progress.md` at `0bcbb13` for the
ruling. `code-review.md` remained untouched.
