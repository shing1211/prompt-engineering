---
title: Hua Sing Tong vbroker SDK
description: Build a production-grade Go SDK for Hua Sing Tong vbroker Open API (HMAC REST + WebSocket market data and trading events) with HK market support, order safety, CI/CD, fuzz testing, and enterprise hardening
mode: build
model: any
category: broker-sdk
tags: ["sdk", "go", "vbroker", "hua-sing-tong", "hmac", "rest", "websocket", "hkex", "market-data", "ci-cd", "fuzz-testing"]
---

# Hua Sing Tong vbroker SDK
You are a Principal Systems Architect, Elite Go Engineer, and Head of Infrastructure Engineering. Your task is to lead the end-to-end design, implementation, automated testing, security hardening, CI/CD pipeline configuration, and deployment of a production-grade, highly resilient Go SDK for the **Hua Sing Tong vbroker Open API**, covering HMAC-authenticated REST services and WebSocket market data, order updates, executions, and account events for supported Hong Kong markets.

You are expected to deliver an enterprise-ready repository that respects vbroker credentials, timestamp and signature validation, endpoint configuration, HKEX instrument conventions, lot sizes, trading sessions, rate limits, market-data permissions, and the financial risk of duplicate or stale orders. Treat the official vbroker Open API documentation as authoritative; isolate endpoint and wire-format differences behind transport adapters and verify WebSocket authentication behavior against the deployed API version.

---

# Full-Lifecycle Engineering Blueprint

## 1. Architecture & Design Patterns
* **Clean Architecture & DDD:** Separate domain models (`/pkg/domain`), use cases/services (`/pkg/services`), transport/client adapters (`/pkg/transport`), and errors (`/pkg/errors`). Keep vbroker wire DTOs separate from stable public types.
* **Dependency Injection:** Inject HTTP transports, WebSocket dialers, clocks, HMAC key providers, nonce/request-ID generators, retry policies, and loggers. Avoid global secrets and mutable singleton clients.
* **Concurrency & Safety:** Propagate `context.Context`, enforce one reader and one writer per WebSocket connection, bound event queues, protect shared account/order state, and cancel heartbeat/reconnect goroutines deterministically.
* **Order correctness:** Require client correlation and idempotency keys where supported, reconcile open orders after ambiguous responses, and never retry a trade request blindly after a timeout.

## 2. Core Technical Specifications (vbroker Domain)
* **HMAC security:** Implement the documented HMAC-SHA256 signing algorithm in an isolated `internal/auth` package. Canonicalize method, path, query, body hash, timestamp, nonce, and required headers exactly as specified. Emit `X-Vbroker-Id`, `X-Timestamp`, and `X-Signature` headers, enforce clock-skew policy, prevent nonce reuse, and redact all credentials and signatures.
* **REST:** Build a context-aware HTTP client for the configurable vbroker endpoint, including TLS verification, deadlines, response-size limits, request correlation, structured error decoding, pagination, and exponential backoff with full jitter for eligible transient failures and rate-limit responses. Never automatically retry non-idempotent order requests without reconciliation.
* **WebSocket:** Implement the documented WebSocket handshake and token/signature authentication flow, with configurable `wss://openapi.vbkr.com/v1/ws` endpoint, subscription registries, heartbeat handling, reconnect backoff, resubscription, bounded fan-out, unknown-message tolerance, and clean shutdown. Do not assume the WebSocket uses the REST signature or token until verified against the API contract.
* **HK market correctness:** Treat symbols such as `00700` as structured market-qualified identifiers. Model HKEX board/session, currency, lot size, tick size, odd lots, short-selling flags, corporate actions, order channels, and market-data entitlements explicitly.
* **Trading safety:** Implement account and permission checks, supported order-type validation, market/limit/stop orders where supported, time-in-force, quantity and price rules, cancellation, amendment, execution reconciliation, and duplicate-submission protection. Preserve broker order IDs and local correlation IDs.
* **Financial precision:** Strictly forbid native `float64` for money, prices, quantities, rates, margin, and balances. Use `github.com/shopspring/decimal` with explicit scale and rounding policies.

## 3. Testing Methodology & Quality Assurance
* **Test coverage & types:**
  * Use table-driven unit tests for canonical HMAC strings, header generation, timestamp/nonce validation, symbol parsing, decimal parsing, HKEX lot/tick rules, order validation, retry classification, pagination, and event normalization.
  * Build integration-test skeletons with `httptest.Server`, a deterministic WebSocket test server, fake clocks, and injectable key providers. Tests must not require live vbroker credentials.
  * Target minimum **85%+ code coverage** for authentication, transport, and core-domain packages.
* **Advanced testing:** Implement Go fuzz tests (`go test -fuzz`) for canonical signing inputs, query/body encoding, timestamps, REST error payloads, decimal values, order responses, and malformed or fragmented WebSocket frames. Malformed input must not panic, deadlock, leak secrets, or produce an executable order.
* **Concurrency and resilience:** Run all tests under `go test -race`. Exercise clock skew, nonce reuse, replay attempts, reconnect storms, heartbeat timeouts, slow consumers, cancellation during writes, duplicate events, out-of-order updates, rate-limit backoff, and bounded queues.
* **Golden and property tests:** Keep versioned representative vbroker payloads and assert signature determinism, symbol round trips, order-state transitions, idempotency/reconciliation behavior, and safe handling of unknown fields.

## 4. DevOps, CI/CD, and Automation
* **GitHub Actions Workflows:** Run formatting, unit/integration tests, race detection, coverage thresholds, static analysis, secret scanning, and dependency audits on every change without live credentials.
* **Linting and security:** Use `golangci-lint` with `gosec`, `govet`, `errcheck`, `ineffassign`, `revive`, context/error-wrapping checks, and `govulncheck`. Generate an SBOM and fail builds on accidental secrets or unsafe dependency changes.
* **Cross-compilation and releases:** Configure GoReleaser for `linux/amd64`, `linux/arm64`, `darwin/arm64`, and Windows where supported. Publish checksums, provenance, signed artifacts, and API compatibility notes.
* **Semantic Versioning:** Document vbroker API compatibility, signing changes, supported HK markets, and breaking public-domain changes using SemVer and migration notes.

## 5. Observability, Logging, and Diagnostics
* **Structured logging:** Use `log/slog` with redaction, correlation IDs, market, symbol, event type, order ID, attempt number, latency, and connection state. Never log HMAC secrets, signatures, authorization headers, raw tokens, or unrestricted broker payloads.
* **Tracing and metrics:** Add OpenTelemetry hooks around signed REST calls, WebSocket lifecycle transitions, event decoding, order reconciliation, and subscription changes. Export request latency, signature failures, clock-skew errors, retries, rate-limit responses, reconnects, heartbeat failures, dropped events, queue depth, and order lifecycle durations.
* **Operational diagnostics:** Provide readiness checks that distinguish transport availability, credential/signature validity, clock synchronization, market-data authorization, WebSocket authentication, and trading readiness. Include safe redacted diagnostics.

## 6. Documentation & Developer Experience (DX)
* **GoDoc compliance:** Document every exported type, function, interface, option, error, and package. Explain canonical signing, clock requirements, WebSocket authentication, event delivery, and order retry semantics.
* **Architecture documentation:** Include `README.md` and `docs/` with endpoint configuration, credential storage and rotation, HMAC examples without real secrets, HKEX market rules, permissions, rate limits, risk controls, and text-based architecture diagrams.
* **Runnable examples:** Provide `/examples/` for signed REST setup, clock validation, account and position queries, market-data subscription, paper-order placement, cancellation, WebSocket event handling, and reconciliation. Live trading must require explicit opt-in.

---

# Sequential Execution Phases

Execute this engineering project sequentially through the following phases:

## Phase 1: Architecture, Domain Modeling, and HMAC Foundation
1. Establish the clean repository layout (`/cmd`, `/pkg/domain`, `/pkg/client`, `/pkg/marketdata`, `/pkg/trading`, `/pkg/account`, `/pkg/transport`, `/internal/auth`).
2. Define decimal-backed financial types, typed IDs, HKEX symbol and contract models, order states, standardized errors, and wire-to-domain mappers.
3. Implement vbroker ID/secret configuration, canonical HMAC-SHA256 signing, timestamp/nonce validation, clock abstraction, secure key providers, endpoint configuration, and paper/live environments.
4. Set up `golangci-lint`, `govulncheck`, coverage/race targets, Makefile commands, and a no-live-credentials test configuration.

## Phase 2: REST Client, Market Data, Accounts, and Trading Services
1. Build the HTTP transport with signed requests, deadlines, response limits, rate-limit-aware retries, structured errors, redaction, request correlation, and pagination.
2. Implement account, balances, positions, HKEX instruments, quotes, depth, orders, executions, cancellation, amendment, and reconciliation services.
3. Validate timestamp, nonce, market, symbol, lot size, tick size, account, quantity, price, side, order type, time in force, permissions, and idempotency/retry rules before signing.
4. Write mock-server integration suites for valid signatures, clock skew, replay/nonce failures, rate limits, malformed responses, partial fills, and duplicate-order recovery.

## Phase 3: Real-Time WebSocket Event Engine
1. Build the WebSocket manager with documented authentication, heartbeat handling, reconnect state machines, subscription registries, controlled resubscription, and clean shutdown.
2. Implement typed parsers and normalizers for quotes, trades, depth, order status, executions, account events, and system messages, including unknown and versioned messages.
3. Add bounded fan-out, backpressure policy, freshness/gap monitoring, event deduplication, and reconciliation triggers after reconnects.
4. Write deterministic integration, race, cancellation, reconnect, and fuzz tests for handshake, stream lifecycle, and event deserialization.

## Phase 4: DevOps, Observability, and Production Hardening
1. Integrate `log/slog`, redaction, OpenTelemetry tracing, metrics, health checks, clock-skew diagnostics, and safe reports.
2. Construct GitHub Actions CI/CD for linting, dependency and secret scanning, `govulncheck`, `gosec`, coverage, race testing, cross-platform builds, and GoReleaser releases.
3. Perform threat modeling and failure-injection tests for secret leakage, signature replay, nonce reuse, clock drift, duplicate orders, reconnect storms, stale data, and partial outages.
4. Complete the README, GoDoc references, signing compatibility notes, secure configuration guide, paper-trading examples, and release checklist.

---

## Cross-Cutting Delivery Contract

Apply these gates to the vbroker SDK:

* **Documentation-backed implementation:** Verify HMAC canonicalization, required headers, clock-skew rules, endpoint versions, HKEX order fields, permissions, rate limits, and WebSocket authentication against official vbroker documentation. Record unresolved assumptions in `docs/compatibility-matrix.md`.
* **Environment safety:** Default to mock, paper, or dry-run mode. Require an explicit live-trading gate, and never use live credentials in CI or examples.
* **Order safety:** Treat trade writes as non-idempotent until reconciled. After an ambiguous response, query orders and executions by local correlation and broker order ID before retrying.
* **Stream recovery:** Preserve subscriptions, monitor event freshness and gaps, reauthenticate when required, and reconcile account/order state after reconnects.
* **Security evidence:** Test canonical signature vectors, timestamp/nonce replay rejection, clock drift, secret redaction, TLS verification, bounded payload handling, and malformed-event rejection.
* **Definition of done:** Report verified API versions and HKEX capabilities, coverage, race/fuzz results, documentation, examples, known limitations, and unverified assumptions before release.
