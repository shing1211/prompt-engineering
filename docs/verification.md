# Verification register

Which prompts in this library have been run against a real codebase, and what
came of it. This file is the source of truth for the `Verified` column in the
[prompt index](../prompts/index.md);
[scripts/generate_index.py](../scripts/generate_index.py) reads the table below
and fails if the two disagree, so a prompt cannot be added, renamed or dropped
without this file changing with it.

## What verified means

A prompt is **verified** when it was run against a real codebase and that run
produced anti-patterns the prompt did not already contain. That is the whole
definition, and it is deliberately narrow.

It is not a score and there is no ranking. An unverified prompt is not a
suspect one: most of this library is unverified, and that is the normal state
of a prompt written by someone with experience rather than by someone with a
test case. Verification records that a prompt left the page at least once and
found something. It does not claim the prompt is better than one that has not
been run, because a run against one codebase is evidence about that codebase
and about nothing else.

A prompt can be verified and still have no evidence behind much of what it
covers. One of the three runs below is in that state — half of that prompt was
run against a system the other half does not describe. The third carries a
different caveat again: a different kind of corpus rather than an uncovered
half. Each says so in its own row, and the caveats are the part of this file
worth reading.

## The register

One row per prompt, in alphabetical order by file name.

| Prompt | Verified | What was run | When |
|---|---|---|---|
| `api-design` | no | Not run. | — |
| `architecture` | no | Not run. | — |
| `backend-services` | yes | Run against production code in which many services implement a single contract. Four anti-patterns added. | 2026-09-29 |
| `broker-certification` | no | Not run. | — |
| `broker-futu` | no | Not run. | — |
| `broker-google` | no | Not run. | — |
| `broker-ibkr` | no | Not run. | — |
| `broker-integration` | no | Not run. | — |
| `broker-longbridge` | no | Not run. | — |
| `broker-tiger` | no | Not run. | — |
| `broker-vbroker` | no | Not run. | — |
| `broker-webull` | no | Not run. | — |
| `change-review` | no | Not run. | — |
| `code-review` | no | Not run. | — |
| `compliance-regulatory` | no | Not run. | — |
| `data-engineering` | no | Not run. | — |
| `data-platforms` | yes | Run against a private production system whose data path is an operational streaming plane rather than a warehouse. Four anti-patterns added; the warehouse half of the prompt is still unverified. | 2026-09-29 |
| `database-design` | no | Not run. | — |
| `devops` | no | Not run. | — |
| `event-driven-architecture` | no | Not run. | — |
| `financial-docs` | no | Not run. | — |
| `frontend-dev` | no | Not run. | — |
| `graphql-development` | no | Not run. | — |
| `grpc-development` | no | Not run. | — |
| `incident-response` | no | Not run. | — |
| `jvm-backend` | no | Not run. No codebase with a JVM service layer was available for this pass, so there was nothing to run it against. | — |
| `llm-integration` | no | Not run. | — |
| `market-data-pipeline` | no | Not run. | — |
| `migration` | no | Not run. | — |
| `observability-sre` | no | Not run. | — |
| `orchestrate` | no | Not run. | — |
| `performance` | no | Not run. | — |
| `plan` | no | Not run. The prompt was rebuilt on the house structure in this pass, so its verification history resets: the text that was never run and the text here now are not the same prompt, and no run covers this one. | — |
| `platform-engineering` | yes | Run against two existing Kubernetes repositories. Three anti-patterns and one guardrail added. | 2026-09-29 |
| `portfolio-accounting` | no | Not run. | — |
| `quant-backtesting` | no | Not run. | — |
| `realtime-analytics` | no | Not run. | — |
| `sdk-build` | no | Not run. | — |
| `sdk-docs` | no | Not run. | — |
| `security` | no | Not run. | — |
| `testing` | no | Not run. | — |
| `trading-bot` | no | Not run. | — |
| `trading-risk` | no | Not run. | — |

`platform-engineering` shipped its run in 0.3.1; the other two are in
0.4.0.

## Why the published findings read the way they do

The two runs from this pass were read out of a private codebase, which is not
public and cannot be made public by publishing about it. Every finding was
therefore generalised before it was written down: the failure mode goes out,
the evidence stays in.

That is why the anti-patterns name a *contract*, a *shared definition* and a
*dependency* rather than the files they were found in, and why they carry no
identifier, no path and no count. A public file cannot be unpublished, so a
name that survives a generalisation is a pointer back to a codebase rather than
a finding — and a pointer is worth keeping private. The register can honestly
say a prompt was run and still refuse to say where.

What `scripts/check_no_fingerprint.py` catches, and the three things it
cannot, is stated once for contributors in
[CONTRIBUTING.md](../CONTRIBUTING.md#findings-travel-generalised) rather
than restated here. What no script could make, and what this pass did
instead, was reading each added line.

## What this pass did not do

- **Forty of the forty-three prompts have not been run.** The register
  records that plainly rather than rounding it up. Every row that says "not
  run" is an open item, not a verdict.
- **`jvm-backend` was skipped for want of a corpus.** No codebase with a JVM
  service layer was available for this pass, so there was nothing to run it
  against, and the gap is not closable by editing the prompt.
- **One prompt was verified against a corpus of a different kind.**
  `platform-engineering` was run against two public Kubernetes repositories
  rather than against a private codebase. That is a real run and it produced
  real findings, but it is not the same evidence as the other two rows, which
  is why the column above says what was run rather than only marking a tick.
- **A verified prompt can still have an unverified half.** `data-platforms` was
  run against a streaming system, so everything the prompt says about columnar
  storage, file formats and query planning has no evidence behind it and
  nothing was written about any of it. The absence of findings there is not
  coverage.

The register is meant to grow. Every prompt that gets a run gets a row, and
every run that finds something the prompt missed gets an anti-pattern — which
is the process the worked example shipped in the same release shows end to end,
including the part where review cut what the run produced.
