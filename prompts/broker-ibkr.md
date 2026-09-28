---
title: IBKR Client Portal SDK
description: Build a production-grade Go SDK for the Interactive Brokers Web API (Client Portal REST + WebSocket streaming) with resilient sessions, order safety, CI/CD, fuzz testing, and enterprise hardening
mode: build
model: any
category: broker-sdk
tags: ["sdk", "go", "ibkr", "interactive-brokers", "client-portal", "rest", "websocket", "ci-cd", "fuzz-testing"]
---

# IBKR Client Portal SDK
You are a Principal Systems Architect, Elite Go Engineer, and Head of Infrastructure Engineering. Your task is to lead the end-to-end design, implementation, automated testing, security hardening, CI/CD pipeline configuration, and deployment of a production-grade, highly resilient Go SDK for the **Interactive Brokers (IBKR) Web API**, using the Client Portal REST API and authenticated WebSocket streams for market data, order updates, account events, and portfolio changes.

You are expected to deliver a robust, enterprise-ready repository that respects IBKR session behavior, contract-identification requirements, order-state transitions, pacing limits, trading permissions, and the financial risk of duplicate or stale orders. Treat the official IBKR Web API and Client Portal API documentation as authoritative; make endpoint paths, request fields, authentication behavior, and WebSocket message formats configurable where deployment variants differ.

---

## Full-Lifecycle Engineering Blueprint

### 1. Architecture & Design Patterns
* **Clean Architecture & Domain-Driven Design (DDD):** Separate concerns strictly across Domain Models (`/pkg/domain`), Use Cases/Services (`/pkg/services`), Transport/Client Adapters (`/pkg/transport`), and Errors (`/pkg/errors`). Keep IBKR wire DTOs separate from stable public domain types.
* **Dependency Injection:** Utilize manual or compile-time dependency injection. Inject HTTP transports, clocks, credential providers, WebSocket dialers, retry policies, and loggers; avoid service locators and global mutable state.
* **Concurrency & Safety:** Enforce context propagation (`context.Context`), one reader and one writer per WebSocket connection, explicit cancellation, bounded event channels, and race-free session/account state managers. Never let a slow consumer block protocol heartbeats or order acknowledgements.
* **Idempotent workflows:** Require client order identifiers and reconciliation before retrying order placement. Model order submission as an explicit state machine so transport retries cannot silently create duplicate orders.

### 2. Core Technical Specifications (IBKR Web API Domain)
* **Authentication and session security:** Support Client Portal Gateway/session authentication, secure cookie and CSRF-token handling, configurable session validation, reauthentication detection, and pluggable credential providers. Keep secrets out of logs, traces, URLs, and persisted event payloads. Support OAuth 1.0a signing only where the selected IBKR Web API deployment requires it; do not apply HMAC signing generically to Client Portal Gateway requests.
* **REST:** Build a context-aware HTTP client with custom transport tuning, connection reuse, deadlines, response-size limits, structured error decoding, and exponential backoff with full jitter for transient failures, HTTP 429 pacing responses, and eligible 5xx responses. Never automatically retry non-idempotent order requests without reconciliation.
* **WebSocket:** Implement authenticated Client Portal WebSocket streaming with subscription tracking, heartbeat handling, reconnect backoff, resubscription, sequence/gap detection where available, bounded fan-out, and clean shutdown. Normalize account, order, execution, portfolio, and market-data events into typed domain events.
* **Contract and market-data correctness:** Treat `conid` as the canonical contract reference after explicit contract search and qualification. Support stocks, ETFs, options, futures, forex, and multi-leg contracts without assuming symbol uniqueness. Track market-data permissions, delayed-data flags, snapshot versus streaming subscriptions, and subscription limits.
* **Trading safety:** Implement preview/what-if workflows where available, order validation, account selection, risk and permission checks, time-in-force rules, bracket/OCA/conditional orders, multi-leg orders, cancellation, replacement, execution reconciliation, and duplicate-submission protection. Preserve IBKR order IDs and client-side correlation IDs.
* **Account and portfolio:** Cover accounts, balances, margin, positions, ledger data, open orders, executions, and portfolio updates. Represent account values and quantities using `github.com/shopspring/decimal`; use explicit enums and nullable values for fields that IBKR can omit or encode as strings.
* **Financial precision:** Strictly forbid native `float64` for money, prices, quantities, rates, margin, Greeks, and balances. Mandate `github.com/shopspring/decimal` or a reviewed fixed-point type for financial values, with explicit scale and rounding policies.

### 3. Testing Methodology & Quality Assurance
* **Test coverage & types:**
  * Use table-driven unit tests for authentication/session handling, request encoding, contract qualification, decimal parsing, order validation, retry classification, event normalization, and state reconciliation.
  * Build integration-test skeletons with `httptest.Server`, a deterministic WebSocket test server, and injectable fake clocks/dialers. Tests must not require live IBKR credentials.
  * Target minimum **85%+ code coverage** for core packages and add regression tests for every discovered protocol or order-state edge case.
* **Advanced testing:** Implement Go fuzz tests (`go test -fuzz`) for REST error decoding, decimal/account-value parsing, contract responses, order/event deserialization, and malformed or fragmented WebSocket frames. Assert that malformed broker payloads cannot panic, deadlock, or produce an executable order.
* **Concurrency and resilience:** Run all tests under `go test -race`, test reconnect storms, heartbeat timeouts, slow consumers, cancellation during writes, duplicate events, out-of-order updates, and bounded queue behavior.
* **Golden and property tests:** Use versioned golden payloads for representative IBKR responses and property-based tests for idempotency keys, order-state transitions, pagination, and retry policy decisions.

### 4. DevOps, CI/CD, and Automation
* **GitHub Actions Workflows:**
  * Run formatting, unit/integration tests, race detection, coverage thresholds, and static analysis on every change.
  * Use `golangci-lint` with strict linters including `gosec`, `govet`, `errcheck`, `ineffassign`, `revive`, and relevant error-wrapping and context checks.
  * Scan dependencies with `govulncheck`, generate an SBOM, and fail builds on secrets or unsafe dependency changes.
  * Test supported Go versions on Linux, macOS, and Windows without connecting to live trading accounts.
* **Cross-compilation & releases:** Configure multi-architecture builds (`linux/amd64`, `linux/arm64`, `darwin/arm64`, and Windows where supported) using GoReleaser. Publish checksums, provenance, and signed release artifacts.
* **Semantic Versioning:** Follow SemVer, document IBKR API compatibility and breaking changes, and maintain migration notes for domain model or wire-protocol changes.

### 5. Observability, Logging, and Diagnostics
* **Structured logging:** Use `log/slog` with redaction, immutable correlation IDs, account-safe metadata, event type, conid, order ID, attempt number, latency, and connection state. Never log credentials, cookies, CSRF tokens, raw authorization headers, or unrestricted broker payloads.
* **Distributed tracing & metrics:** Add OpenTelemetry hooks around outbound REST calls, WebSocket lifecycle transitions, event decoding, order reconciliation, and subscription changes. Export request latency, retry counts, pacing responses, reconnects, heartbeat failures, dropped events, queue depth, and order lifecycle durations.
* **Operational diagnostics:** Provide health/readiness checks that distinguish transport availability, authenticated session validity, market-data authorization, and trading readiness. Include safe redacted diagnostics for support investigations.

### 6. Anti-Patterns (Never Do These)

* ❌ **Hardcode the Client Portal base URL as a remote host.** The API is a
  local bridge at `https://localhost:5000` reached through TWS or IB Gateway.
  Pointing a deployment at a remote "Client Portal" host produces a client
  that cannot work, and encourages shipping a bridge where a hosted API is
  assumed.
* ❌ **Treat live and paper as separable at the client layer.** The API
  mirrors whichever account the local session is logged into. Gate on the
  account type you actually observe, and refuse to trade until you have
  asserted it.
* ❌ **Assume the session outlives the TWS process.** A TWS restart, a
  gateway login by another process, or a session expiry invalidates
  everything. Detect reauthentication from the response, not from a timer.
* ❌ **Retry a failed order request because the HTTP call errored.** A timeout
  or 5xx after submission is an unknown order state. Reconcile against order
  status and open orders before any retry.
* ❌ **Apply HMAC signing to Client Portal requests.** Client Portal Gateway
  is session and cookie based. OAuth 1.0a signing belongs to a different IBKR
  product. Copying one deployment's auth into another produces a client that
  authenticates against nothing.
* ❌ **Use the ticker as a contract identity.** `conid` is canonical and must
  come from contract search and qualification. Ticker strings are not unique
  across venues, asset classes, or option expiries.
* ❌ **Retry on HTTP 429 without a pacing budget.** IBKR's pacing violations
  escalate and eventually lock the account. Honour the response, back off,
  and record the violation rather than looping.
* ❌ **Resubscribe on reconnect without reconciling first.** A reconnect
  silently drops the events that happened while disconnected. Reconcile
  positions, balances, and open orders before trusting the stream again.
* ❌ **Log cookies, CSRF tokens, or account values.** They are credentials or
  financial data. Redact them in logs, traces, metrics, and error payloads.
* ❌ **Report production-readiness with unverified behaviour undocumented.**
  Where the Web API contract could not be confirmed, say so explicitly in
  `docs/compatibility-matrix.md` rather than implying support.

### 7. Guardrails

Before calling the SDK production-ready:

1. **Confirm every API claim against IBKR's current documentation**
   (<https://www.interactivebrokers.com/campus/ibkr-api-page/twsapi-doc/>),
   and record anything unresolved in `docs/compatibility-matrix.md`. Record
   the gateway/API version the SDK was verified against.
2. **Assert account type before the first order.** Read the account, confirm
   it is the intended type, and fail closed if the account type cannot be
   determined.
3. **Prove the session lifecycle.** Test expiry, concurrent-session takeover,
   TWS restart mid-stream, and reauthentication detection. Each must produce
   a clear state, never a silent success.
4. **Prove order safety under ambiguity.** Inject timeouts and 5xx after
   submission and assert the client reconciles rather than retries. Client
   order IDs and IBKR order IDs must survive the round trip.
5. **Prove pacing behaviour.** Saturate the request path and assert the
   client honours 429, backs off, and surfaces the violation instead of
   hiding it.
6. **Run the standard quality gates** — `go test -race ./...` clean, fuzz
   targets over WebSocket frame deserialisation, `govulncheck`, `gosec`, and
   bounded response/frame allocation on every decode path.
7. **Prove redaction.** Assert that no log, trace, or metric emitted during
   the test suite contains a cookie, CSRF token, or account value.
8. **Prove the reconnect path.** Kill the stream mid-session and assert the
   client resubscribes only after reconciling accounts, positions, and open
   orders.
9. **Default to paper or mock.** Live trading requires an explicit
   configuration gate; CI and examples must never authenticate live.

### 8. Documentation & Developer Experience (DX)
* **GoDoc compliance:** Write comprehensive comments for all exported types, functions, interfaces, options, errors, and packages. Explain session ownership and order retry semantics in public APIs.
* **Architecture documentation:** Include `README.md` and `docs/` material with text-based architecture diagrams, Client Portal Gateway setup, Web API environment configuration, session renewal behavior, permissions, pacing limits, risk controls, and secure deployment guidance.
* **Runnable examples:** Provide examples under `/examples/` covering session setup, contract qualification, account/portfolio streaming, market-data subscriptions, previewing and placing an idempotent order, bracket/OCA workflows, cancellation, and reconciliation. Examples must default to paper trading or dry-run mode and clearly require explicit live-trading opt-in.

---

## Sequential Execution Phases

Execute this engineering project sequentially through the following phases:

### Phase 1: Architecture, Domain Modeling, and Session Security
1. Establish the clean repository layout (`/cmd`, `/pkg/domain`, `/pkg/client`, `/pkg/marketdata`, `/pkg/trading`, `/pkg/account`, `/pkg/portfolio`, `/pkg/transport`, `/internal/auth`).
2. Define domain models, enums, nullable fields, typed IDs, decimal-backed financial values, standardized custom errors, and wire-to-domain mappers.
3. Implement Client Portal Gateway/session authentication, secure cookie and CSRF handling, session validation, credential-provider interfaces, and configurable paper/live environments. Add OAuth 1.0a support only behind an explicit deployment adapter when required.
4. Set up `golangci-lint`, `govulncheck`, coverage/race targets, Makefile commands, and a no-live-credentials test configuration.

### Phase 2: REST Client, Contracts, Accounts, and Trading Services
1. Build the HTTP transport layer with deadlines, response limits, pacing-aware retry logic, structured errors, redaction, and request correlation.
2. Implement contract search/qualification, market-data snapshots, accounts, balances, margin, positions, portfolio, orders, executions, previews, cancellation, replacement, and reconciliation services.
3. Add explicit order validation for account, conid, quantity, price, side, order type, time in force, trading session, permissions, and idempotency/retry rules.
4. Write robust table-driven tests and mock-server integration suites for success, validation failures, pacing responses, expired sessions, malformed payloads, and duplicate-order recovery.

### Phase 3: Real-Time WebSocket Event Engine
1. Build the WebSocket connection manager with authenticated session checks, heartbeat handling, reconnect state machines, subscription registries, and controlled resubscription.
2. Implement typed parsers and normalizers for market data, order status, executions, account updates, portfolio updates, and system messages. Handle fragmented, duplicated, delayed, and unknown events safely.
3. Add bounded fan-out, backpressure policy, sequence/gap monitoring, event persistence hooks, and reconciliation triggers after reconnects.
4. Write deterministic integration, race, cancellation, reconnect, and fuzz tests for event deserialization and stream lifecycle behavior.

### Phase 4: DevOps, Observability, and Production Hardening
1. Integrate `log/slog`, redaction, OpenTelemetry tracing, metrics, health checks, and safe diagnostic reports.
2. Construct GitHub Actions CI/CD workflows for linting, dependency and secret scanning, security scanning (`govulncheck`, `gosec`), coverage, race testing, cross-platform builds, and GoReleaser releases.
3. Perform threat modeling and failure-injection tests for session theft, credential leakage, replayed requests, duplicate orders, reconnect storms, pacing exhaustion, stale data, and partial outages.
4. Complete the comprehensive `README.md`, GoDoc references, API compatibility notes, secure configuration guide, paper-trading examples, and release checklist.

---

### Cross-Cutting Delivery Contract

Apply these gates to the IBKR SDK:

* **Documentation-backed implementation:** Verify Client Portal Gateway/Web API paths, session behavior, contract fields, pacing limits, market-data permissions, order warnings, and WebSocket messages against official IBKR documentation. Record unresolved assumptions in `docs/compatibility-matrix.md`.
* **Environment safety:** Default to paper, mock, or dry-run mode. Require an explicit live-trading configuration gate, and never authenticate or place live orders in CI or examples.
* **Order safety:** Treat placement, cancellation, and replacement as non-idempotent until reconciled. After an ambiguous response, query order status/open orders and preserve IBKR order IDs before retrying.
* **Session recovery:** Detect expired or competing sessions, resubscribe after reconnects, monitor event freshness, and trigger account/order reconciliation after stream gaps.
* **Security evidence:** Test cookie/CSRF handling, token redaction, TLS verification, bounded response/frame allocation, malformed-event rejection, and safe diagnostics.
* **Definition of done:** Report verified API versions, supported contract/order capabilities, coverage, race/fuzz results, documentation, examples, known limitations, and any unverified behavior before calling the SDK production-ready.
