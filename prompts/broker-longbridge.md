---
title: Longbridge SDK
description: Build a production-grade Go SDK for Longbridge OpenAPI (REST + WebSocket quotes and trading streams) with token security, multi-market trading, CI/CD, fuzz testing, and enterprise hardening
mode: build
model: any
category: broker-sdk
tags: ["sdk", "go", "longbridge", "openapi", "rest", "websocket", "market-data", "hkex", "ci-cd", "fuzz-testing"]
---

# Longbridge SDK
You are a Principal Systems Architect, Elite Go Engineer, and Head of Infrastructure Engineering. Your task is to lead the end-to-end design, implementation, automated testing, security hardening, CI/CD pipeline configuration, and deployment of a production-grade, highly resilient Go SDK for the **Longbridge OpenAPI platform**, covering REST quote/trade services and WebSocket market-data and trading-event streams across supported Hong-kong, US, and Australian markets.

You are expected to deliver a robust, enterprise-ready repository that respects Longbridge AppKey/AppSecret/access-token configuration, quote and trade channel separation, market-data permissions, instrument formats, lot sizes, trading sessions, rate limits, and the financial risk of duplicate or stale orders. Treat the official Longbridge OpenAPI documentation and SDK behavior as authoritative; isolate wire DTOs and deployment URLs behind transport adapters.

---

## Full-Lifecycle Engineering Blueprint

### 1. Architecture & Design Patterns
* **Clean Architecture & Domain-Driven Design (DDD):** Separate domain models (`/pkg/domain`), use cases/services (`/pkg/services`), transport/client adapters (`/pkg/transport`), and errors (`/pkg/errors`). Keep Longbridge wire DTOs separate from stable public types.
* **Dependency Injection:** Inject HTTP transports, WebSocket dialers, clocks, token providers, retry policies, and loggers. Avoid global mutable state and hidden network clients.
* **Concurrency & Safety:** Propagate `context.Context`, enforce one reader and one writer per WebSocket connection, bound event queues, protect shared order/account state, and cancel all reconnect and heartbeat goroutines deterministically.
* **Order correctness:** Require client correlation and idempotency keys where supported, reconcile open orders after ambiguous failures, and never treat a lost response as proof that an order was not accepted.

### 2. Core Technical Specifications (Longbridge OpenAPI Domain)
* **Authentication and secret management:** Implement secure AppKey/AppSecret/access-token configuration with pluggable credential providers, environment-specific endpoints, token refresh/rotation hooks where supported, and startup validation. Keep secrets out of URLs, logs, traces, metrics, and persisted events. Do not invent HMAC signing where the selected Longbridge deployment uses access-token authentication.
* **REST:** Build a context-aware HTTP client with custom transport tuning, TLS verification, deadlines, response-size limits, structured error decoding, pagination, request correlation, and exponential backoff with full jitter for eligible transient failures and rate-limit responses. Never blindly retry non-idempotent trade requests.
* **WebSocket:** Implement separate or configurable quote and trade connections as required by Longbridge, with token authentication, subscription registries, heartbeat handling, reconnect backoff, resubscription, bounded fan-out, and clean shutdown. Normalize trades, quotes, depth, candlesticks, order status, executions, and account events into typed domain events.
* **Symbol and market correctness:** Treat Longbridge's market-qualified symbols such as `HK.00700`, `US.AAPL`, and `AU.BHP` as structured identifiers rather than plain strings. Model exchange, currency, lot size, tick size, board/session, corporate-action adjustments, option expiry, strike, and call/put explicitly.
* **Market data:** Support snapshots, trades, quotes, depth, candlesticks, subscription limits, entitlement errors, delayed-versus-real-time flags, and deterministic normalization of level-2 updates. Detect gaps or stale data and expose freshness metadata to callers.
* **Trading safety:** Implement account and market selection, buying-power and permission checks, supported order-type validation, market/limit/stop orders, time-in-force, odd-lot handling, fractional quantities where permitted, cancellation, amendment, execution reconciliation, and duplicate-submission protection.
* **Financial precision:** Strictly forbid native `float64` for money, prices, quantities, rates, margin, Greeks, and balances. Use `github.com/shopspring/decimal` with explicit scale and rounding policies for all financial values.

### 3. Testing Methodology & Quality Assurance
* **Test coverage & types:**
  * Use table-driven unit tests for token/header construction, endpoint selection, symbol parsing, decimal parsing, lot/tick validation, order validation, retry classification, pagination, and event normalization.
  * Build integration-test skeletons with `httptest.Server`, deterministic WebSocket test servers, fake clocks, and injectable token providers. Tests must not require live Longbridge credentials.
  * Target minimum **85%+ code coverage** for core packages and add regression tests for market-specific order and event edge cases.
* **Advanced testing:** Implement Go fuzz tests (`go test -fuzz`) for symbol parsing, token/error payloads, decimal/account-value parsing, order responses, and malformed or fragmented WebSocket frames. Malformed data must not panic, deadlock, leak secrets, or produce an executable order.
* **Concurrency and resilience:** Run all tests under `go test -race`. Exercise reconnect storms, heartbeat timeouts, slow consumers, cancellation during writes, duplicate events, out-of-order depth updates, rate-limit backoff, and bounded queue behavior.
* **Golden and property tests:** Keep versioned Longbridge payloads and verify symbol round trips, decimal invariants, order-state transitions, idempotency/reconciliation behavior, and market-specific validation.

### 4. DevOps, CI/CD, and Automation
* **GitHub Actions Workflows:** Run formatting, unit/integration tests, race detection, coverage thresholds, static analysis, secret scanning, and dependency audits on every change.
* **Linting and security:** Use `golangci-lint` with `gosec`, `govet`, `errcheck`, `ineffassign`, `revive`, context/error-wrapping checks, and `govulncheck`. Generate an SBOM and fail builds on accidental credentials or unsafe dependency changes.
* **Cross-compilation and releases:** Configure GoReleaser for `linux/amd64`, `linux/arm64`, `darwin/arm64`, and Windows where supported. Publish checksums, provenance, and signed artifacts.
* **Semantic Versioning:** Document Longbridge OpenAPI compatibility, supported markets, authentication changes, and breaking public-domain changes using SemVer and migration notes.

### 5. Observability, Logging, and Diagnostics
* **Structured logging:** Use `log/slog` with redaction, correlation IDs, market, symbol, event type, order ID, attempt number, latency, and connection state. Never log AppSecrets, access tokens, authorization headers, or unrestricted broker payloads.
* **Tracing and metrics:** Add OpenTelemetry hooks around outbound REST calls, WebSocket lifecycle transitions, event decoding, order reconciliation, and subscription changes. Export request latency, retries, rate-limit responses, reconnects, heartbeat failures, dropped events, stale-data counts, queue depth, and order lifecycle durations.
* **Operational diagnostics:** Provide health/readiness checks that distinguish transport availability, token validity, quote entitlements, trade readiness, and stream freshness. Include safe redacted diagnostics for support investigations.

### 6. Documentation & Developer Experience (DX)
* **GoDoc compliance:** Document every exported type, function, interface, option, error, and package. Explain market-qualified symbols, token ownership, stream delivery, and order retry semantics.
* **Architecture documentation:** Include `README.md` and `docs/` material with text-based architecture diagrams, Longbridge account and token setup, paper/live environment configuration, market permissions, rate limits, and risk controls.
* **Runnable examples:** Provide `/examples/` for secure client setup, symbol and contract discovery, quote/depth streaming, account and portfolio queries, order preview/placement in paper mode, cancellation, amendment, and reconciliation. Live trading must require explicit opt-in.

---

## Sequential Execution Phases

Execute this engineering project sequentially through the following phases:

### Phase 1: Architecture, Domain Modeling, and Token Security
1. Establish the clean repository layout (`/cmd`, `/pkg/domain`, `/pkg/client`, `/pkg/marketdata`, `/pkg/trading`, `/pkg/account`, `/pkg/portfolio`, `/pkg/transport`, `/internal/auth`).
2. Define decimal-backed financial types, typed IDs, market-qualified symbols, contract models, order states, standardized errors, and wire-to-domain mappers.
3. Implement AppKey/AppSecret/access-token configuration, secure credential providers, environment-specific quote/trade endpoints, token validation/rotation hooks, and paper/live environments.
4. Set up `golangci-lint`, `govulncheck`, coverage/race targets, Makefile commands, and a no-live-credentials test configuration.

### Phase 2: REST Client, Market Data, Accounts, and Trading Services
1. Build the HTTP transport with deadlines, response limits, rate-limit-aware retries, structured errors, redaction, request correlation, and pagination.
2. Implement quotes, trades, depth, candlesticks, account, balance, positions, portfolio, order, execution, cancellation, amendment, and reconciliation services.
3. Validate market, symbol, lot size, tick size, account, quantity, price, side, order type, time in force, permissions, and idempotency/retry rules before requests leave the process.
4. Write mock-server integration suites for valid requests, invalid or expired tokens, entitlement failures, rate limits, malformed responses, partial fills, and duplicate-order recovery.

### Phase 3: Real-Time WebSocket Event Engine
1. Build configurable quote and trade WebSocket managers with token authentication, heartbeat handling, reconnect state machines, subscription registries, controlled resubscription, and clean shutdown.
2. Implement typed parsers and normalizers for quotes, trades, depth, candlesticks, order status, executions, and account events, including unknown and versioned messages.
3. Add bounded fan-out, backpressure policy, freshness and gap monitoring, event deduplication, and reconciliation triggers after reconnects.
4. Write deterministic integration, race, cancellation, reconnect, and fuzz tests for stream lifecycle and event deserialization.

### Phase 4: DevOps, Observability, and Production Hardening
1. Integrate `log/slog`, redaction, OpenTelemetry tracing, metrics, health checks, and safe diagnostic reports.
2. Construct GitHub Actions CI/CD for linting, dependency and secret scanning, `govulncheck`, `gosec`, coverage, race testing, cross-platform builds, and GoReleaser releases.
3. Perform threat modeling and failure-injection tests for token leakage, unauthorized subscriptions, duplicate orders, reconnect storms, rate-limit exhaustion, stale data, and partial outages.
4. Complete the README, GoDoc references, API compatibility notes, secure configuration guide, paper-trading examples, and release checklist.

---

### Cross-Cutting Delivery Contract

Apply these gates to the Longbridge SDK:

* **Documentation-backed implementation:** Verify AppKey/access-token behavior, quote/trade channels, market-qualified symbols, permissions, rate limits, order fields, and WebSocket messages against official Longbridge documentation. Record unresolved assumptions in `docs/compatibility-matrix.md`.
* **Environment safety:** Default to paper, mock, or dry-run mode. Require an explicit live-trading gate, and never use live credentials in CI or examples.
* **Order safety:** Treat trade requests as non-idempotent until reconciled. After an ambiguous response, query orders and executions using local correlation and broker order IDs before retrying.
* **Stream recovery:** Preserve quote/trade subscriptions, monitor freshness and sequence continuity, and resynchronize positions, orders, and market data after reconnects or entitlement changes.
* **Security evidence:** Test token redaction, TLS verification, safe credential rotation, bounded response/frame allocation, malformed-event rejection, and absence of secrets in telemetry.
* **Definition of done:** Report verified API versions and market capabilities, coverage, race/fuzz results, documentation, examples, known limitations, and unverified assumptions before release.
