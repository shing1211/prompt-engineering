# Mode Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the project-coupled `plan.md` with a house-structure prompt, add three
review prompts, and verify all four against a real codebase.

**Architecture:** Phase 1 writes four prompts, one commit each. Phase 2 runs each against a
named corpus and records the result in the verification register. Phase 2 follows Phase 1
deliberately: a prompt verified before it is rewritten is verified against the wrong text,
which is how the previous project produced three prompts that were never run.

**Tech Stack:** Markdown, Python 3.12 (the existing `scripts/*.py` gates), bash
(`scripts/validate.sh`), MkDocs Material, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-29-mode-coverage-design.md`

## Global Constraints

- **Every prompt this project adds is verified before it ships.** A prompt that has never
  been run is not marked verified, and the register says so individually rather than in
  aggregate.
- **The house structure.** Every prompt carries the six layers — `Layer 1: Identity & Core
  Principles`, `Layer 2: Project Context (Loaded from Repository)`, `Layer 3: Core
  Specifications`, `Layer 4: Anti-Patterns (Never Do These)`, `Layer 5: Guardrails`,
  `Layer 6: Delivery Contract`. Frontmatter carries all six required fields: `title`,
  `description`, `mode`, `model`, `category`, `tags`. Tags are lowercase kebab-case. The
  description does not end with a period. The `title` matches the H1 exactly. A blank line
  follows the closing frontmatter fence.
- **Category must be one the generator already knows.** `generate_index.py` indexes
  `CATEGORY_TITLES[category]` and raises `KeyError` on anything else. All four prompts use
  `architecture`, which is where `code-review.md` already lives. Do not add a category.
- **Anti-patterns use the house form:** `- ❌ **Name.** Sentence.` in Layer 4. Each new
  prompt carries 10 to 14.
- **The existing checks are the test harness.** `scripts/validate.sh` green at the end of
  every task. `python3 scripts/generate_index.py --check` exits 0. markdownlint clean at
  the version CI pins, `markdownlint-cli@0.45.0`.
- **No prompt is added unverified to hit a count.** If a prompt does not earn its place, it
  is cut and the count goes back down.
- **`code-review.md` and `orchestrate.md` are not modified.**

## Review Focus

Failure modes the spec implies that no task's steps directly exercise, most likely first.
Each gets a test pinned in the task that owns the code.

1. **A new prompt is added to `prompts/` but not the register.** `generate_index.py` fails
   on a missing row, so this is loud. Expected: a red build, not a prompt that silently
   reads as verified. Pinned in Task 1 Step 3.
2. **The mode-count table in `README.md` drifts, and nothing will catch it.** The
   generated index has no mode breakdown, so this table is hand-maintained and no gate
   reads it — it drifted from 32/7/1/1 to 32/8/1/1 without a red build. Expected: the
   Task 5 Step 2 command recomputes it from the frontmatter, which is the only check it
   has. Pinned in Task 5.
3. **A new prompt is marked verified without a run behind it.** The register is the reader's
   only evidence, and a false tick is worse than a blank. Expected: Task 6 Step 2 requires
   naming the corpus and the anti-patterns it produced. Pinned in Task 6.
4. **`plan.md` keeps its backlog assumption after the rewrite.** The phrase is easy to
   reintroduce because it reads like project vocabulary. Expected: a grep for
   `pending phase|phase items` in `prompts/plan.md` returns nothing. Pinned in Task 2.
5. **The three review prompts overlap each other and are not distinguishable.** Three
   reviews that all say "look for bugs" is one prompt and two words of overhead. Expected:
   each names a question the others do not answer. Pinned in Task 5's whole-branch review.

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `prompts/plan.md` | Replace | Planning without a backlog assumption |
| `prompts/change-review.md` | Create | Reviewing one change rather than a codebase |
| `prompts/plan-review.md` | Create | Reviewing a plan before implementation |
| `prompts/test-review.md` | Create | Reviewing tests for what they actually assert |
| `mkdocs.yml` | Modify | Four nav entries: one replacement, three additions |
| `docs/verification.md` | Modify | Four rows, then four verified rows in Phase 2 |
| `README.md` | Modify | Mode table, browse table, prompt total |
| `docs/strategy.md` | Modify | Tick the mode-coverage item |

Every prompt file is one responsibility: the system prompt itself. No prompt imports
another, and the register is the only cross-cutting file.

---

## Phase 1: the prompts

### Task 1: `change-review.md`

The first new prompt, and the one that proves the house structure for the rest.

**Files:**
- Create: `prompts/change-review.md`
- Modify: `mkdocs.yml` (nav, immediately after `code-review.md`)
- Modify: `docs/verification.md` (one unverified row)

**Interfaces:**
- Consumes: the house structure and the four anti-patterns in `code-review.md`.
- Produces: `prompts/change-review.md`; the nav pattern later tasks copy;
  a register row later tasks extend.

- [ ] **Step 1: Write the prompt**

Six layers, per the Global Constraints. The question it answers, and the one
`code-review.md` does not: *did this change do what it claimed, correctly, and without
breaking its contract?*

Layer 3 covers, in order: what the change claims to do versus what it does; behaviour
that changed without the description mentioning it; the contract a caller depends on;
the error path; what the tests cover and what they do not; the input nobody wrote a case
for.

10 to 14 anti-patterns in Layer 4, house form. Candidates, chosen because none duplicates
an existing entry: a change whose description and diff disagree; a rename that moves
behaviour as well as a name; a new default that existing callers never opted into; an
error path added but unreachable; a test updated to match new behaviour rather than to
pin the behaviour; a widening of accepted input with no note in the description.

- [ ] **Step 2: Verify the gates that apply to a single new file**

```bash
python3 scripts/check_prompt_sections.py
```

Expected: `every prompt has anti-patterns and guardrails`, and `change-review.md` is not
listed as missing either.

- [ ] **Step 3: Write the register row, then prove the generator catches its absence**

Add to `docs/verification.md` in alphabetical order among the unverified rows:

```markdown
| `change-review` | no | Not run. | — |
```

```bash
python3 scripts/generate_index.py
```

Expected: the count rises to 43 and the row appears. This is Review Focus item 1 pinned —
the generator raises rather than defaulting, so a prompt without a register row is a red
build.

- [ ] **Step 4: Add the nav entry, directly after `code-review.md`**

```yaml
        - Code Review: code-review.md
        - Change Review: change-review.md
```

```bash
python3 scripts/check_nav.py
```

Expected: `every prompt file is listed in the nav`.

- [ ] **Step 5: Run the full validation**

```bash
bash scripts/validate.sh
```

Expected: `All checks passed.`

- [ ] **Step 6: Commit**

```bash
git add prompts/change-review.md mkdocs.yml docs/verification.md prompts/index.md
git commit -m "feat(review): add a prompt for reviewing a change rather than a codebase"
```

### Task 2: replace `plan.md`

**Files:**
- Modify: `prompts/plan.md` (full replacement)
- Modify: `docs/verification.md` (one unverified row, replacing the old `plan` row)

**Interfaces:**
- Consumes: the house structure from Task 1; the sub-agent dispatch pattern in
  `orchestrate.md`, which reads from this prompt.
- Produces: a `plan` prompt that works on a repository with no backlog.

- [ ] **Step 1: Write the replacement**

Six layers. The problem being fixed, stated in Layer 1: the current prompt assumes a
`pending phase` / `phase items` / `todo` backlog exists, and a reader without one is told
to invent it — a plan derived from an imagined backlog is worse than no plan, because it
looks like the repository's plan.

Keep what is genuinely used: dispatching sub-agents so the main session holds a plan
rather than a transcript. `orchestrate.md` builds on this and is not modified.

10 to 14 anti-patterns. Candidates: inventing a backlog to plan against; a plan that
restates the request without decomposing it; a step whose size is unbounded; a plan that
names files without saying what changes in them; sequencing work before its dependency;
declaring done without a checkable condition.

- [ ] **Step 2: Prove the backlog assumption is gone**

```bash
grep -cE 'pending phase|phase items' prompts/plan.md
```

Expected: `0`. This is Review Focus item 4 pinned — the phrase is easy to reintroduce
because it reads like ordinary project vocabulary.

- [ ] **Step 3: Update the register row in place**

Replace the existing `plan` row with a fresh unverified one. The prompt is being replaced,
so its verification history resets; say so in the row's third column rather than leaving a
tick that now describes different text.

- [ ] **Step 4: Run the full validation**

```bash
bash scripts/validate.sh
```

Expected: `All checks passed.`

- [ ] **Step 5: Commit**

```bash
git add prompts/plan.md docs/verification.md
git commit -m "refactor(plan): rebuild the planning prompt on the house structure"
```

### Task 3: `plan-review.md`

**Files:**
- Create: `prompts/plan-review.md`
- Modify: `mkdocs.yml` (nav, after `change-review.md`)
- Modify: `docs/verification.md` (one unverified row)

**Interfaces:**
- Consumes: Task 2's replacement, which is the text this prompt reviews.
- Produces: the second `review` prompt, and the register row Phase 2 fills in.

- [ ] **Step 1: Write the prompt**

Six layers. The question: *is this plan worth implementing, and will doing what it says
produce the thing that was asked for?*

10 to 14 anti-patterns. Candidates: a plan whose steps cannot be checked as done; a plan
that solves a problem nobody stated; a step that changes two things so they cannot be
reverted independently; a plan that omits the migration path; a plan whose scope silently
grows mid-document; a plan that names an outcome and not a mechanism.

- [ ] **Step 2: Add the nav entry and register row**

Follow Task 1 Steps 3 and 4 exactly. Row:

```markdown
| `plan-review` | no | Not run. | — |
```

- [ ] **Step 3: Run the full validation**

```bash
bash scripts/validate.sh
```

Expected: `All checks passed.`

- [ ] **Step 4: Commit**

```bash
git add prompts/plan-review.md mkdocs.yml docs/verification.md prompts/index.md
git commit -m "feat(review): add a prompt for reviewing a plan before implementing it"
```

### Task 4: `test-review.md`

**Files:**
- Create: `prompts/test-review.md`
- Modify: `mkdocs.yml` (nav, after `plan-review.md`)
- Modify: `docs/verification.md` (one unverified row)

**Interfaces:**
- Consumes: the house structure; the testing vocabulary in `testing.md`, which is a
  `build` prompt about designing tests and is not modified.
- Produces: the fourth `review` prompt.

- [ ] **Step 1: Write the prompt**

Six layers. The question: *would these tests fail if the implementation were wrong, and
would they still pass if it were?*

10 to 14 anti-patterns. Candidates: a test that asserts what the code does rather than
what it should do; a mock asserting its own configuration; a test that cannot fail; a
shared fixture hiding which case depends on what; an assertion on a log line; a test whose
name does not say the condition it pins; coverage treated as evidence; a test that passes
for a reason unrelated to the behaviour named in its name.

- [ ] **Step 2: Add the nav entry and register row**

Follow Task 1 Steps 3 and 4 exactly. Row:

```markdown
| `test-review` | no | Not run. | — |
```

- [ ] **Step 3: Run the full validation**

```bash
bash scripts/validate.sh
```

Expected: `All checks passed.`

- [ ] **Step 4: Commit**

```bash
git add prompts/test-review.md mkdocs.yml docs/verification.md prompts/index.md
git commit -m "feat(review): add a prompt for reviewing what tests actually assert"
```

### Task 5: reconcile every count the new prompts moved

Separate from the prompt tasks because it is the part most likely to be left undone, and
`check_counts.py` exists precisely because these numbers drifted once already.

**Files:**
- Modify: `README.md`
- Modify: `docs/strategy.md`

**Interfaces:**
- Consumes: Tasks 1–4, all committed.
- Produces: prose that agrees with the generated index.

- [ ] **Step 1: Read the current generated figures**

```bash
python3 scripts/check_counts.py
```

Expected: it fails, listing each disagreeing document and line. Those lines are the
inventory for this task.

- [ ] **Step 2: Update the README mode table**

Four prompts become `review` and one `plan` remains, so the table reads `build` 32,
`all` 8, `plan` 1, `review` 4.

**The index does not generate these numbers.** `prompts/index.md` has sections for
category, technology, and language, but no mode breakdown — the mode table in `README.md`
is hand-maintained and no gate checks it. That is why the numbers drifted to 32/8/1/1 from
32/7/1/1 earlier without anything failing.

So compute them rather than looking them up, and check the arithmetic:

```bash
python3 -c "
import re, glob, collections
c = collections.Counter()
for f in glob.glob('prompts/*.md'):
    t = open(f).read()
    if not t.startswith('---') or f.split('/')[-1] in ('index.md', 'tags.md'):
        continue
    c[re.search(r'^mode:\s*(.+)\$', t, re.M).group(1).strip()] += 1
print(dict(c), 'total', sum(c.values()))
"
```

Expected: `build` 32, `all` 8, `plan` 1, `review` 4, total 45. If it differs, the
prompts are not all in place — do not adjust the table to match reality, fix the missing
prompt first.

- [ ] **Step 3: Update the README prompt total and browse table**

The total rises to 45. Add a browse row for each of the three new prompts, keeping the
existing ordering: the code rows first, then the financial ones.

Expected: `grep -c 'prompts/change-review.md\|prompts/plan-review.md\|prompts/test-review.md'`
README.md` returns 3, and the browse table's rows are 26 in total, matching the 45 prompts
minus the 16 financial ones and the 3 that the table does not list individually.

- [ ] **Step 4: Update `docs/strategy.md`**

Tick the mode-coverage item if one exists, or add the completed state. Remove any prose
that describes `plan` or `review` mode as a single prompt.

Expected: `grep -ciE 'plan or .review. mode as a single|only one (plan|review)' docs/strategy.md`
returns 0, and any line describing the mode spread now matches Step 2's figures.

- [ ] **Step 5: Verify the counts now agree**

```bash
python3 scripts/check_counts.py
```

Expected: `every hand-written count matches the generated index`. This is Review Focus item
2 pinned.

- [ ] **Step 6: Run markdownlint and the full validation**

```bash
npx markdownlint-cli@0.45.0 --config .markdownlint.yaml README.md docs/strategy.md
bash scripts/validate.sh
```

Expected: both clean.

- [ ] **Step 7: Commit**

```bash
git add README.md docs/strategy.md
git commit -m "docs: reconcile the counts the three new review prompts moved"
```

## Phase 2: verification

### Task 6: verify `change-review` and `plan-review`

**Files:**
- Modify: `docs/verification.md` (two rows, unverified to verified)

**Interfaces:**
- Consumes: Tasks 1 and 3, both committed and unchanged since.
- Produces: two verified rows, and whatever anti-patterns the runs surface.

**Corpora are named at execution time.** `CHANGE_CORPUS` and `PLAN_CORPUS` are paths
supplied when this task runs, never written into a committed file. A public repository
should not carry paths to somebody's local checkouts. Both prompts are non-mutating, so
nothing is executed against the corpus and no safety constraint applies.

- [ ] **Step 1: Confirm the corpora are usable**

Both must be a real repository with a commit history deep enough to review a single change
against — at least 50 commits, and at least one commit that a reviewer would have
something to say about.

Expected: both meet the bar, or a different corpus is named before proceeding. A corpus
too small to review a change against produces a verdict with no information in it.

- [ ] **Step 2: Run each prompt against its corpus and record what it found**

For each prompt: choose a commit in the corpus that is a genuine change — a fix, a feature,
a refactor. Run the prompt's Layer 3 checklist against that commit's diff.

Write the findings down before editing anything, in a scratch file outside the repository.
As in the previous project, the findings must exist somewhere specific before they can be
generalised, or the generalisation step has nothing to work from.

Expected per prompt: at least one thing the prompt's anti-patterns did not already name. A
run that finds nothing is a legitimate result and the prompt stays unverified — recording
a tick for a run that found nothing would make the register mean the opposite of what its
own definition says.

- [ ] **Step 3: Add the anti-patterns the run found**

Two to four per prompt, in Layer 4, house form. Generalise: no corpus path, file name,
identifier, or count. These corpora are the user's own repositories rather than a system
that cannot be named, but the same discipline applies — a prompt that cites one person's
repo is less useful to the next reader.

- [ ] **Step 4: Flip the register rows**

```markdown
| `change-review` | yes | Run against a repository with a deep commit history. N anti-patterns added. | 2026-09-29 |
| `plan-review` | yes | Run against the same corpus. N anti-patterns added. | 2026-09-29 |
```

`N` is the real number from Step 2. This is Review Focus item 3 pinned: a row that does not
name what was run is a false claim to a reader.

- [ ] **Step 5: Regenerate, verify, and commit**

```bash
python3 scripts/generate_index.py
python3 scripts/generate_index.py --check
bash scripts/validate.sh
```

Expected: no drift, all checks passed.

```bash
git add prompts/change-review.md prompts/plan-review.md docs/verification.md prompts/index.md
git commit -m "docs(review): add anti-patterns found by running the prompts against a real repository"
```

### Task 7: verify `plan` and `test-review`, and close out

**Files:**
- Modify: `prompts/plan.md`, `prompts/test-review.md` (anti-patterns only)
- Modify: `docs/verification.md` (two rows)
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: Tasks 2 and 4. Produces: the last two verified rows and the release entry.

- [ ] **Step 1: Run both prompts against `CHANGE_CORPUS`, the corpus already in use**

Plan-review is verified against a real plan. `plan.md` is verified against the same
repository: does its Layer 3 checklist hold up when pointed at a real codebase with no
backlog, which is the case it was rewritten for? `test-review` against a commit that
changed tests.

Expected: at least one new anti-pattern each, or a recorded decision to leave the prompt
unverified with the reason.

- [ ] **Step 2: Add the anti-patterns and flip the rows**

As Task 6 Steps 3 and 4.

- [ ] **Step 3: Write the changelog entry**

State the mode counts as they now stand, name the four prompts, and say plainly how many
of the library remain unverified. A release entry that reports coverage without stating
what is still uncovered implies coverage that does not exist.

- [ ] **Step 4: Run the full validation and commit**

```bash
bash scripts/validate.sh
git add prompts/plan.md prompts/test-review.md docs/verification.md prompts/index.md CHANGELOG.md
git commit -m "docs: verify the planning and test-review prompts against a real repository"
```

Expected: `All checks passed.`

## Self-Review

**Spec coverage.** Goal, context, and the two phases each map to tasks. The `plan.md`
replacement is Task 2; the three review prompts are Tasks 1, 3, and 4; Phase 1 count
reconciliation is Task 5; Phase 2 verification is Tasks 6 and 7. The spec's Global
Constraints are restated verbatim in this plan's own. The `jvm-backend` exclusion is in the
Global Constraints by omission — no task touches it. Every Known limit is either carried
into Review Focus or deliberately not actionable: "one corpus shape, again" is why
Review Focus item 5 asks the whole-branch review to check the three review prompts are
distinguishable; "verifying a review prompt is worth less" is why Task 6 Step 2 accepts a
null result rather than pushing for a finding; "three review prompts is a lot of surface"
is why Task 5's review is tasked with merging or cutting rather than protecting the count.

**Step scan.** Tasks 2 and 5 are the two without a red-green test, and both say why:
`check_prompt_sections` asserts a section exists, not that a prompt is any good, so the
real gate is the count check and a grep. Manufacturing a passing test that proves nothing
is the failure mode the previous plan's self-review named. Every other step has a command
and an expected output.

**Type consistency.** Prompt slugs are `change-review`, `plan-review`, `test-review`
throughout, matching the file names and the register keys. The environment variables
`CHANGE_CORPUS` and `PLAN_CORPUS` are named in Task 6 and used again in Task 7 Step 1.
Category `architecture` is used by all four, which is required because
`generate_index.py` indexes `CATEGORY_TITLES[category]` and raises on anything unknown.

**Review Focus.** Item 1 is pinned in Task 1 Step 3, item 2 in Task 5 Step 5, item 3 in
Task 6 Step 4, item 4 in Task 2 Step 2, item 5 in Task 5's review. Each names the
condition and where its test lives.

**Proportion.** The plan is longer than four prompts of prose, and the excess is the gates
and the count inventory, not transcribed content. No step contains prompt prose; every
anti-pattern entry is named as a candidate with its general shape, leaving the writing to
the implementer, which is the part that is genuinely theirs.
