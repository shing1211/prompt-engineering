---
title: Prompt Library
hide:
  - navigation
  - toc
---

# Prompt Library

System prompts for coding agents, across architecture, data, platform,
protocols, SDK, and financial engineering. 43 prompts: 27 cross-stack
engineering practice, 16 covering multi-broker trading systems.

Each prompt is a standalone system prompt with a declared mode
(`build`, `plan`, `review`, `all`) and a tag set. Copy one into your agent's
configuration, or read it first: the structure is deliberately consistent
across the library, so knowing one prompt tells you how the others are
organised.

`plan` and `review` prompts analyse without editing. `build` prompts are
licensed to write code. For multi-area work, start with
[orchestrate](orchestrate.md), which spawns a sub-agent per area so the main
session holds a plan rather than a transcript.

Not every prompt here has been run against a real codebase. The `Verified`
column in the tables below says which have, and the
[verification register](https://github.com/shing1211/prompt-engineering/blob/main/docs/verification.md)
is the record behind it — including which prompts have not been run, why one of
them could not be, and which one was checked against a corpus of a different
kind from the rest.

Browse the categories below, or jump to the [full tag index](tags.md).

<!-- BEGIN GENERATED TABLES -->

## Browse by Category

### Orchestration and Planning

Multi-phase sub-agent execution and project planning — 2 prompt(s).

| Prompt | Mode | Description | Verified |
|---|---|---|---|
| [`orchestrate.md`](orchestrate.md) — Orchestrator | build | Orchestrate multi-phase implementation using sub-agents with specialist roles (backend, frontend, data, devops, security, tester, docs, reviewer, release, architect, planner) | not verified |
| [`plan.md`](plan.md) — Planning | plan | Turn a change request into an ordered plan whose units each end in a check that can fail, and dispatch per-area sub-agents so the session holds a plan rather than a transcript | not verified |

### Architecture and Engineering

Cross-cutting engineering practice — 13 prompt(s).

| Prompt | Mode | Description | Verified |
|---|---|---|---|
| [`api-design.md`](api-design.md) — API Design | all | Design REST, GraphQL, and gRPC APIs with OpenAPI specs, versioning strategies, authentication, rate limiting, pagination, filtering, and error handling | not verified |
| [`architecture.md`](architecture.md) — Architecture Design | all | Design system architecture for scalability, reliability, and maintainability covering microservices, event-driven patterns, caching, load balancing, and data consistency | not verified |
| [`backend-services.md`](backend-services.md) — Backend Services | all | Design backend services without a language assumption, covering boundaries, idempotency, consistency, versioning, and the failure modes of distributed systems | [verified](https://github.com/shing1211/prompt-engineering/blob/main/docs/verification.md) |
| [`change-review.md`](change-review.md) — Change Review | review | Review a single change against what it claims to do, what the diff actually does, and what its callers depend on | not verified |
| [`code-review.md`](code-review.md) — Code Review | review | Conduct comprehensive code review for correctness, security, performance, maintainability, and best practices across all major languages | not verified |
| [`database-design.md`](database-design.md) — Database Design | all | Design database schemas, migrations, indexing strategies, query optimization, and multi-tenant architecture for relational and NoSQL databases | not verified |
| [`devops.md`](devops.md) — DevOps | all | Design and implement CI/CD pipelines, Docker/Kubernetes configurations, Infrastructure as Code, and deployment strategies (blue-green, canary, rolling) | not verified |
| [`incident-response.md`](incident-response.md) — Incident Response | all | Design incident response runbooks, on-call procedures, postmortem templates, and alerting strategies for production systems | not verified |
| [`migration.md`](migration.md) — Migration | build | Migration guide for zero-downtime database migrations with Flyway/Liquibase, monolith to microservices refactoring, language upgrades, Infrastructure as Code with Terraform, and blue-green deployments on AWS | not verified |
| [`observability-sre.md`](observability-sre.md) — Observability and SRE | build | Design observability and SRE practices for financial platforms with OpenTelemetry, SLOs, incident response, capacity planning, and production diagnostics | not verified |
| [`performance.md`](performance.md) — Performance | build | Performance optimization guide covering Go pprof/async-profiler, Python py-spy/cProfile, k6 load testing, PostgreSQL EXPLAIN ANALYZE, Redis caching, numba/cython optimization, and Core Web Vitals for frontend | not verified |
| [`security.md`](security.md) — Security | all | Security engineering guide covering OWASP Top 10, SAST/DAST scanning, secrets management with AWS Secrets Manager, threat modeling (STRIDE), penetration testing, and secure coding practices for Go and Python | not verified |
| [`testing.md`](testing.md) — Testing | all | Design comprehensive testing strategies covering unit tests, integration tests, e2e tests, fuzz testing, property-based testing, and test automation with coverage gates | not verified |

### Application Development

Frontend, LLM, events, and data pipelines — 4 prompt(s).

| Prompt | Mode | Description | Verified |
|---|---|---|---|
| [`data-engineering.md`](data-engineering.md) — Data Engineering | build | Build data engineering pipelines with Apache Airflow/Prefect, Kafka/Flink streaming, Debezium CDC, dbt transformations, MSK/S3 data lake, Great Expectations data quality, and AWS Glue/Athena | not verified |
| [`event-driven-architecture.md`](event-driven-architecture.md) — Event-Driven Architecture | build | Design event-driven financial systems with Kafka, schema evolution, CQRS, event sourcing, ordering, replay, deduplication, and resilient asynchronous workflows | not verified |
| [`frontend-dev.md`](frontend-dev.md) — Frontend Development | build | Frontend development guide with React 18, Next.js 14 App Router, Zustand state management, shadcn/ui + Tailwind CSS, TanStack Query, Core Web Vitals, accessibility, and Vitest/Playwright testing | not verified |
| [`llm-integration.md`](llm-integration.md) — LLM Integration | build | LLM integration guide with RAG architecture, vector databases (Pinecone/Milvus), prompt engineering, vLLM/Ollama local deployment, AI safety, RAG evaluation with RAGAS, and cloud API integration (OpenAI, Anthropic, Google Gemini) | not verified |

### Platform and Infrastructure

Kubernetes, packaging, delivery, and operability — 1 prompt(s).

| Prompt | Mode | Description | Verified |
|---|---|---|---|
| [`platform-engineering.md`](platform-engineering.md) — Platform Engineering | build | Build and operate Kubernetes infrastructure with Helm, GitOps, Terraform, progressive delivery, and the failure modes of agent-written infrastructure | [verified](https://github.com/shing1211/prompt-engineering/blob/main/docs/verification.md) |

### API Protocols

GraphQL and gRPC specifics — 2 prompt(s).

| Prompt | Mode | Description | Verified |
|---|---|---|---|
| [`graphql-development.md`](graphql-development.md) — GraphQL Development | build | GraphQL development guide with Apollo Server 4, DataLoader for N+1 problem, Apollo Federation for microservices, graphql-ws subscriptions, schema registry, and performance optimization (persisted queries, APQ) | not verified |
| [`grpc-development.md`](grpc-development.md) — gRPC Development | build | gRPC development guide with Protobuf v3, buf CLI for modern protobuf tooling, Go grpc-go, gRPC-gateway for REST-to-gRPC, Envoy proxy, Istio service mesh, and streaming RPC patterns | not verified |

### SDK Development

Reusable patterns for building and documenting SDKs — 2 prompt(s).

| Prompt | Mode | Description | Verified |
|---|---|---|---|
| [`sdk-build.md`](sdk-build.md) — SDK Build | build | Build an enterprise-grade Go SDK for a financial broker (Account, Market Data, Trading, Positions) with phases covering infrastructure, domain models, WebSocket streaming, observability, and rigorous testing | not verified |
| [`sdk-docs.md`](sdk-docs.md) — SDK Documentation | build | Improve all Markdown documentation in an API SDK repository | not verified |

### Data Platforms

Lakehouse, contracts, and data quality — 1 prompt(s).

| Prompt | Mode | Description | Verified |
|---|---|---|---|
| [`data-platforms.md`](data-platforms.md) — Data Platforms | build | Build lakehouse and streaming data platforms with data contracts, late-arriving data handling, lineage, quality gates, and cost control | [verified](https://github.com/shing1211/prompt-engineering/blob/main/docs/verification.md) |

### JVM and Java

Spring Boot, Quarkus, and the JVM — 1 prompt(s).

| Prompt | Mode | Description | Verified |
|---|---|---|---|
| [`jvm-backend.md`](jvm-backend.md) — JVM Backend | build | Build JVM backend services with Spring Boot, Quarkus, or Micronaut compared against each other, covering persistence, concurrency, testing, and JVM-specific operational concerns | not verified |

### Documentation

Documentation workflows — 1 prompt(s).

| Prompt | Mode | Description | Verified |
|---|---|---|---|
| [`financial-docs.md`](financial-docs.md) — Financial Platform Documentation | build | Improve all Markdown documentation in a unified multi-broker trading and portfolio management system | not verified |

### Financial Engineering — Trading and Broking

Trading systems, market data, risk, quant, and compliance — 9 prompt(s).

| Prompt | Mode | Description | Verified |
|---|---|---|---|
| [`broker-certification.md`](broker-certification.md) — Broker Certification | build | Certify multi-broker trading integrations through sandbox testing, capability conformance, contract tests, paper trading, reconciliation, and production go-live controls | not verified |
| [`broker-integration.md`](broker-integration.md) — Broker Integration | build | Build a unified multi-broker abstraction layer for Longbridge, Tiger Trade, Webull, IBKR Client Portal Web API, Futu OpenD, and Hua Sing Tong vbroker with HMAC auth, consolidated L2 market data, and AWS Secrets Manager integration | not verified |
| [`compliance-regulatory.md`](compliance-regulatory.md) — Compliance and Regulatory | build | Design regulatory compliance and control systems for financial trading platforms covering best execution, surveillance, audit trails, retention, and multi-jurisdiction requirements | not verified |
| [`market-data-pipeline.md`](market-data-pipeline.md) — Market Data Pipeline | build | Build real-time market data pipelines from 6 brokers (Longbridge, Tiger, Webull, IBKR, Futu, vbroker) into MSK, Redis, and S3 with consolidated L2 tape, corporate actions handling, and Athena analytics | not verified |
| [`portfolio-accounting.md`](portfolio-accounting.md) — Portfolio Accounting | build | Build portfolio accounting and reconciliation systems for multi-broker trading platforms covering positions, PnL, corporate actions, FX, settlement, and multi-currency precision | not verified |
| [`quant-backtesting.md`](quant-backtesting.md) — Quant Backtesting | build | Build quant backtesting frameworks in Python using backtrader/vectorbt, IBKR Client Portal Web API for historical data, alpha research with factor models (momentum, value, carry), walk-forward validation, and performance attribution | not verified |
| [`realtime-analytics.md`](realtime-analytics.md) — Real-Time Analytics | build | Build real-time analytics for trading with L2 order book reconstruction, VPIN/order flow imbalance, volume profiling, tick feature engineering, arbitrage detection, and both Redis streaming and S3/Athena long-term storage | not verified |
| [`trading-bot.md`](trading-bot.md) — Trading Bot | build | Build an event-driven trading bot in Go with state machine design, algorithmic execution strategies (TWAP/VWAP/Grid/Market-making), Kelly criterion position sizing, paper/live trading modes, and kill switch | not verified |
| [`trading-risk.md`](trading-risk.md) — Trading Risk | build | Design real-time intraday risk management for trading bots with VaR/CVaR calculation, drawdown controls, margin call handling, Greeks monitoring, kill switch, and AWS CloudWatch dashboards | not verified |

### Broker SDKs

One prompt per broker, each a production Go SDK build — 7 prompt(s).

| Prompt | Mode | Description | Verified |
|---|---|---|---|
| [`broker-futu.md`](broker-futu.md) — Futu OpenD SDK | build | Build a production-grade Go SDK for Futu OpenD (proprietary binary protocol with L2 market data and trading services) with secure local connectivity, resilience, CI/CD, fuzz testing, and enterprise hardening | not verified |
| [`broker-google.md`](broker-google.md) — Generic HMAC Broker SDK | build | Build a production-grade Go SDK for a multi-asset financial broker API with HMAC auth, REST, WebSocket, and circuit breaker resilience patterns | not verified |
| [`broker-ibkr.md`](broker-ibkr.md) — IBKR Client Portal SDK | build | Build a production-grade Go SDK for the Interactive Brokers Web API (Client Portal REST + WebSocket streaming) with resilient sessions, order safety, CI/CD, fuzz testing, and enterprise hardening | not verified |
| [`broker-longbridge.md`](broker-longbridge.md) — Longbridge SDK | build | Build a production-grade Go SDK for Longbridge OpenAPI (REST + WebSocket quotes and trading streams) with token security, multi-market trading, CI/CD, fuzz testing, and enterprise hardening | not verified |
| [`broker-tiger.md`](broker-tiger.md) — Tiger Trade SDK | build | Build a production-grade Go SDK for Tiger Trade OpenAPI (REST + WebSocket market data and trading events) with private-key authentication, order safety, CI/CD, fuzz testing, and enterprise hardening | not verified |
| [`broker-vbroker.md`](broker-vbroker.md) — Hua Sing Tong vbroker SDK | build | Build a production-grade Go SDK for Hua Sing Tong vbroker Open API (HMAC REST + WebSocket market data and trading events) with HK market support, order safety, CI/CD, fuzz testing, and enterprise hardening | not verified |
| [`broker-webull.md`](broker-webull.md) — Webull SDK | build | Build a production-grade Go SDK for the Webull OpenAPI (REST + MQTT market data + gRPC order pushes) with CI/CD, fuzz testing, and enterprise hardening | not verified |

## Browse by Technology

| Technology | Prompts |
|---|---|
| Go / Golang | [broker-futu](broker-futu.md), [broker-google](broker-google.md), [broker-ibkr](broker-ibkr.md), [broker-integration](broker-integration.md), [broker-longbridge](broker-longbridge.md), [broker-tiger](broker-tiger.md), [broker-vbroker](broker-vbroker.md), [broker-webull](broker-webull.md), [grpc-development](grpc-development.md), [market-data-pipeline](market-data-pipeline.md), [performance](performance.md), [portfolio-accounting](portfolio-accounting.md), [realtime-analytics](realtime-analytics.md), [sdk-build](sdk-build.md), [security](security.md), [trading-bot](trading-bot.md), [trading-risk](trading-risk.md) |
| Python | [data-engineering](data-engineering.md), [data-platforms](data-platforms.md), [llm-integration](llm-integration.md), [market-data-pipeline](market-data-pipeline.md), [performance](performance.md), [quant-backtesting](quant-backtesting.md), [realtime-analytics](realtime-analytics.md), [security](security.md) |
| TypeScript | [frontend-dev](frontend-dev.md), [graphql-development](graphql-development.md) |
| AWS | [broker-integration](broker-integration.md), [data-platforms](data-platforms.md), [migration](migration.md), [platform-engineering](platform-engineering.md), [trading-bot](trading-bot.md), [trading-risk](trading-risk.md) |
| Kafka / MSK | [data-engineering](data-engineering.md), [event-driven-architecture](event-driven-architecture.md), [market-data-pipeline](market-data-pipeline.md) |
| Redis | [market-data-pipeline](market-data-pipeline.md), [performance](performance.md), [realtime-analytics](realtime-analytics.md) |
| PostgreSQL | [database-design](database-design.md), [migration](migration.md) |
| React / Next.js | [frontend-dev](frontend-dev.md) |
| GraphQL / Apollo | [api-design](api-design.md), [graphql-development](graphql-development.md) |
| gRPC / Protobuf | [api-design](api-design.md), [broker-webull](broker-webull.md), [grpc-development](grpc-development.md) |
| Kubernetes | [devops](devops.md), [platform-engineering](platform-engineering.md) |
| Terraform | [devops](devops.md), [migration](migration.md), [platform-engineering](platform-engineering.md) |
| CI/CD | [broker-futu](broker-futu.md), [broker-ibkr](broker-ibkr.md), [broker-longbridge](broker-longbridge.md), [broker-tiger](broker-tiger.md), [broker-vbroker](broker-vbroker.md), [broker-webull](broker-webull.md), [devops](devops.md), [platform-engineering](platform-engineering.md) |
| Security | [code-review](code-review.md), [security](security.md) |
| Testing | [frontend-dev](frontend-dev.md), [jvm-backend](jvm-backend.md), [testing](testing.md) |
| LLM / RAG | [llm-integration](llm-integration.md) |
| Market data | [broker-futu](broker-futu.md), [broker-longbridge](broker-longbridge.md), [broker-tiger](broker-tiger.md), [broker-vbroker](broker-vbroker.md), [market-data-pipeline](market-data-pipeline.md) |
| Trading | [broker-certification](broker-certification.md), [broker-futu](broker-futu.md), [financial-docs](financial-docs.md), [portfolio-accounting](portfolio-accounting.md), [sdk-build](sdk-build.md) |
| Compliance | [compliance-regulatory](compliance-regulatory.md) |
| Go SDK | [broker-futu](broker-futu.md), [broker-google](broker-google.md), [broker-ibkr](broker-ibkr.md), [broker-longbridge](broker-longbridge.md), [broker-tiger](broker-tiger.md), [broker-vbroker](broker-vbroker.md), [broker-webull](broker-webull.md), [sdk-build](sdk-build.md), [sdk-docs](sdk-docs.md) |

## Browse by Language

Prompts written against a specific language's tooling. Everything not listed here assumes no language-specific tooling and applies as written.

| Language | Prompts |
|---|---|
| Go | [broker-futu](broker-futu.md), [broker-google](broker-google.md), [broker-ibkr](broker-ibkr.md), [broker-integration](broker-integration.md), [broker-longbridge](broker-longbridge.md), [broker-tiger](broker-tiger.md), [broker-vbroker](broker-vbroker.md), [broker-webull](broker-webull.md), [grpc-development](grpc-development.md), [market-data-pipeline](market-data-pipeline.md), [performance](performance.md), [portfolio-accounting](portfolio-accounting.md), [realtime-analytics](realtime-analytics.md), [sdk-build](sdk-build.md), [security](security.md), [trading-bot](trading-bot.md), [trading-risk](trading-risk.md) |
| Python | [data-engineering](data-engineering.md), [data-platforms](data-platforms.md), [llm-integration](llm-integration.md), [market-data-pipeline](market-data-pipeline.md), [performance](performance.md), [quant-backtesting](quant-backtesting.md), [realtime-analytics](realtime-analytics.md), [security](security.md) |
| TypeScript | [frontend-dev](frontend-dev.md), [graphql-development](graphql-development.md) |
| Java / JVM | [jvm-backend](jvm-backend.md) |
| **Any stack** | [api-design](api-design.md), [architecture](architecture.md), [backend-services](backend-services.md), [broker-certification](broker-certification.md), [change-review](change-review.md), [code-review](code-review.md), [compliance-regulatory](compliance-regulatory.md), [database-design](database-design.md), [devops](devops.md), [event-driven-architecture](event-driven-architecture.md), [financial-docs](financial-docs.md), [incident-response](incident-response.md), [migration](migration.md), [observability-sre](observability-sre.md), [orchestrate](orchestrate.md), [plan](plan.md), [platform-engineering](platform-engineering.md), [sdk-docs](sdk-docs.md), [testing](testing.md) |

## Quick Reference

| Task | Prompt |
|---|---|
| Design an API | [`api-design.md`](api-design.md) |
| Set up CI/CD | [`devops.md`](devops.md) |
| Review code | [`code-review.md`](code-review.md) |
| Security audit | [`security.md`](security.md) |
| Design a database | [`database-design.md`](database-design.md) |
| Build a trading bot | [`trading-bot.md`](trading-bot.md) |
| Wire up market data | [`market-data-pipeline.md`](market-data-pipeline.md) |
| Manage risk | [`trading-risk.md`](trading-risk.md) |
| Backtest a strategy | [`quant-backtesting.md`](quant-backtesting.md) |
| Track PnL and positions | [`portfolio-accounting.md`](portfolio-accounting.md) |
| Tune performance | [`performance.md`](performance.md) |
| Write tests | [`testing.md`](testing.md) |
| Plan a migration | [`migration.md`](migration.md) |
| Set up observability | [`observability-sre.md`](observability-sre.md) |
| Handle an incident | [`incident-response.md`](incident-response.md) |
| Integrate an LLM | [`llm-integration.md`](llm-integration.md) |
| Build a data pipeline | [`data-engineering.md`](data-engineering.md) |

## Statistics

| Metric | Count |
|---|---|
| **Total prompts** | 43 |
| **Orchestration and Planning** | 2 |
| **Architecture and Engineering** | 13 |
| **Application Development** | 4 |
| **Platform and Infrastructure** | 1 |
| **API Protocols** | 2 |
| **SDK Development** | 2 |
| **Data Platforms** | 1 |
| **JVM and Java** | 1 |
| **Documentation** | 1 |
| **Financial Engineering — Trading and Broking** | 9 |
| **Broker SDKs** | 7 |
| **Distinct tags** | 246 |
| **Language-agnostic** | 19 |
| **Verified** | 3 |
| **Mode: all** | 8 |
| **Mode: build** | 32 |
| **Mode: plan** | 1 |
| **Mode: review** | 2 |

<!-- END GENERATED TABLES -->

---

## Contributing

Prompts are added as files under `prompts/` with the frontmatter contract
below. Run the two generators, then open a pull request.

```yaml
---
title: Display Name
description: One line, shown in index tables and search results
mode: build # build | plan | review | all
model: any
category: architecture
tags: ["lowercase", "kebab-case"]
---
```

| Field | Rule |
|---|---|
| `title` | Display name. Must match the file's H1. |
| `description` | One line. No trailing period. |
| `mode` | One of `build`, `plan`, `review`, `all`. |
| `model` | `any`, or a pinned model ID. Default to `any`. |
| `category` | Must be a key in `scripts/apply_categories.py`. |
| `tags` | Lowercase kebab-case. Reuse existing tags where one fits. |

Adding a prompt touches three files: the prompt itself, its `title` and
`category` entries in the two generator scripts, and an entry in the `nav:`
block of `mkdocs.yml`. Skipping the nav entry is the easy mistake, because
MkDocs still builds an unlisted page — it just never appears in the sidebar.

```bash
python3 scripts/apply_titles.py           # frontmatter title + H1
python3 scripts/apply_categories.py       # category key
python3 scripts/fix_heading_hierarchy.py  # one H1 per document
python3 scripts/generate_index.py         # tables in this file
scripts/validate.sh                       # schema, nav, links, lint
```

CI runs the same checks, so a stale `index.md`, a malformed frontmatter
block, or a prompt missing from the nav fails the pull request rather than
reaching the site.

See [CONTRIBUTING.md](https://github.com/shing1211/prompt-engineering/blob/main/CONTRIBUTING.md)
for the full review criteria.
