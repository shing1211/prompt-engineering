# Prompt Library

Comprehensive collection of prompts for IT software project development, specializing in **financial trading systems**, **Go backend development**, and **AWS cloud infrastructure**.

---

## Browse by Category

### Orchestration & Planning

| File | Description | Mode | Tags |
|------|-------------|------|------|
| `orchestrate.md` | Multi-phase sub-agent orchestration with specialist roles (backend, frontend, data, devops, security, tester, docs, reviewer, release, architect, planner) | build | orchestration, sub-agent, build, plan |
| `plan.md` | Project planning prompts for next-phase roadmapping, code enhancements, bug fixes, and architecture improvements | plan | planning, roadmap, enhancement |

### Financial Domain — Trading & Broking

| File | Description | Mode | Tags |
|------|-------------|------|------|
| `broker-integration.md` | Unified multi-broker abstraction for Longbridge, Tiger, Webull, IBKR Client Portal, Futu OpenD, and Hua Sing Tong vbroker with HMAC auth, consolidated L2 tape, and AWS Secrets Manager | build | broker, longbridge, tiger-trade, webull, ibkr, futu, vbroker, hmac, websocket, aws |
| `broker-webull.md` | Production-grade Go SDK for Webull HK OpenAPI (REST + MQTT market data + gRPC order pushes) with CI/CD, fuzz testing, and enterprise hardening | build | sdk, go, webull, mqtt, grpc, rest, ci-cd, fuzz-testing |
| `broker-ibkr.md` | Production-grade Go SDK for IBKR Client Portal Web API (REST + WebSocket) with session security, order safety, CI/CD, fuzz testing, and enterprise hardening | build | sdk, go, ibkr, interactive-brokers, client-portal, rest, websocket, ci-cd, fuzz-testing |
| `broker-tiger.md` | Production-grade Go SDK for Tiger Trade OpenAPI (REST + WebSocket) with private-key authentication, order safety, CI/CD, fuzz testing, and enterprise hardening | build | sdk, go, tiger-trade, tiger-openapi, rest, websocket, market-data, ci-cd, fuzz-testing |
| `broker-longbridge.md` | Production-grade Go SDK for Longbridge OpenAPI (REST + WebSocket) with token security, multi-market trading, CI/CD, fuzz testing, and enterprise hardening | build | sdk, go, longbridge, openapi, rest, websocket, market-data, hkex, ci-cd, fuzz-testing |
| `broker-futu.md` | Production-grade Go SDK for Futu OpenD (proprietary binary protocol with L2 market data and trading services) with secure local connectivity, CI/CD, fuzz testing, and enterprise hardening | build | sdk, go, futu, opend, binary-protocol, market-data, l2, trading, ci-cd, fuzz-testing |
| `broker-vbroker.md` | Production-grade Go SDK for Hua Sing Tong vbroker Open API (HMAC REST + WebSocket) with HK market support, order safety, CI/CD, fuzz testing, and enterprise hardening | build | sdk, go, vbroker, hua-sing-tong, hmac, rest, websocket, hkex, market-data, ci-cd, fuzz-testing |
| `compliance-regulatory.md` | Regulatory compliance and control systems for financial trading platforms covering best execution, surveillance, audit trails, retention, and multi-jurisdiction requirements | build | compliance, regulatory, mifid-ii, sec, finra, hkex, sfc, best-execution, trade-surveillance, audit |
| `portfolio-accounting.md` | Portfolio accounting and reconciliation for multi-broker trading platforms covering positions, PnL, corporate actions, FX, settlement, and multi-currency precision | build | portfolio, accounting, pnl, reconciliation, settlement, corporate-actions, multi-currency, trading, go |
| `broker-certification.md` | Multi-broker certification through sandbox testing, capability conformance, contract tests, paper trading, reconciliation, and production go-live controls | build | broker, certification, sandbox, paper-trading, conformance, contract-testing, go-live, trading |
| `broker-google.md` | Production-grade Go SDK for Google-style multi-asset broker API with HMAC auth, REST, WebSocket, and circuit breaker resilience patterns | build | sdk, go, financial, broker, hmac, rest, websocket, resilience |
| `financial-docs.md` | DocSmith-FinOps — Financial system documentation improvement with multi-broker abstraction clarity, event-driven architecture transparency, and regulatory compliance | build | documentation, financial, trading, portfolio, broker, event-driven |
| `market-data-pipeline.md` | Real-time market data pipeline from 6 brokers into MSK, Redis, and S3 with consolidated L2 tape, corporate actions handling, and Athena analytics | build | market-data, kafka, msk, redis, s3, athena, consolidated-tape, order-book, golang, python |
| `quant-backtesting.md` | Python backtesting framework using backtrader/vectorbt with IBKR Client Portal data, factor models (momentum, value, carry), walk-forward validation, and performance attribution | build | quant, backtesting, python, backtrader, vectorbt, ibkr, factor-models, alpha-research, walk-forward |
| `realtime-analytics.md` | Real-time analytics for trading with L2 order book, VPIN, order flow imbalance, volume profiling, tick feature engineering, arbitrage detection, and Redis + S3/Athena storage | build | realtime-analytics, golang, python, order-book, vpin, order-flow, arbitrage, athena, market-microstructure |
| `trading-bot.md` | Event-driven trading bot in Go with state machine design, TWAP/VWAP/Grid/Market-making strategies, Kelly criterion position sizing, paper/live modes, and kill switch | build | trading-bot, golang, event-driven, state-machine, twap, vwap, grid-trading, market-making, kelly-criterion |
| `trading-risk.md` | Real-time intraday risk management with VaR/CVaR calculation, drawdown controls, margin call handling, Greeks monitoring, kill switch, and CloudWatch dashboards | build | trading-risk, golang, var, cvar, margin, greeks, drawdown, risk-management, aws |

### SDK Development

| File | Description | Mode | Tags |
|------|-------------|------|------|
| `sdk-build.md` | Principal Golang Software Architect co-pilot for building enterprise-grade Go SDKs for financial brokers with phases covering infrastructure, domain models, WebSocket streaming, observability, and testing | build | sdk, go, financial, trading, websocket, implementation |
| `sdk-docs.md` | DocSmith-SDK — API SDK documentation improvement with SDK README structure, OpenAPI integration, version safety, and authentication guides | build | documentation, sdk, api, readme, changelog, migration |

### Architecture & Engineering

| File | Description | Mode | Tags |
|------|-------------|------|------|
| `api-design.md` | REST/GraphQL/gRPC API design with OpenAPI specs, versioning, authentication, rate limiting, pagination, and error handling | all | api, rest, graphql, grpc, openapi, design, versioning |
| `architecture.md` | System architecture design for scalability, reliability, and maintainability covering microservices, event-driven patterns, caching, load balancing, and data consistency | all | architecture, system-design, microservices, event-driven, scalability, caching |
| `code-review.md` | Comprehensive code review for correctness, security, performance, maintainability, and best practices across Go and Python | review | code-review, security, performance, maintainability, correctness |
| `database-design.md` | Database schema design, migrations, indexing strategies, query optimization, and multi-tenant architecture | all | database, schema, migration, indexing, sql, nosql, query-optimization |
| `devops.md` | CI/CD pipelines, Docker/Kubernetes configurations, Infrastructure as Code, and deployment strategies (blue-green, canary, rolling) | all | devops, ci-cd, docker, kubernetes, infrastructure, iac, deployment, github-actions |
| `frontend-dev.md` | React 18 + Next.js 14 frontend development with Zustand state management, shadcn/ui + Tailwind CSS, TanStack Query, Core Web Vitals, and accessibility | build | frontend, react, nextjs, typescript, zustand, tailwind, shadcn, web-vitals |
| `graphql-development.md` | GraphQL development with Apollo Server 4, DataLoader for N+1 prevention, Apollo Federation, graphql-ws subscriptions, and performance optimization | build | graphql, apollo, dataloader, federation, subscriptions, typescript |
| `grpc-development.md` | gRPC development with Protobuf v3, buf CLI, Go grpc-go, gRPC-gateway for REST, Envoy proxy, and Istio service mesh | build | grpc, protobuf, golang, buf, grpc-gateway, envoy, istio |
| `llm-integration.md` | LLM integration with RAG architecture, vector databases (Pinecone/Milvus), prompt engineering, vLLM/Ollama local deployment, AI safety, and RAG evaluation | build | llm, rag, vector-db, pinecone, milvus, langchain, vllm, ollama, ai-safety |
| `incident-response.md` | Incident response runbooks, on-call procedures, postmortem templates, and alerting strategies for production systems | all | incident-response, on-call, postmortem, runbook, alerting, sre |
| `performance.md` | Performance optimization with Go pprof/async-profiler, Python py-spy/cProfile, k6 load testing, PostgreSQL EXPLAIN ANALYZE, Redis caching, and Core Web Vitals | build | performance, golang, python, pprof, profiling, load-testing, k6, redis |
| `security.md` | Security engineering with OWASP Top 10, SAST/DAST scanning, secrets management, threat modeling (STRIDE), and penetration testing | all | security, owasp, sast, dast, secrets-management, threat-modeling |
| `testing.md` | Testing strategy with unit tests, integration tests, e2e tests, fuzz testing, property-based testing, and test automation with coverage gates | all | testing, unit-test, integration-test, e2e, fuzzing, property-based-testing, coverage |
| `migration.md` | Migration guide for zero-downtime database migrations with Flyway/Liquibase, monolith to microservices refactoring, and blue-green deployments | build | migration, flyway, liquibase, zero-downtime, monolith, terraform, blue-green |
| `observability-sre.md` | Observability and SRE practices for financial platforms with OpenTelemetry, SLOs, incident response, capacity planning, and production diagnostics | build | observability, sre, opentelemetry, slo, slis, monitoring, alerting, reliability, incident-response |
| `event-driven-architecture.md` | Event-driven financial systems with Kafka, schema evolution, CQRS, event sourcing, ordering, replay, deduplication, and resilient asynchronous workflows | build | event-driven, kafka, cqrs, event-sourcing, schema-registry, streaming, replay, distributed-systems |

### Data Engineering

| File | Description | Mode | Tags |
|------|-------------|------|------|
| `data-engineering.md` | Data pipeline with Apache Airflow/Prefect, Kafka/Flink streaming, Debezium CDC, dbt transformations, MSK/S3 data lake, and Great Expectations quality | build | data-engineering, airflow, kafka, debezium, dbt, msk, s3, athena |

---

## Browse by Technology

### Language

| Language | Files |
|----------|-------|
| **Go** | `broker-integration.md`, `market-data-pipeline.md`, `trading-bot.md`, `trading-risk.md`, `realtime-analytics.md`, `grpc-development.md`, `performance.md`, `sdk-build.md`, `broker-webull.md`, `broker-ibkr.md`, `broker-tiger.md`, `broker-longbridge.md`, `broker-futu.md`, `broker-vbroker.md`, `portfolio-accounting.md`, `broker-google.md` |
| **Python** | `quant-backtesting.md`, `realtime-analytics.md`, `data-engineering.md`, `llm-integration.md`, `frontend-dev.md`, `performance.md` |
| **TypeScript** | `frontend-dev.md`, `graphql-development.md` |

### Cloud Provider

| Provider | Files |
|----------|-------|
| **AWS** | `broker-integration.md`, `trading-risk.md`, `market-data-pipeline.md`, `data-engineering.md`, `devops.md`, `security.md`, `migration.md` |

### Broker / Exchange

| Broker | Files |
|--------|-------|
| **IBKR** | `broker-integration.md`, `broker-ibkr.md`, `quant-backtesting.md` |
| **Futu (OpenD)** | `broker-integration.md`, `broker-futu.md` |
| **Webull** | `broker-integration.md`, `broker-webull.md` |
| **Tiger Trade** | `broker-integration.md`, `broker-tiger.md` |
| **vbroker (Hua Sing Tong)** | `broker-integration.md`, `broker-vbroker.md` |
| **Longbridge** | `broker-integration.md`, `broker-longbridge.md` |

### Framework / Tool

| Tool | Files |
|------|-------|
| **Kafka / MSK** | `market-data-pipeline.md`, `data-engineering.md` |
| **Redis** | `market-data-pipeline.md`, `realtime-analytics.md`, `performance.md` |
| **PostgreSQL** | `database-design.md`, `migration.md`, `performance.md` |
| **React / Next.js** | `frontend-dev.md` |
| **GraphQL / Apollo** | `graphql-development.md` |
| **gRPC / Protobuf** | `grpc-development.md` |
| **Kubernetes** | `devops.md`, `migration.md` |
| **Terraform** | `devops.md`, `migration.md` |
| **Airflow** | `data-engineering.md` |

---

## Search

### Find by task

```
# Looking for trading bot development?
grep -l "trading-bot\|TWAP\|VWAP\|position sizing" *.md

# Looking for API design?
grep -l "api-design\|openapi\|rest\|graphql" *.md

# Looking for security?
grep -l "security\|owasp\|penetration" *.md

# Looking for observability?
grep -l "cloudwatch\|prometheus\|grafana\|tracing" *.md
```

### Quick Reference

| Task | Recommended Prompt |
|------|-------------------|
| Start a new project | `orchestrate.md` (BUILD mode) |
| Plan next phase | `plan.md` |
| Build broker SDK | `broker-integration.md` |
| Backtest strategy | `quant-backtesting.md` |
| Design APIs | `api-design.md` |
| Set up CI/CD | `devops.md` |
| Review code | `code-review.md` |
| Security audit | `security.md` |
| Database design | `database-design.md` |
| Performance tuning | `performance.md` |
| Incident response | `incident-response.md` |
| Testing strategy | `testing.md` |
| Migration plan | `migration.md` |
| Frontend dev | `frontend-dev.md` |
| LLM integration | `llm-integration.md` |
| Data pipeline | `data-engineering.md` |

---

## Statistics

| Metric | Count |
|--------|-------|
| **Total Prompts** | 38 |
| **Financial Domain** | 18 |
| **SDK Development** | 2 |
| **Architecture & Engineering** | 16 |
| **Data Engineering** | 1 |
| **Orchestration** | 2 |
| **Go-focused** | 10 |
| **Python-focused** | 6 |
| **TypeScript-focused** | 3 |
| **AWS-related** | 7 |

---

## Contributing

When adding a new prompt:

1. Follow the frontmatter format:
```yaml
---
description: [1-line summary]
mode: [build | plan | review | docs | all]
model: any
tags: [array of relevant tags]
---
```

2. Place in appropriate category above
3. Update this index with the new file
4. Ensure tags cover: language, domain, broker (if applicable), key technologies
