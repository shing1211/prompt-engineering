# Prompt Verification Design

**Date:** 2026-09-29
**Status:** Approved for planning
**Scope:** Verify the unrun prompts against a real codebase, and produce the worked example.

---

## Goal

Establish evidence that the library's prompts produce good output when run against
a real repository, and publish one end-to-end worked example as the proof artifact.

Success means:

- Every prompt verified in this pass has at least one anti-pattern that came from
  a real run rather than from experience.
- One prompt has a published worked example: real input, real output, real diff.
- Every prompt in the library is labelled by whether it has been verified.
- The public repository contains no fingerprint of the corpus.

## Context

The library is 42 prompts, ~86,000 words, published, with green CI and a live
site. It has zero traction and, more importantly, zero evidence that any prompt
produces good output.

One prompt has been run against real code: `platform-engineering`, verified
against two Kubernetes repositories. It immediately surfaced three anti-patterns
it did not previously name, which is the precedent and the reason to expect the
same from a second pass. The other 41 are unverified assertions.

Packaging and adoption were considered and rejected as the first move. Both
amplify a claim without testing it: shipping 42 unverified prompts as
installable artifacts is a larger distribution of unproven work, and directory
submissions put an unproven library in front of curators.

## Corpus

A private multi-broker trading system, referenced below only as "the corpus" and
not named here.

- A Go codebase large enough that its layout, rather than any one file, is
  where a reader has to start.
- Broker adapters that vary in size by a wide margin.
- A stream and SQL surface, with consumer entry points spread across the
  codebase rather than concentrated in one place.
- SQL migrations as the schema source of truth.

### Safety constraints

**Read-only.** Source text, file structure, and `git log` only. No build, no
test execution, no `go run`, no agent harness with tool access against the
corpus.

This is a hard constraint, not a preference. The corpus's most recent commit
fixes a bug where a configuration typo dialled live brokers and deleted real
positions. Any execution path that can reach a broker is out of scope.

**No corpus fingerprint in the public repository.** Findings are generalised into
the library's existing voice. Not published: venue names, adapter or directory
names, file counts, line counts, or any phrasing that points at a specific codebase as the source.
Published: the failure mode, stated so it generalises.

The public repository is the constraint that shapes this work. A prompt
improved by a private trading system is published for everyone to read, and a
finding that names how many integrations there are and what they share
publishes an architectural fingerprint. The generalised form — "integrations
with no shared contract" — is both safer and more useful, since a reader
running a handful of services can act on it.

**No secrets.** The corpus contains sealed secret manifests. Nothing in them is
read, referenced, or paraphrased.

## Scope

| Prompt | Corpus fit | Decision |
|---|---|---|
| `backend-services` | Strong: an adapter layer of uneven size in a Go codebase, with service entry points in more than one service | Verify |
| `data-platforms` | Adequate: a stream and SQL surface with consumers spread across services, and no lakehouse, warehouse or CDC layer to check | Verify, with a deferral condition |
| `jvm-backend` | None: no Java, Kotlin, or Gradle files | **Drop from this pass** |

`jvm-backend` has no corpus in the trading project. Verifying it requires a
public JVM repository, which is a different pass with a different safety
profile. It is dropped rather than verified against a substitute, and it is
explicitly labelled unverified.
### Deferral condition for `data-platforms`

**As hypothesised before the work:** the corpus has no top-level data platform
directory, and data lives inside services. That hypothesis was wrong. The probe
found a data platform — a message log and a time-series store, with consumers, a
dead-letter mechanism, and an outbox. The platform was simply not named or
shaped the way this section expected to find it.

A prompt about data *platforms* applied to a codebase with no data platform may
find that its subject does not exist. That is a legitimate result and is reported
as one. Phase 2 defers if and only if the honest finding is "this codebase has no
data platform to verify against" — in which case the prompt is left unchanged and
marked unverified, and the labelling work covers it.

Phase 2 does not defer because findings are thin. It defers only when there is
nothing to evaluate.

## Phase 1: `backend-services`

Probe the adapter layer for:

- Contract drift. Is there a shared interface, or does each integration declare
  its own? Where do they disagree — error semantics, cancellation, retry
  behaviour, ordering guarantees?
- Duplicated authentication. Is auth implemented once or per venue?
- Inconsistent timeout and context handling across the layer.
- Divergent error taxonomies that a caller cannot handle uniformly.
- Whether a developer adding an integration would copy an existing file or
  implement a contract.

**Known gap, confirmed by pre-design probing.** The adapters vary in size by a
wide margin and no shared interface exists anywhere in the corpus. The prompt's
twelve existing anti-patterns — retry without budget, missing timeouts, timeout
treated as failure, two services writing one dataset,
unversioned contract breaks, partial-success as 200, distributed transactions,
ignored graceful shutdown, unwatched circuit breakers — do not cover this.

The missing anti-pattern is stated in general terms: *when every integration
reimplements the contract because none is shared, the implementations diverge,
and the divergence is invisible until a caller depends on the difference.*

The divergence itself is evidence: a shared interface would have one place to
state cancellation and error semantics; a layer of separate files cannot.

## Phase 2: `data-platforms`

Probe the stream and SQL surface for:

- Exactly-once claims without idempotency at the consumer.
- Schema evolution: are migrations the schema source of truth, or is the schema
  implied by application code?
- Replay safety: what happens if a consumer re-reads from an earlier offset?
- Offset and checkpoint handling across the consumers.
- Whether the data plane and the serving plane share a schema without a boundary.

Findings are added as anti-patterns in the same generalised voice.

## Phase 3: worked example

One prompt, end to end, published.

- Real input: an excerpt of the corpus the prompt was run against, generalised
  where it would fingerprint.
- Real output: what the agent produced, abridged but unedited in substance.
- The real diff: the actual change the run produced, generalised where needed.
- What the prompt got wrong: stated plainly.

The example is the artifact `docs/strategy.md` names as the highest-value single
missing item. It falls out of Phases 1 and 2 rather than being separate work.

Prefer `backend-services`, since that phase has the most concrete material.

## Phase 4: CI, labels, docs

- `check_prompt_sections.py` already requires anti-patterns and guardrails, so
  new anti-patterns are covered by existing CI with no new check.
- Add verification state to the library's own documentation: verified, unverified,
  or unrunnable-without-a-corpus. This is the honesty requirement — a reader must
  be able to tell which prompts rest on a real run.
- Update `docs/strategy.md` to tick the verification item and record that
  `jvm-backend` was skipped for want of a corpus.
- `CHANGELOG.md` records what was verified and what was not.

## Known limits

Stated in the design rather than discovered later — with one exception, recorded
in place below.

**One corpus, one architecture.** A trading system is a real test and not a
neutral one. An anti-pattern drawn from a heavily multi-venue system may
over-weight multi-venue concerns. Where a finding is specific to high-fan-out
integrations, the prompt says so, so a reader with a handful of services knows
it does not apply.

**Most prompts remain unverified.** *As designed:* 2 of 42 were to be verified
after this pass — `platform-engineering` from the earlier pass, plus
`backend-services`, plus `data-platforms` only if its corpus held a data
platform to evaluate against. *As delivered:* **3 of 42**, because
`data-platforms` did have one, and the deferral condition was not met.
`jvm-backend` was skipped for want of a corpus. The remaining 39 are
unverified, each named individually in `docs/verification.md` so the absence
is on the record rather than inferred from a count.

This is the one limit above that did not survive contact with the work, so it
is the one worth reading twice: the design made a conditional bet on the corpus,
and the corpus answered. The other three held as written.

**A single run is not a benchmark.** This establishes that the prompts produce
good output, not that they produce good output reliably. The platform-engineering
pass found gaps; this pass finds gaps; neither measures variance.

**No evaluator.** There is no way to score output quality automatically. "Good"
here means the run surfaced gaps a knowledgeable reviewer had not already named.
That is a weaker claim than a benchmark and is the strongest available without
building one.

## Not in scope

- Packaging, `install.sh`, or harness-native output.
- Directory submissions, pinned repo, per-cluster posts.
- Adding new prompts or rebalancing the `mode` axis.
- Verifying the remaining prompts beyond the three covered here.
- Building an automated quality evaluator.
