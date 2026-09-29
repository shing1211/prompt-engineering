# Prompt Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify the two unrun prompts against a real codebase and publish one
end-to-end worked example, so the library carries evidence rather than assertion.

**Architecture:** Each prompt is verified in its own commit. The analysis is
read-only against a private corpus, and findings are generalised into the
library's existing voice before they are written. A new check enforces the
safety constraint in CI, because a constraint nothing verifies is a constraint
that will eventually be broken.

**Tech Stack:** Markdown, Python 3.12 (the existing `scripts/*.py` checks),
bash (`scripts/validate.sh`), MkDocs Material, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-29-prompt-verification-design.md`

## Global Constraints

These apply to every task. They are the spec's constraints, copied verbatim in
substance.

- **Read-only against the corpus.** Source text, file structure, and `git log`
  only. No `go build`, no `go run`, no test execution, no agent harness with
  tool access against the corpus. The corpus's most recent commit fixes a bug
  where a configuration typo dialled live brokers and deleted real positions.
- **No corpus fingerprint in this repository.** Findings are generalised into
  the library's voice. Not permitted in any committed file: venue names, adapter
  or directory names from the corpus, file counts, line counts, commit hashes,
  or phrasing that points at a specific codebase as the source. The corpus path and the project name never
  appear in a commit, a file, or a commit message.
- **No secrets.** The corpus contains sealed secret manifests. Nothing in them
  is read, referenced, or paraphrased.
- **Existing checks are the test harness.** `scripts/validate.sh` must be green
  at the end of every task. Its 7 negative cases in `scripts/test_checks.py`
  must still be caught.
- **Anti-patterns are the deliverable.** A prompt that cannot be improved by
  the run is reported as unchanged, not padded.

## Review Focus

Failure modes the spec implies that no task's steps directly exercise, most
likely to bite first. Each line names the condition and the expected behaviour.
The test pinning each is added to the task that owns the code.

1. **A finding is generalised away into uselessness.** An anti-pattern written
   so abstractly that a reader cannot recognise their own code. Expected: a
   reader with three services should be able to tell whether it applies. Task 5
   pins this.
2. **A fingerprint survives into a public file** — a venue name, a directory
   name, or a count slips into an anti-pattern while it is being written.
   Expected: Task 2's check fails the build. Task 2 owns the check.
3. **Phase 2 finds nothing and the task invents a finding to have something to
   commit.** Expected: the prompt is left unchanged and reported as deferred.
   Task 4 owns this, and a no-op commit is a valid outcome.
4. **A prompt gains anti-patterns but loses its shape.** Additions change the
   H1, the frontmatter `title`, or the layered section order. Expected:
   `check_prompt_sections.py` and `check_counts.py` fail. Tasks 3 and 4 own
   this.
5. **The verification label is added to a prompt that was never verified.**
   Expected: the label script cross-checks against the actual commit history.
   Task 5 owns this.

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `scripts/check_no_fingerprint.py` | Create | Fails if a committed file names a corpus venue, path, or count. The safety constraint, made executable. |
| `scripts/validate.sh` | Modify | Add the new check as step 8, after the check tests. |
| `prompts/backend-services.md` | Modify | Add anti-patterns from the adapter probe. |
| `prompts/data-platforms.md` | Modify | Add anti-patterns from the stream probe, or leave unchanged if deferred. |
| `docs/worked-example.md` | Create | One prompt, end to end: input, output, diff, what it got wrong. |
| `prompts/index.md` | Modify | Verification label per prompt, generated, not hand-written. |
| `scripts/generate_index.py` | Modify | Emit the verification column from a single source of truth. |
| `docs/verification.md` | Create | The source of truth for which prompts are verified, and how. |
| `docs/strategy.md` | Modify | Tick the verification item; record `jvm-backend` skipped. |
| `CHANGELOG.md` | Modify | Record what was verified and what was not. |

**On the two label files.** The user approved `docs/verification.md` as the
single source of truth, with `prompts/index.md` consuming it. `index.md` has a
generated block between `<!-- BEGIN GENERATED TABLES -->` and
`<!-- END GENERATED TABLES -->`; the label column is added inside that block so
`check_counts.py` and the `--check` idempotence test keep working. Do not
hand-edit anything inside the generated markers.

---

## Task 1: Record the analysis out of band

**Files:**
- Read-only: the corpus
- Create: nothing tracked

**Interfaces:**
- Consumes: nothing
- Produces: an untracked scratch file at `/tmp/opencode/verification/` holding
  the raw findings. Later tasks read it; the repository never sees it.

The findings must exist somewhere before they can be generalised into a
committed file, or the generalisation step has nothing to work from and the
temptation is to write directly into the public prompt.

- [ ] **Step 1: Create the scratch directory outside the repository**

```bash
mkdir -p /tmp/opencode/verification
```

Expected: directory exists, nothing created inside the repo.

- [ ] **Step 2: Confirm the corpus is not modified by this plan**

```bash
git -C "$CORPUS_PATH" status --porcelain | wc -l
```

`CORPUS_PATH` is the corpus root, supplied out of band at execution time. It is
deliberately not written into this plan: a plan committed to a public repository
should not carry the path to a private codebase, and the executor has it.

Expected: `0`. If non-zero, stop and report — the corpus must not change.

- [ ] **Step 3: Probe the adapter layer, read-only, and write raw findings to the scratch file**

Probe for: a shared interface; whether auth is implemented once or per venue;
timeout and context handling across the layer; error taxonomies; what a ninth
integration would copy.

Use only `git ls-files`, `git show`, `grep` over tracked text, and file
structure. Do not run Go, do not execute tests, do not invoke a harness.

Record raw observations — including exact names and counts — in
`/tmp/opencode/verification/backend-services.raw.md`. This file is deliberately
specific; the generalisation happens in Task 3.

Expected: a file exists, and the repo shows no modification.

- [ ] **Step 4: Probe the stream and SQL surface the same way**

Write to `/tmp/opencode/verification/data-platforms.raw.md`. Probe for
exactly-once claims without idempotency, schema source of truth, replay safety
from an earlier offset, checkpoint handling across consumers, and whether data
and serving planes share a schema without a boundary.

Expected: a file exists, and the repo shows no modification.

- [ ] **Step 5: Verify both raw files contain what Task 3 needs**

```bash
grep -c '^' /tmp/opencode/verification/*.raw.md
```

Expected: both files non-empty. A file with fewer than three observations means
the probe found nothing — record that fact and carry it into Task 4, which
treats "nothing to verify against" as a legitimate result.

---

## Task 2: Make the safety constraint executable

**Files:**
- Create: `scripts/check_no_fingerprint.py`
- Modify: `scripts/validate.sh` (add step 8, after the check tests)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: `check_no_fingerprint.py`, runnable as `python3
  scripts/check_no_fingerprint.py`, exit 0 clean and 1 on drift. Task 3 and
  Task 4's anti-pattern edits are validated by it, and it is a required
  negative case in Task 6.

The constraint "no corpus fingerprint" is currently a promise in a document.
A promise nothing checks is a promise that breaks the first time someone pastes
a real line number into an anti-pattern.

- [ ] **Step 1: Write the failing test**

Add to `scripts/test_checks.py` a negative case that seeds a venue name into a
prompt and asserts this new check catches it. Follow the existing
`NEGATIVE_CASES` tuple shape: name, script, mutation lambda, expected substring
in the check's output. The expected substring is `venue name`.

Expected: the case is present in the `NEGATIVE_CASES` list, so Step 2 has
something to fail on, and the mutation uses the existing `_replace` helper
rather than a new one.

- [ ] **Step 2: Run it to verify it fails**

```bash
python3 scripts/test_checks.py
```

Expected: FAIL on the new case with a setup error, because
`scripts/check_no_fingerprint.py` does not exist yet.

- [ ] **Step 3: Implement the check**

Create `scripts/check_no_fingerprint.py`. Follow the module docstring style of
the existing checks: state what it can and cannot detect, and why.

Expected: the file exists, its docstring names both the detected classes and
the undetected ones, and it imports only `re`, `sys`, and `pathlib`.

Scan tracked Markdown and Python under `prompts/`, `docs/`, `scripts/`, and the
repo root. Fail on:

- A broker venue name that is not already permitted by
  `check_vendor_claims.py`'s provenance rule. Reuse that script's
  `KNOWN_VENDOR_HOSTS` vocabulary rather than inventing a second list; the
  existing check permits a vendor name in a prompt that carries a verification
  instruction, and this check must not contradict it.
- An absolute path beginning `/home/`.
- The corpus's project name, in any case.
- A `git log`-shaped hash in a prompt file: seven or more consecutive hex
  characters that are not a documented identifier.

The docstring must state the limit plainly: it catches names and paths, not a
file count or a line count. Those are covered by review, not by this check.

- [ ] **Step 4: Run the new check to verify it passes on the current tree**

```bash
python3 scripts/check_no_fingerprint.py
```

Expected: exit 0. The library already names venues in its broker prompts, all
under the existing provenance rule, so the check must accept them.

- [ ] **Step 5: Run the check tests to verify the negative case is caught**

```bash
python3 scripts/test_checks.py
```

Expected: all 8 negative cases caught, including the new one.

- [ ] **Step 6: Wire it into `validate.sh`**

Add a step after the check-tests step, following the existing
`step` / `if python3 scripts/...` / `ok` / `fail` shape. Update the header
comment's numbered list to include it.

Expected: `grep -c 'check_no_fingerprint' scripts/validate.sh` returns 2 or
more — once in the step body, once in the header comment. One means the
invocation landed but the documentation did not.

- [ ] **Step 7: Run the full validation**

```bash
bash scripts/validate.sh
```

Expected: `All checks passed.`

- [ ] **Step 8: Commit**

```bash
git add scripts/check_no_fingerprint.py scripts/test_checks.py scripts/validate.sh
git commit -m "ci: make the no-fingerprint constraint executable"
```

---

## Task 3: Verify `backend-services`

**Files:**
- Modify: `prompts/backend-services.md` (Layer 4: Anti-Patterns)
- Read: `/tmp/opencode/verification/backend-services.raw.md`

**Interfaces:**
- Consumes: the raw findings from Task 1 Step 3; the check from Task 2.
- Produces: generalised anti-patterns in `backend-services.md` Layer 4. Task 5
  labels this prompt verified based on the commit from Task 3.

- [ ] **Step 1: Write the failing test**

The library's check for this prompt is `check_prompt_sections.py`, which passes
before and after — it asserts a section exists, not that its contents improved.
A passing suite is therefore not evidence for this task. Use the Task 2 check
as the real gate, plus a manual read.

State that in the commit message. Do not manufacture a passing test that proves
nothing.

- [ ] **Step 2: Run the fingerprint check to establish the baseline**

```bash
python3 scripts/check_no_fingerprint.py
```

Expected: exit 0. The prompt is currently clean and must stay clean.

- [ ] **Step 3: Write the new anti-patterns**

Add to Layer 4 of `prompts/backend-services.md`, in the existing
`- ❌ **Name.** Sentence.` shape, two to four entries derived from the raw
findings.

Expected: `grep -c '^- ❌' prompts/backend-services.md` returns 12 to 16. The
pre-existing twelve are unchanged; a count outside that range means an entry
was mangled or the section was reordered.

The known gap, from the pre-design probe: every integration reimplements the
contract because none is shared, so the implementations diverge invisibly until
a caller depends on the difference. The divergence in the corpus is the
evidence — a shared interface has one place to state cancellation and error
semantics; N files cannot.

Other candidates, from the raw findings: duplicated authentication that must be
correct N times; divergent error taxonomies a caller cannot handle uniformly;
what a new integration copies when no contract tells it what to implement.

Generalise. No venue names, no counts, no directory names, and nothing that points
at a specific codebase as the source.
Where a finding only applies at high fan-out, say so in the entry, so a reader
with three services knows it does not apply to them.

- [ ] **Step 4: Run the fingerprint check to verify the generalisation held**

```bash
python3 scripts/check_no_fingerprint.py
```

Expected: exit 0. If it fails, a name or path slipped in — fix the prose, do not
weaken the check.

- [ ] **Step 5: Run the full validation**

```bash
bash scripts/validate.sh
```

Expected: `All checks passed.` This proves the prompt kept its shape: H1, title,
and section order unchanged.

- [ ] **Step 6: Diff-review the change for fingerprint by eye**

```bash
git diff prompts/backend-services.md
```

Read every added line and confirm: no venue name, no count, no corpus directory,
no commit hash, and the failure mode is stated as a general property.

Expected: `git diff --stat prompts/backend-services.md` shows only insertions, or
insertions balanced by deletions of the same entries — never a modification to
Layers 1, 2, 3, 5, or 6. A changed H1 or a reordered section means the
fingerprint check passed but the prompt's shape moved.

- [ ] **Step 7: Commit**

Follow the `8869479` pattern: subject names what was found, body says what was
probed and what it missed. The body must not name the corpus or any specific.

```bash
git add prompts/backend-services.md
git commit -m "docs(services): add anti-patterns found by running the prompt against a real codebase"
```

---

## Task 4: Verify `data-platforms`

**Files:**
- Modify: `prompts/data-platforms.md` (Layer 4: Anti-Patterns), only if the
  probe found something
- Read: `/tmp/opencode/verification/data-platforms.raw.md`

**Interfaces:**
- Consumes: the raw findings from Task 1 Step 4; the check from Task 2.
- Produces: either generalised anti-patterns, or a recorded deferral. Task 5
  labels this prompt from the outcome.

The spec sets one deferral condition: if the honest finding is that the corpus
has no data platform to verify against, defer. Deferring is a legitimate
outcome and is not a failure. Inventing a finding to have something to commit
is a failure.

- [ ] **Step 1: Establish the baseline**

```bash
python3 scripts/check_no_fingerprint.py
```

Expected: exit 0.

- [ ] **Step 2: Apply the deferral test**

Read the raw findings and answer one question: is there a data platform here to
evaluate against? Write the answer, either way, into the scratch file.

Expected: `/tmp/opencode/verification/deferral-decision.md` exists and states
the answer in one sentence. The decision is written down whether it is yes or
no, so a later reader can tell a considered deferral from an oversight.

If no — the corpus keeps data inside services and has no platform — record the
deferral in the commit message, leave `prompts/data-platforms.md` unchanged, and
continue to Task 5. A no-op commit is a valid outcome; make it explicitly:

```bash
git commit --allow-empty -m "docs(data): defer verification, no data platform in the corpus to evaluate against"
```

If yes, continue to Step 3.

- [ ] **Step 3: Write the new anti-patterns**

Add two to four entries to Layer 4 in the same shape as Task 3, derived from the
raw findings. Candidate failure modes: an exactly-once claim with no idempotency
at the consumer; a schema implied by application code rather than owned by
migrations; replay from an earlier offset with no defined outcome; checkpoints
that do not survive the thing they are supposed to survive; data and serving
planes sharing a schema with no boundary between them.

Generalise exactly as in Task 3.

Expected: `grep -c '^- ❌' prompts/data-platforms.md` returns 12 to 16. The
pre-existing twelve unchanged, two to four added.

- [ ] **Step 4: Run the fingerprint check**

```bash
python3 scripts/check_no_fingerprint.py
```

Expected: exit 0.

- [ ] **Step 5: Run the full validation**

```bash
bash scripts/validate.sh
```

Expected: `All checks passed.`

- [ ] **Step 6: Commit**

```bash
git add prompts/data-platforms.md
git commit -m "docs(data): add anti-patterns found by running the prompt against a real codebase"
```

---

## Task 5: Publish the worked example and the verification labels

**Files:**
- Create: `docs/worked-example.md`
- Create: `docs/verification.md`
- Modify: `prompts/index.md` (generated block only)
- Modify: `scripts/generate_index.py`
- Modify: `docs/strategy.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: the Task 3 and Task 4 commits.
- Produces: `docs/verification.md` as the single source of truth, and a
  generated column in `prompts/index.md` that reads from it. The site build
  consumes `docs/verification.md` only if `mkdocs.yml` nav includes it — add it
  to the nav, or the file is invisible to a reader.

**Part A — the source of truth.**

- [ ] **Step 1: Write `docs/verification.md`**

A table with one row per prompt: name, verified or not, and if verified, what
was run and when. Verified entries: the two from this pass, plus
`platform-engineering` from the earlier pass. Everything else is unverified, and
`jvm-backend` is unverified with the reason that no corpus was available.

State the definition once: verified means the prompt was run against a real
codebase and the run produced anti-patterns it did not already contain. Not a
benchmark, not a score. This is the honesty requirement — a reader must be able
to tell which prompts rest on a real run.

Expected: `grep -c '^| \`' docs/verification.md` returns 42, one row per prompt,
which `check_counts.py` independently confirms as the total. A lower count means
prompts were missed; a higher count means a file that is not a prompt was listed.

- [ ] **Step 2: Commit**

```bash
git add docs/verification.md
git commit -m "docs: record which prompts have been verified against a real codebase"
```

**Part B — the worked example.**

- [ ] **Step 3: Write `docs/worked-example.md`**

One prompt, `backend-services`, end to end. Four sections:

- **The input** — an excerpt of what the prompt was given, generalised where it
  would fingerprint. Say plainly that the corpus is private and generalised.
- **The output** — what the agent produced, abridged in length but not in
  substance. Do not tidy it into looking better than it was.
- **The diff** — the actual change the run produced, in the same generalised
  form as it appears in the committed prompt.
- **What the prompt got wrong** — the honest part. What it missed, what it
  overstated, what a reviewer had to fix by hand. A worked example that shows
  only successes teaches nothing and is not believable.

Expected: the file has all four sections, and the fourth is non-empty —
`awk '/## What the prompt got wrong/,0' docs/worked-example.md | grep -c '[a-z]\\{20,\\}'`
returns a positive number. An empty section is the failure this step exists to
prevent.

- [ ] **Step 4: Run the fingerprint check**

```bash
python3 scripts/check_no_fingerprint.py
```

Expected: exit 0. The generalised input and diff are the most likely place for
a name or count to survive.

- [ ] **Step 5: Commit**

```bash
git add docs/worked-example.md
git commit -m "docs: add the worked example"
```

**Part C — the generated label.**

- [ ] **Step 6: Add the verification column to `generate_index.py`**

Read `docs/verification.md` and emit a `Verified` column in the category tables
inside the generated markers. Pin the format: a link to `../docs/verification.md`
where a prompt is verified, and the literal `not verified` where it is not.

Expected: the column header is `Verified`, and every row carries either the link
or `not verified` — no row left blank.

The generator must fail loudly if `docs/verification.md` names a prompt that
does not exist, and must not silently label an unverified prompt as verified.
This is Review Focus item 5.

- [ ] **Step 7: Run the generator**

```bash
python3 scripts/generate_index.py
```

Expected: rewrites the generated block, and says so.

- [ ] **Step 8: Verify the generator is idempotent**

```bash
python3 scripts/generate_index.py --check
```

Expected: exit 0. This is the drift test.

- [ ] **Step 9: Add `docs/verification.md` to the nav in `mkdocs.yml`**

It is the document that tells a reader which prompts to trust, so it belongs in
the nav near the top, after the orchestration entries. `check_nav.py` only
requires that every prompt file is listed, so this is a judgement call, not a
test.

Expected: `python3 scripts/check_nav.py` still exits 0, and
`grep -c 'verification' mkdocs.yml` returns at least 1.

- [ ] **Step 10: Run the full validation**

```bash
bash scripts/validate.sh
```

Expected: `All checks passed.`

- [ ] **Step 11: Build the site strictly**

```bash
mkdocs build --strict
```

Expected: success, no warnings.

- [ ] **Step 12: Commit**

```bash
git add prompts/index.md scripts/generate_index.py mkdocs.yml
git commit -m "docs: show verification state in the generated index"
```

**Part D — record it.**

- [ ] **Step 13: Update `docs/strategy.md`**

Tick the verification item. Record that `jvm-backend` was skipped for want of a
corpus, so the open list reflects reality. Do not tick the worked-example item
separately; it is now done and should read as done.

Expected: `grep -c '^- \[x\]' docs/strategy.md` increases by 2 from the
pre-task count, and the text mentions `jvm-backend` by name. An increase of 3
means an unticked item was ticked by mistake.

- [ ] **Step 14: Update `CHANGELOG.md`**

Add a `0.4.0` entry: verification state, the worked example, the new check, and
explicitly which prompts remain unverified. State that the findings came from a
private codebase and are published in generalised form, so a reader knows why
the examples are phrased the way they are.

Expected: `grep -c '^## \[0.4.0\]' CHANGELOG.md` returns 1, and the entry names
both the verified prompts and the unverified remainder. An entry that mentions
verification without naming what stayed unverified is the failure mode — it
implies coverage that does not exist.

- [ ] **Step 15: Run the full validation and commit**

```bash
bash scripts/validate.sh
git add docs/strategy.md CHANGELOG.md
git commit -m "docs: record the verification pass in the changelog and strategy"
```

Expected: `All checks passed.`, then a clean commit.

---

## Task 6: Close the loop in CI

**Files:**
- Modify: `CONTRIBUTING.md`
- No workflow change. `validate.yml` already runs `scripts/validate.sh`, so
  Task 2's wiring reaches CI on its own. The inline credential scan in that
  workflow is a different concern and stays as it is.

**Interfaces:**
- Consumes: every check from Task 2.
- Produces: a contributor document that states the no-fingerprint rule, so the
  constraint is known before it is broken rather than discovered as a red build.

- [ ] **Step 1: Establish the baseline**

```bash
bash scripts/validate.sh
```

Expected: `All checks passed.`

- [ ] **Step 2: Confirm `validate.yml` calls `scripts/validate.sh`**

`validate.yml` already runs `scripts/validate.sh` as one step, plus `mkdocs
build --strict`, markdownlint, and an inline credential scan. Because Task 2
Step 6 wired the new check into `validate.sh`, CI already runs it. There is
nothing to add to the workflow.

Do not add a second invocation. The credential scan is inline in the workflow
and is a different concern from this check — leave it alone.

Expected: `git diff --name-only` after this task lists only `CONTRIBUTING.md`.
Any workflow file in the diff means a redundant step was added.

- [ ] **Step 4: Document the rule in `CONTRIBUTING.md`**

Add a short section under the review criteria: prompts state failure modes in
general terms, and must not name a private codebase, a venue the prompt is not
about, or a specific line count. Say that `scripts/check_no_fingerprint.py`
enforces the name-and-path part, and that counts are caught in review. A
contributor who knows the rule writes to it; one who does not discovers it as a
red build.

Expected: `grep -c 'check_no_fingerprint' CONTRIBUTING.md` returns at least 1,
so a contributor can find the rule and the check by name.

- [ ] **Step 5: Run markdownlint on the changed docs**

```bash
npx markdownlint-cli --config .markdownlint.yaml CONTRIBUTING.md
```

Expected: exit 0.

- [ ] **Step 6: Run the full validation and commit**

```bash
bash scripts/validate.sh
git add CONTRIBUTING.md
git commit -m "docs: state the no-fingerprint rule for contributors"
```

Expected: `All checks passed.`

---

## Self-Review

**Spec coverage.** Goal and Context are framing, not tasks. Corpus and its
safety constraints are Task 1 and enforced by Task 2. Scope: `backend-services`
is Task 3, `data-platforms` is Task 4 including its deferral condition,
`jvm-backend`'s drop is recorded in Task 5 Part A and Task 5 Part D. Phase 3,
the worked example, is Task 5 Part B. Phase 4 — CI, labels, docs — is Tasks 5
and 6. Known limits: one-corpus-one-architecture is Task 3 Step 3's fan-out
caveat; most-prompts-unverified is Task 5 Part A; single-run-is-not-a-benchmark
and no-evaluator are Task 5 Part A's definition. Every spec section maps to a
task.

**Step scan.** Each step is one action with a checkable result. Task 3 Step 1
is the weakest and is labelled as such: there is no automatic test for "this
prompt got better", and the plan says so rather than inventing one. Task 4
Step 2 produces either a commit or a no-op commit, and both are valid outcomes
the step names.

**Type consistency.** `check_no_fingerprint.py` is named identically in Task 2,
Task 3, Task 4, Task 5, and Task 6. `docs/verification.md` is created in Task 5
Part A and consumed by Part C and named in Part B's commit. The scratch paths
are created in Task 1 and read in Tasks 3 and 4.

**Review Focus.** Item 1 is pinned by Task 5 Part B Step 3, which requires the
example to say what the prompt got wrong and requires a three-service reader to
be able to tell whether an entry applies. Item 2 is pinned by Task 2. Item 3 is
pinned by Task 4 Step 2, where a deferral is a valid outcome. Item 4 is pinned
by the `validate.sh` gate in Tasks 3 and 4. Item 5 is pinned by Task 5 Part C
Step 6, where the generator must fail loudly rather than mislabel.

**Proportion.** The plan is longer than the two prompts it edits. That is
justified: the targets are prose, where the decisions are which findings to
generalise and where to stop, and those decisions are exactly what a plan is
for. The extra length is the safety constraints and the Review Focus, not
transcribed code.
