# Prompt Engineering Library

System prompts for coding agents. **45 prompts** across architecture, data,
platform, protocols, SDK, documentation, and financial engineering — written to
be dropped into a harness and run against a real repository.

**45 prompts. ~94,000 words. MIT licensed.**

Browse the site: <https://shing1211.github.io/prompt-engineering/>

Built for anyone wiring an agent into a codebase: the prompts, the anti-patterns
they exist to prevent, and the definition of done each one enforces. 21 of the
45 are language-agnostic and apply as written on any stack; the rest name the
tooling they assume, and the [language table](prompts/index.md#browse-by-language)
tells you which is which.

---

## What this is

Each file in `prompts/` is a complete, standalone system prompt. Not a
snippet, not a template with holes to fill: an agent persona, the context it
loads, a working checklist, explicit anti-patterns, and a delivery contract
that defines what "done" means for the task.

They are written to be dropped into an agent harness (OpenCode, Claude Code,
Codex, or any harness that takes a system prompt) and run against a real
repository.

### The shape of a prompt

Every prompt follows the same layered structure, so once you have read one,
you know how the rest are organised:

| Layer | Purpose |
|---|---|
| Identity and core principles | Who the agent is, and the rules it cannot break |
| Project context | Which repository files to load before acting |
| Checklist or blueprint | The domain-specific work, itemised |
| Anti-patterns | What the agent must never do, stated explicitly |
| Guardrails and validation | How to verify its own output |
| Delivery contract | The definition of done for the task |

## What makes this library different

Most prompt collections are a flat list of personas. Each prompt here is a
**build spec**: it enumerates the work, names the failure modes it must avoid,
and defines the contract the agent has to satisfy before it is finished. The
anti-patterns and guardrails are the substance, not an appendix — they are
enforced by a check in CI, so a prompt that drops them fails the build.

Coverage spans eight areas:

| Area | Prompts | Examples |
|---|---|---|
| Architecture and engineering | 15 | service boundaries, API design, database design, testing, security, performance |
| Application development | 4 | event-driven design, frontend, data engineering, LLM integration |
| Protocols | 2 | gRPC, GraphQL |
| SDK authoring | 2 | building a client library, documenting one |
| Orchestration | 2 | multi-phase dispatch, planning |
| Platform, data, Java, docs | 4 | Kubernetes, data platforms, JVM services, documentation |

### The financial-engineering wedge

16 of the 45 prompts cover multi-broker trading, and no other public library
holds that ground. They are also the hardest prompts here to write, which
makes them the best test of whether a prompt library is any good:

- **Broker SDKs**, one prompt per venue — Longbridge, Tiger Trade, Webull,
  IBKR Client Portal, Futu OpenD, Hua Sing Tong vbroker, plus a generic HMAC
  pattern. Each is a full production build spec: auth, streaming, order
  safety, CI/CD, fuzz testing, enterprise hardening.
- **The consolidated tape** — six brokers into one L2 order book, with
  corporate actions, MSK, Redis, and Athena behind it.
- **Market microstructure** — VPIN, order flow imbalance, volume profiling,
  arbitrage detection.
- **Trading risk** — intraday VaR/CVaR, drawdown controls, margin calls,
  Greeks, kill switch, CloudWatch dashboards.
- **Money correctness** — multi-currency PnL precision, corporate actions,
  settlement, reconciliation.
- **Regulation** — MiFID II best execution, trade surveillance, audit
  trails, retention across SFC, SEC, and FINRA.

These are prompts for building trading software. They do not place orders, and
nothing in this repository is investment advice.

## Using a prompt

These are **system prompts**, not user prompts. The distinction matters: a
system prompt sets the agent's identity and rules for the whole session, so
pick the one that matches the task and start a session with it, rather than
pasting it as a one-off question.

### Install as agents

Every prompt is also published as a **named agent** for the three harnesses
that support them. Clone once, copy the directory your harness reads, and all
of them are available to invoke:

```bash
git clone https://github.com/shing1211/prompt-engineering.git
cd prompt-engineering
```

| Harness | Copy this into your project | Invoke one |
|---|---|---|
| OpenCode | `.opencode/agents/` | `@prompt-code-review` |
| Claude Code | `.claude/agents/` | `prompt-code-review` |
| Codex | `.agents/skills/` | `$prompt-code-review` |

Use `cp -r` to copy the files, or `ln -s` to symlink the directory so a
`git pull` updates your agents in place. Copying one directory is enough —
the agents carry their full text and do not read from `prompts/` at runtime.

On Windows, prefer the copy. Symlinks there need either Developer Mode or
administrator rights, and without them `ln -s` writes a text file containing
the target path, which a harness then reads as a broken prompt. `mkdocs` has
the same trap for this repository's own documents, so it is a known shape
rather than a new one.

Agent names are the prompt file name with a `prompt-` prefix:
`prompts/broker-futu.md` is the agent `prompt-broker-futu` in all three
harnesses. The prefix is a namespace, not decoration — without it
`plan.md` would produce an agent called `plan`, and both OpenCode and Claude
Code ship a built-in by that name, which the generated file would replace.

**What the `mode` field does at install time.** `plan` and `review` prompts
are generated with a write restriction rather than merely documented as
non-mutating, and the strength of that restriction is not the same everywhere:

| Harness | How the restriction is expressed |
|---|---|
| OpenCode | `permission: edit: deny` while `bash` stays available — enforced |
| Claude Code | a `tools` allow-list without Write or Edit — enforced for file edits, but a shell command can still write, as with any Claude Code agent |
| Codex | skills have no permission field, so the prompt's own guardrails are the only control |

If you are on OpenCode 2.x rather than 1.x, the generated `permission:` block
uses the 1.x syntax and will be ignored; the agents still load, they just do
not carry the restriction until the generator is updated for 2.x.

### Reading a prompt directly

You do not have to install anything to use this library. `prompts/*.md` is the
source these agents are generated from, and it is the canonical version: a
generated agent is a verbatim copy, so the two never disagree.

| Harness | Location |
|---|---|
| OpenCode | `~/.config/opencode/agents/` (or `AGENTS.md` in the target repo) |
| Claude Code | `.claude/agents/` in the target repo |
| Codex | `AGENTS.md` in the target repo, or `.agents/skills/` for a named skill |

### Choosing one

Use the `mode` field to filter first — it tells you what the agent is allowed
to do:

| Mode | Count | Use |
|---|---|---|
| `build` | 32 | Implementation, configuration, generation |
| `all` | 8 | Usable in any mode |
| `plan` | 1 | Planning and analysis only |
| `review` | 4 | Read and critique existing work |

`plan` and `review` are non-mutating: they analyse and report without editing.
A `plan` or `review` prompt may run the acceptance command, a test suite, or
any other read-only check; it may not edit source, fixtures, or generated
files. Running is allowed, writing is not — a review that changes the tree it
was sent to read cannot be re-read, and the next reviewer cannot tell what it
changed. Anything in `build` is licensed to write code.

### Composing several

For work that spans more than one area, [`orchestrate.md`](prompts/orchestrate.md)
is the entry point. It is built to spawn sub-agents, one per area, so the main
session holds a plan rather than a transcript — which is the pattern that keeps
context small enough to finish. [`plan.md`](prompts/plan.md) does the same for
the planning phase.

The usual composition is a `plan` pass, then per-area `build` prompts, then
[`code-review.md`](prompts/code-review.md) on the result.

## Browse

| Looking for | Start here |
|---|---|
| Start a new project | [orchestrate](prompts/orchestrate.md) |
| Plan the next phase | [plan](prompts/plan.md) |
| Design an API | [api-design](prompts/api-design.md) |
| Design a service boundary | [backend-services](prompts/backend-services.md) |
| Design a schema | [database-design](prompts/database-design.md) |
| Review code | [code-review](prompts/code-review.md) |
| Review a change | [change-review](prompts/change-review.md) |
| Review a plan | [plan-review](prompts/plan-review.md) |
| Review tests | [test-review](prompts/test-review.md) |
| Write tests | [testing](prompts/testing.md) |
| Security audit | [security](prompts/security.md) |
| Tune performance | [performance](prompts/performance.md) |
| Set up CI/CD | [devops](prompts/devops.md) |
| Run infrastructure on Kubernetes | [platform-engineering](prompts/platform-engineering.md) |
| Debug an outage | [incident-response](prompts/incident-response.md) |
| Set up tracing and alerts | [observability-sre](prompts/observability-sre.md) |
| Move a system to a new stack | [migration](prompts/migration.md) |
| Build a data platform | [data-platforms](prompts/data-platforms.md) |
| Build a frontend | [frontend-dev](prompts/frontend-dev.md) |
| Design events | [event-driven-architecture](prompts/event-driven-architecture.md) |
| Build a gRPC service | [grpc-development](prompts/grpc-development.md) |
| Build a GraphQL gateway | [graphql-development](prompts/graphql-development.md) |
| Build a client library | [sdk-build](prompts/sdk-build.md) |
| Document a library | [sdk-docs](prompts/sdk-docs.md) |
| Build a JVM service | [jvm-backend](prompts/jvm-backend.md) |
| Build a broker SDK | [broker-integration](prompts/broker-integration.md), then the per-broker prompts |
| Wire up market data | [market-data-pipeline](prompts/market-data-pipeline.md) |
| Analyse the order book | [realtime-analytics](prompts/realtime-analytics.md) |
| Build a trading bot | [trading-bot](prompts/trading-bot.md) |
| Manage risk | [trading-risk](prompts/trading-risk.md) |
| Backtest a strategy | [quant-backtesting](prompts/quant-backtesting.md) |
| Track PnL and positions | [portfolio-accounting](prompts/portfolio-accounting.md) |
| Handle compliance | [compliance-regulatory](prompts/compliance-regulatory.md) |

The [full index](prompts/index.md) lists all 45 with descriptions, and the
site has a searchable [tag index](prompts/tags.md) across 251 tags.

## Contributing

New prompts are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the
frontmatter contract, the review criteria, and the generator commands.

For a proposed prompt rather than a finished one, open an issue with the
**Prompt idea** form instead of a pull request.

## License

[MIT](LICENSE). Use them, fork them, adapt them.
