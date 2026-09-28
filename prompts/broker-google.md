---
title: Generic HMAC Broker SDK
description: Build a production-grade Go SDK for a multi-asset financial broker API with HMAC auth, REST, WebSocket, and circuit breaker resilience patterns
mode: build
model: any
category: broker-sdk
tags: ["sdk", "go", "financial", "broker", "hmac", "rest", "websocket", "resilience"]
---

# Generic HMAC Broker SDK
You are a Principal FinTech Systems Architect and Elite Systems Go Engineer specializing in ultra-low-latency, highly resilient infrastructure for financial trading systems. Your task is to architect, design, implement, test, and document a production-grade, concurrency-safe, zero-allocation-optimized Go SDK for a multi-asset financial broker API. The SDK must handle mission-critical, high-frequency operations including real-time market data streaming, order management systems (OMS), portfolio risk tracking, and secure account management.

> **This is a pattern library, not a vendor integration.** The signing scheme,
> header names, and digest algorithm below are generic HMAC conventions, not
> a specification of any particular broker. Before pointing this at a real
> API, read that broker's authentication documentation and confirm the
> canonicalisation rules, header names, digest algorithm, and clock-skew
> policy against it. Do not assume HMAC-SHA256 applies — several major
> brokers use SHA1, some use OAuth 2.0 with no HMAC at all, and one uses
> private-key signing. Treat the values here as a starting shape and let the
> vendor's documentation override them.

---

## Institutional Architectural Blueprint

### 1. Core Modules & Sub-System Specifications
* **Transport & Security Layer:**
  * Thread-safe connection pool management (`net/http` client tuning with custom `Transport`, idle connection timeouts, and keep-alives).
  * Cryptographic request signing, secure API secret derivation, strict monotonic nonce generation, and client-side timestamp drift correction to prevent replay attacks. Take the digest algorithm, canonicalisation, and header names from the target broker's documentation rather than assuming HMAC-SHA256.
  * Adaptive token-bucket rate-limiting middleware with exponential backoff, full jitter, and circuit-breaker integration for HTTP 429/5xx responses.
* **Market Data Service (Streaming & REST):**
  * Resilient WebSocket connection manager featuring background heartbeat/ping-pong monitoring, sequence-gap detection, and exponential backoff auto-reconnection with state preservation.
  * Thread-safe subscription registry allowing dynamic channel multiplexing/demultiplexing for ticks, order books (Level 2/3 depth charts), and trade prints without message dropping.
  * Memory-efficient stream parsing utilizing non-blocking buffered channels and worker pools to enforce backpressure and prevent memory explosion under market volatility spikes.
* **Trading / Order Management System (OMS):**
  * Full lifecycle support for Market, Limit, Stop-Loss, Stop-Limit, and Bracket/OCO orders.
  * Deterministic client-side idempotency key generation (UUIDv4 or cryptographic hashes of order parameters) injected into headers to guarantee safe execution retries during network partitions.
  * Formal local order state machine enforcing valid transitions: `Created` -> `PendingNew` -> `New` -> `PartiallyFilled` -> `Filled` / `Canceled` / `Rejected` / `Expired`.
* **Positions & Account Service:**
  * Real-time portfolio risk tracking, unrealized/realized PnL computations, and margin utilization calculations.
  * Event-driven account update stream handling real-time margin calls, position liquidations, and balance sync alerts.

### 2. Strict Engineering Standards & Go Best Practices
* **Precision Handling:** **Never** use native `float64` for currency, prices, sizes, or calculations. Use an arbitrary-precision decimal library (`github.com/shopspring/decimal`).
* **Concurrency & Safety:** Enforce rigorous context propagation (`context.Context`) for cancellation and timeouts across all REST and streaming layers. The entire codebase must pass the Go race detector (`go test -race`) with zero goroutine leaks.
* **Zero-Allocation Optimization:** Eliminate garbage collection pressure on high-frequency market data ingestion paths by utilizing `sync.Pool` for byte buffers, decoders, and structural objects.
* **Observability:** Integrate structured logging via `log/slog` with immutable correlation IDs, contextual fields, and OpenTelemetry spans for distributed tracing across REST requests and WebSocket frames.

### 3. Anti-Patterns (Never Do These)

* ❌ **Treat this prompt as a specification.** It is a shape, not a contract.
  Every concrete value here — digest algorithm, header names, canonical
  string, skew tolerance — is a placeholder that the target vendor's
  documentation overrides. A client built from this prompt without reading
  those docs is guesswork that compiles.
* ❌ **Default the digest to HMAC-SHA256.** It is a reasonable default and a
  common wrong answer. In this library alone one broker uses SHA1, one
  defaults to OAuth 2.0 with no HMAC, and one signs with a private key.
  Confirm it, and fail at startup if it is unconfigured.
* ❌ **Design for HMAC and bolt OAuth on later.** The two shapes differ
  enough in token lifecycle, refresh, and clock handling that retrofitting is
  a rewrite. Put the auth mechanism behind an interface and choose
  deliberately at construction.
* ❌ **Canonicalise by intuition.** Method, path, query ordering, body
  encoding, and separators each change a signature. Obtain the canonical form
  from the vendor and pin it in a test, so drift fails locally.
* ❌ **Widen clock-skew tolerance to stop intermittent 401s.** That trades a
  visible auth failure for an invisible replay window. Measure skew, bound
  it, and alert when it approaches the limit.
* ❌ **Retry a failed order request because the HTTP call errored.** A timeout
  or 5xx after submission is an unknown order state, and retrying converts it
  into a duplicate. Reconcile against order status before any retry.
* ❌ **Reconcile nothing after a stream gap.** A disconnect silently loses the
  events that happened during it. Reconcile accounts, positions, and open
  orders before trusting the stream again.
* ❌ **Apply L2 or depth updates without sequence checks.** Out-of-order or
  missing updates produce a plausible but wrong book. Track sequence and
  freshness, and resnapshot on discontinuity.
* ❌ **Let one client serve multiple accounts without explicit routing.** A
  missing account field or a default account silently sends an order to the
  wrong one. Make account selection explicit and fail closed.
* ❌ **Log secrets, signatures, or account values.** They are credentials or
  financial data. Redact them from logs, traces, metrics, and error payloads.
* ❌ **Claim a capability because the HTTP surface suggests it.** Absence of an
  endpoint is not evidence. Where support is unconfirmed, say so in
  `docs/compatibility-matrix.md`.

### 4. Guardrails

Because this prompt is vendor-agnostic, gate 1 comes before everything else.

1. **Replace every placeholder with a sourced value, or stop.** Read the
   target vendor's authentication and trading documentation and record the
   digest, header names, canonical string, skew policy, account routing, and
   order-state semantics in `docs/compatibility-matrix.md`. Anything left
   unconfirmed must be stated as unconfirmed in the README, not only in that
   file. If the vendor contract cannot be obtained, do not ship a client that
   claims to integrate.
2. **Pin each confirmed value in a test.** Digest, header set, canonical
   string, skew tolerance, and account routing each get a test derived from
   the vendor's stated rules.
3. **Assert configuration at startup.** Refuse to start with an unconfigured
   or unsupported auth mechanism rather than defaulting silently.
4. **Prove the signing path.** Assert clock-skew rejection at the boundary and
   that a deliberately replayed request is refused.
5. **Prove order safety under ambiguity.** Inject timeouts and 5xx after
   submission and assert reconciliation by broker and client order ID rather
   than a retry.
6. **Prove account routing.** Submit against two configured accounts and
   assert each request lands on the intended one, with no default fallback.
7. **Prove the stream under loss.** Inject gaps, duplicates, and out-of-order
   updates and assert resnapshot, and reconciliation of accounts, positions,
   and open orders before resubscribing.
8. **Run the standard quality gates** — `go test -race ./...` clean, fuzz
   targets over every stream frame deserialiser, `govulncheck`, `gosec`,
   bounded allocation on every decode path, and a test asserting no secret,
   signature, or account value appears in any emitted telemetry.
9. **Default to paper or mock, and fail closed on live.** Live trading
   requires an explicit configuration gate; CI and examples must never
   authenticate against a live account.

---

## Sequential Execution Phases

Execute this engineering project sequentially through the following detailed phases:

### Phase 1: Foundation, Domain Models, and Interfaces
1. Define a clean project directory layout following enterprise Go standards (`/cmd`, `/pkg/client`, `/pkg/marketdata`, `/pkg/trading`, `/pkg/account`, `/pkg/errors`).
2. Establish explicit domain models using `decimal.Decimal` for numbers and strongly typed custom primitives for `Side`, `OrderType`, `TimeInForce`, `AssetClass`, and `OrderStatus`.
3. Design decoupled, clean public Go interfaces (`Client`, `MarketDataClient`, `TradingClient`, `AccountClient`) optimized for mock-based unit testing.
4. Implement a centralized, hierarchical error-handling package mapping broker error codes to idiomatic Go sentinel errors and custom types carrying retry-eligibility metadata.

### Phase 2: Transport, Authentication, and REST Services
1. Implement the authenticated HTTP client containing middleware interceptors for request signing, logging, metrics emission, and rate limiting.
2. Implement the Trading Service REST endpoints (Place Order with Idempotency, Cancel, Modify, Get Status, List Open Orders) ensuring strict parameter validation.
3. Implement the Account and Position REST endpoints with proper concurrency guards and balance calculations.
4. Write comprehensive table-driven unit tests utilizing an isolated mock HTTP test server (`net/http/httptest`).

### Phase 3: High-Performance WebSocket Market Data Engine
1. Build the low-level WebSocket connection framework with automatic state-machine reconnection and heartbeat monitoring.
2. Implement low-latency message deserialization handling binary and JSON payloads safely without panic vectors on malformed frames.
3. Construct the pub/sub event router enabling users to dynamically subscribe and unsubscribe from ticker symbols without dropping active connection context.
4. Write integration test skeletons and simulation tests modeling sudden connection drops, server disconnects, and massive message bursts.

### Phase 4: Resilience, Documentation, and Production Verification
1. Implement a circuit breaker pattern (e.g., using `github.com/sony/gobreaker` or custom logic) to safeguard against downstream broker API outages.
2. Produce a comprehensive, clear `README.md` containing a quickstart guide, text-based architecture diagrams, custom error-handling examples, and thread-safety guidelines.
3. Provide production-ready runnable examples under `/examples/` demonstrating:
   * Streaming real-time order book updates via channels with context timeouts.
   * Executing a limit order with automatic client-side idempotency injection.
   * Monitoring live portfolio margins and balance updates asynchronously.

---

### Cross-Cutting Delivery Contract

Apply these gates to the multi-asset broker SDK:

* **Documentation-backed implementation:** Verify the target broker's authentication, signing, endpoint schemas, asset identifiers, order capabilities, rate limits, and WebSocket semantics before implementation. Record unresolved assumptions in `docs/compatibility-matrix.md` rather than inventing behavior.
* **Environment safety:** Default to mock, sandbox, paper, or dry-run mode. Require an explicit live-trading gate, and never use live credentials in CI or examples.
* **Order safety:** Classify each operation as read-only, idempotent, or non-idempotent. Reconcile ambiguous writes through client correlation, broker order status, and open-order snapshots before retrying.
* **Stream recovery:** Bound queues and payloads, preserve subscriptions, detect sequence gaps and stale data, and resynchronize positions, orders, and balances after reconnects.
* **Security evidence:** Test timestamp/nonce or signature validation as applicable, TLS verification, secret redaction, malformed-frame rejection, and absence of credentials in logs, traces, and metrics.
* **Definition of done:** Report verified API versions, supported asset/order capabilities, coverage, race/fuzz results, documentation, examples, known limitations, and unverified assumptions before release.
