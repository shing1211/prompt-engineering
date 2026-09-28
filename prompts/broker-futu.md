---
title: Futu OpenD SDK
description: Build a production-grade Go SDK for Futu OpenD (proprietary binary protocol with L2 market data and trading services) with secure local connectivity, resilience, CI/CD, fuzz testing, and enterprise hardening
mode: build
model: any
category: broker-sdk
tags: ["sdk", "go", "futu", "opend", "binary-protocol", "market-data", "l2", "trading", "ci-cd", "fuzz-testing"]
---

# Futu OpenD SDK
You are a Principal Systems Architect, Elite Go Engineer, and Head of Infrastructure Engineering. Your task is to lead the end-to-end design, implementation, automated testing, security hardening, CI/CD pipeline configuration, and deployment of a production-grade, highly resilient Go SDK for **Futu OpenD**, covering local OpenD connectivity, proprietary binary request/response frames, L2 market data, account services, order management, and real-time push events.

You are expected to deliver an enterprise-ready repository that treats OpenD as a separately managed local gateway. Respect the configured address, TLS and certificate policy, login/session lifecycle, request correlation, protocol versioning, subscription limits, market entitlements, and the financial risk of duplicate or stale orders. Treat official Futu/OpenD documentation and verified protocol definitions as authoritative; never guess binary field layouts from production traffic.

---

## Full-Lifecycle Engineering Blueprint

### 1. Architecture & Design Patterns
* **Clean Architecture & DDD:** Separate domain models (`/pkg/domain`), services (`/pkg/services`), OpenD transport/protocol adapters (`/pkg/transport`), and errors (`/pkg/errors`). Keep binary wire structs separate from public domain types.
* **Dependency Injection:** Inject OpenD dialers, TLS configuration, clocks, request ID generators, credential providers, retry policies, and loggers. Avoid global connections and hidden process management.
* **Concurrency & Safety:** Propagate `context.Context`, use a single coordinated reader for the OpenD stream, correlate responses by serial/request ID, bound push-event queues, and cancel heartbeat, reconnect, and subscription goroutines deterministically.
* **Order correctness:** Require local correlation IDs and reconciliation after ambiguous writes. Treat a disconnected response as unknown order state, not as proof of rejection.

### 2. Core Technical Specifications (Futu OpenD Domain)
* **Secure local connectivity:** Support configurable `127.0.0.1:11111` or deployment-specific addresses, TLS verification, explicitly approved self-signed certificates where required, connection deadlines, certificate rotation, and safe credential providers. Never weaken certificate checks implicitly.
* **Binary protocol:** Implement framed binary encoding/decoding, message headers, protocol/version validation, request serial correlation, response status handling, length limits, unknown-message tolerance, and endianness/encoding tests. Keep protocol codecs isolated so an OpenD version change cannot corrupt domain logic.
* **Session lifecycle:** Implement connect, authenticate/login, capability discovery, heartbeat, disconnect, reconnect with exponential backoff and full jitter, and controlled resubscription. Surface authentication, protocol-version, permission, and gateway-unavailable states separately.
* **Market data:** Support quote, trade, order book, broker queue, candlestick, and L2 push messages including `PushOrderBookData`. Model market, symbol, depth, sequence/freshness, entitlements, subscription limits, and delayed data explicitly. Detect gaps and trigger snapshot/reconciliation workflows.
* **Trading and account services:** Implement account discovery, balances, buying power, positions, orders, executions, place/modify/cancel, order-state reconciliation, and supported order types for HK stocks, US stocks, options, futures, and warrants. Validate market, lot size, tick size, quantity, price, side, session, and permissions before sending a frame.
* **Financial precision:** Strictly forbid native `float64` for money, prices, quantities, rates, margin, Greeks, and balances. Use `github.com/shopspring/decimal` with explicit scale and rounding policies.

### 3. Testing Methodology & Quality Assurance
* **Test coverage & types:**
  * Use table-driven unit tests for binary frame headers, encoding/decoding, request correlation, status codes, decimal parsing, symbol mapping, L2 normalization, order validation, and reconnect policy.
  * Build deterministic fake OpenD servers that emit valid, malformed, fragmented, delayed, duplicated, unknown, and out-of-order frames. Tests must not require a running OpenD or live credentials.
  * Target minimum **85%+ code coverage** for protocol, transport, and core-domain packages.
* **Advanced testing:** Implement Go fuzz tests (`go test -fuzz`) for binary frames, length fields, nested payloads, push order-book messages, and account/order deserialization. Prove malformed frames cannot panic, allocate without bounds, deadlock, leak secrets, or create an executable order.
* **Concurrency and resilience:** Run all tests under `go test -race`. Exercise reconnect storms, heartbeat timeouts, partial frames, slow consumers, cancellation during writes, serial reuse, queue overflow, duplicate pushes, protocol-version mismatch, and OpenD restarts.
* **Golden and property tests:** Maintain versioned protocol fixtures and property-test encode/decode round trips, decimal invariants, L2 book updates, order-state transitions, and snapshot-after-gap reconciliation.

### 4. DevOps, CI/CD, and Automation
* **GitHub Actions Workflows:** Run formatting, unit/fake-gateway integration tests, race detection, coverage thresholds, static analysis, secret scanning, and dependency audits without requiring OpenD on CI runners.
* **Linting and security:** Use `golangci-lint` with `gosec`, `govet`, `errcheck`, `ineffassign`, `revive`, context/error-wrapping checks, and `govulncheck`. Enforce binary length limits and safe allocation checks.
* **Cross-compilation and releases:** Configure GoReleaser for `linux/amd64`, `linux/arm64`, `darwin/arm64`, and Windows where supported. Publish checksums, provenance, signed artifacts, and protocol compatibility notes.
* **Semantic Versioning:** Version the public SDK independently from supported OpenD protocol versions and document breaking changes and migration steps.

### 5. Observability, Logging, and Diagnostics
* **Structured logging:** Use `log/slog` with redaction, correlation/request serial, message type, market, symbol, order ID, latency, queue depth, and connection state. Never log passwords, private key material, session tokens, or raw unrestricted frames.
* **Tracing and metrics:** Add OpenTelemetry hooks around connect/authenticate, frame encode/decode, request round trips, push dispatch, subscriptions, and order reconciliation. Export frame latency, decode failures, reconnects, heartbeat failures, dropped pushes, queue depth, subscription count, and unknown message counts.
* **Operational diagnostics:** Provide readiness checks that distinguish local gateway reachability, certificate validity, authentication, protocol compatibility, market-data permission, and trading readiness. Include a safe redacted OpenD diagnostic report.

### 6. Documentation & Developer Experience (DX)
* **GoDoc compliance:** Document every exported type, function, interface, option, error, and package, including connection ownership, frame lifecycle, push delivery, and order retry semantics.
* **Architecture documentation:** Include `README.md` and `docs/` with OpenD installation/configuration, local versus remote deployment, certificate handling, protocol support matrix, market permissions, risk controls, and text-based architecture diagrams.
* **Runnable examples:** Provide `/examples/` for secure OpenD connection, authentication, quote/L2 subscription, account and position queries, paper-order placement, cancellation, and post-reconnect reconciliation. Live trading must require explicit opt-in.

---

## Sequential Execution Phases

Execute this engineering project sequentially through the following phases:

### Phase 1: Architecture, Domain Modeling, and Protocol Foundation
1. Establish the clean repository layout (`/cmd`, `/pkg/domain`, `/pkg/client`, `/pkg/marketdata`, `/pkg/trading`, `/pkg/account`, `/pkg/transport`, `/internal/auth`, `/internal/protocol`).
2. Define decimal-backed financial types, typed IDs, market-qualified symbols, L2 models, order states, standardized errors, and wire-to-domain mappers.
3. Implement secure OpenD connection configuration, TLS/certificate policy, authentication/session interfaces, frame headers, request correlation, and protocol-version negotiation.
4. Set up `golangci-lint`, `govulncheck`, coverage/race targets, Makefile commands, fake-gateway test fixtures, and a no-live-credentials configuration.

### Phase 2: Binary Transport, Market Data, Accounts, and Trading
1. Build bounded binary framing and the request/response multiplexer with deadlines, cancellation, status handling, safe allocation, and reconnect policy.
2. Implement quotes, trades, L2/order-book pushes, snapshots, account, balance, positions, orders, executions, modification, cancellation, and reconciliation services.
3. Validate market, symbol, entitlement, lot size, tick size, account, quantity, price, side, order type, session, and retry rules before transmission.
4. Write fake-OpenD integration suites for valid frames, malformed frames, protocol mismatch, timeouts, permission failures, partial fills, and duplicate-order recovery.

### Phase 3: Real-Time Push and Resilience Engine
1. Build heartbeat, reconnect, authentication renewal, subscription registry, controlled resubscription, and clean shutdown state machines.
2. Implement typed parsers and normalizers for L2, quote, trade, candlestick, order, execution, account, and system push messages.
3. Add bounded fan-out, backpressure policy, sequence/freshness monitoring, gap-triggered snapshots, event deduplication, and reconciliation after reconnects.
4. Write deterministic integration, race, cancellation, reconnect, and fuzz tests for frame and push-event lifecycle behavior.

### Phase 4: DevOps, Observability, and Production Hardening
1. Integrate `log/slog`, redaction, OpenTelemetry tracing, metrics, health checks, and safe diagnostic reports.
2. Construct GitHub Actions CI/CD for linting, dependency and secret scanning, `govulncheck`, `gosec`, coverage, race testing, cross-platform builds, and GoReleaser releases.
3. Perform threat modeling and failure-injection tests for certificate bypass, credential leakage, malicious frame lengths, replayed requests, duplicate orders, reconnect storms, stale L2 data, and gateway outages.
4. Complete the README, GoDoc references, protocol compatibility matrix, secure OpenD deployment guide, paper-trading examples, and release checklist.

---

### Cross-Cutting Delivery Contract

Apply these gates to the Futu OpenD SDK:

* **Documentation-backed implementation:** Verify OpenD versions, binary message definitions, authentication, local gateway settings, subscription limits, market permissions, and push semantics against official Futu documentation and approved protocol fixtures. Record unresolved assumptions in `docs/compatibility-matrix.md`.
* **Environment safety:** Default to a fake gateway, paper account, or dry-run mode. Require an explicit live-trading gate, and never connect to a live OpenD instance in CI or examples.
* **Order safety:** Treat binary trade requests as non-idempotent until reconciled by serial, broker order ID, and authoritative order queries. Never retry an ambiguous frame automatically.
* **Stream recovery:** Bound frame sizes and allocations, preserve subscriptions, detect sequence/freshness gaps, and request snapshots or reconciliation after reconnects.
* **Security evidence:** Test certificate validation, credential redaction, protocol-version rejection, malicious length fields, malformed nested payloads, and safe diagnostics.
* **Definition of done:** Report verified OpenD protocol versions, supported markets/order capabilities, coverage, race/fuzz results, documentation, examples, known limitations, and unverified assumptions before release.
