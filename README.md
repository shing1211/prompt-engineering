# Prompt Engineering Library

Agentic-AI prompts for software project delivery, built around **financial
trading systems**, **Go backend development**, and **AWS cloud
infrastructure**.

**42 prompts. ~86,000 words. MIT licensed.**

Browse the site: <https://shing1211.github.io/prompt-engineering/>

> **The site is frozen.** This repository is private, and GitHub Pages is
> only available for private repositories on a paid plan. The deployed site
> remains online and continues serving the last published build; the build
> workflow still runs on every push and will fail it if the site is broken,
> but it no longer deploys. Everything below is readable directly in the
> repository.

18 of the 42 prompts are language-agnostic: they assume no language-specific
tooling and apply as written, whichever stack you are on. The rest are written
against a specific language, and the [language table](prompts/index.md#browse-by-language)
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

Most prompt collections compete on breadth. This one has a **vertical
wedge**: 16 of the 42 prompts cover multi-broker trading systems, and no
other public library holds that ground.

The other 26 are the cross-cutting engineering practice that holds that domain
work together, and they are deliberately not Go-specific. Architecture, API
design, database design, code review, testing, security, performance, DevOps,
migration, observability, incident response, event-driven design, and data
engineering carry no language assumption at all.

That means material you will not find in a generic collection:

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

## Using a prompt

Clone and copy the file you want into your agent's configuration directory:

```bash
git clone https://github.com/shing1211/prompt-engineering.git
```

Then, depending on your harness:

| Harness | Location |
|---|---|
| OpenCode | `~/.config/opencode/agent/` (or `AGENTS.md` in the target repo) |
| Claude Code | `.claude/agents/` in the target repo |
| Codex | `AGENTS.md` in the target repo |

Start with [`orchestrate.md`](prompts/orchestrate.md) for multi-phase work
and [`plan.md`](prompts/plan.md) for planning. Both are designed to spawn
sub-agents so the main session stays small.

## Mode

Each prompt declares the mode it is meant to run in:

| Mode | Count | Use |
|---|---|---|
| `build` | 30 | Implementation, configuration, generation |
| `all` | 7 | Usable in any mode |
| `plan` | 1 | Planning and analysis only |
| `review` | 1 | Read and critique existing work |

## Browse

| Looking for | Start here |
|---|---|
| Start a new project | [orchestrate](prompts/orchestrate.md) |
| Plan the next phase | [plan](prompts/plan.md) |
| Build a broker SDK | [broker-integration](prompts/broker-integration.md), then the per-broker prompts |
| Wire up market data | [market-data-pipeline](prompts/market-data-pipeline.md) |
| Analyse the order book | [realtime-analytics](prompts/realtime-analytics.md) |
| Build a trading bot | [trading-bot](prompts/trading-bot.md) |
| Manage risk | [trading-risk](prompts/trading-risk.md) |
| Backtest a strategy | [quant-backtesting](prompts/quant-backtesting.md) |
| Track PnL and positions | [portfolio-accounting](prompts/portfolio-accounting.md) |
| Handle compliance | [compliance-regulatory](prompts/compliance-regulatory.md) |
| Design an API | [api-design](prompts/api-design.md) |
| Design a service boundary | [backend-services](prompts/backend-services.md) |
| Review code | [code-review](prompts/code-review.md) |
| Security audit | [security](prompts/security.md) |
| Set up CI/CD | [devops](prompts/devops.md) |
| Run infrastructure on Kubernetes | [platform-engineering](prompts/platform-engineering.md) |
| Build a data platform | [data-platforms](prompts/data-platforms.md) |
| Build a JVM service | [jvm-backend](prompts/jvm-backend.md) |
| Tune performance | [performance](prompts/performance.md) |

The [full index](prompts/index.md) lists all 38 with descriptions, and the
site has a searchable [tag index](prompts/tags.md) across 222 tags.

## Contributing

New prompts are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the
frontmatter contract, the review criteria, and the generator commands.

For a proposed prompt rather than a finished one, open an issue with the
**Prompt idea** form instead of a pull request.

## License

[MIT](LICENSE). Use them, fork them, adapt them.

Nothing in this repository is investment advice, and the trading prompts
build software — they do not place orders.
