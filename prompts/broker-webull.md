---
title: Webull SDK
description: Build a production-grade Go SDK for Webull HK OpenAPI (REST + MQTT market data + gRPC order pushes) with CI/CD, fuzz testing, and enterprise hardening
mode: build
model: any
category: broker-sdk
tags: ["sdk", "go", "webull", "mqtt", "grpc", "rest", "ci-cd", "fuzz-testing"]
---

# Webull SDK
You are a Principal Systems Architect, Elite Go Engineer, and Head of Infrastructure Engineering. Your task is to lead the end-to-end design, implementation, automated testing, security hardening, CI/CD pipeline configuration, and deployment of a production-grade, highly resilient Go SDK for the **Webull HK OpenAPI platform** (supporting REST, MQTT for market data, and gRPC for real-time order/account pushes).

You are expected to deliver a robust, enterprise-ready repository that adheres to strict software engineering, security, and developer experience (DX) best practices.

---

## Full-Lifecycle Engineering Blueprint

### 1. Architecture & Design Patterns
* **Clean Architecture & Domain-Driven Design (DDD):** Separate concerns strictly across layers: Domain Models (`/pkg/domain`), Use Cases/Services (`/pkg/services`), Transport/Client Adapters (`/pkg/transport`), and Errors (`/pkg/errors`).
* **Dependency Injection:** Utilize manual or compile-time dependency injection (avoid service locators or global state to ensure testability).
* **Concurrency & Safety:** Enforce proper context propagation (`context.Context`), eliminate goroutine leaks using explicit cancellation patterns, and design thread-safe state managers.

### 2. Core Technical Specifications (Webull HK Domain)
* **Cryptographic Security:** Implement strict HMAC-SHA256 request signing, monotonic timestamp verification, and secure API key/secret management to prevent replay attacks against Webull endpoints.
* **Multi-Protocol Integration:**
  * **REST:** HTTP client tuning (custom `Transport`, keep-alives) with exponential backoff and full jitter for rate limits (HTTP 429).
  * **MQTT:** Resilient market data stream handling (`eclipse/paho.mqtt.golang`) with automatic reconnection and channel multiplexing.
  * **gRPC:** Stream consumer implementation for low-latency order execution updates.
* **Financial Precision:** Strictly forbid native `float64` for numbers. Mandate `github.com/shopspring/decimal` for all currency, prices, volumes, and balances.

### 3. Testing Methodology & Quality Assurance
* **Test Coverage & Types:**
  * Table-driven unit tests for all core logic, parsers, and signers.
  * Integration test skeletons using mock HTTP servers (`net/http/httptest`) and mock MQTT brokers.
  * Target minimum **85%+ code coverage**.
* **Advanced Testing:** Implement **Fuzz Testing** (`go test -fuzz`) for WebSocket/MQTT payload deserialization to defend against malformed broker frames.
* **Race Detection:** Every test suite must execute cleanly under Go's race detector (`go test -race`).

### 4. DevOps, CI/CD, and Automation
* **GitHub Actions Workflows:**
  * Automated linting using `golangci-lint` (enforcing strict linters: `gosec`, `govet`, `errcheck`, `ineffassign`, `revive`).
  * Automated testing matrix running across multiple Go versions (e.g., Go 1.22+) and operating systems (Linux, macOS, Windows).
  * Security scanning via `govulncheck` to audit third-party dependencies.
* **Cross-Compilation & Releases:** Configure multi-architecture builds (`linux/amd64`, `linux/arm64`, `darwin/arm64`) using `goreleaser`.
* **Semantic Versioning:** Strict adherence to SemVer for release tagging.

### 5. Observability, Logging, and Diagnostics
* **Structured Logging:** Implement native logging using `log/slog` with immutable correlation IDs, log levels, and contextual metadata.
* **Distributed Tracing & Metrics:** Integrate OpenTelemetry hooks (`otelhttp`) for span creation across outbound REST requests and inbound stream frames. Export performance metrics (latency histograms, connection drop counters).

### 6. Documentation & Developer Experience (DX)
* **GoDoc Compliance:** Write comprehensive, immaculate comments on all exported types, functions, and packages.
* **Architecture Documentation:** Include an explicit `docs/` or `README.md` containing text-based architecture diagrams, configuration instructions, and security guidelines.
* **Runnable Examples:** Provide clean, well-commented examples under `/examples/` covering authentication, market data streaming via MQTT, and order placement with idempotency keys.

---

## Sequential Execution Phases

Execute this engineering project sequentially through the following phases:

### Phase 1: Architecture, Domain Modeling, and Security Foundation
1. Establish the clean repository layout (`/cmd`, `/pkg/domain`, `/pkg/client`, `/pkg/marketdata`, `/pkg/trading`, `/pkg/account`, `/internal/auth`).
2. Define domain models, custom types using `decimal.Decimal`, and standardized custom error types.
3. Implement the cryptographic HMAC signer and configuration options for Sandbox/Production environments.
4. Set up `golangci-lint` configurations and initial Makefile commands.

### Phase 2: REST Client & Trading/Account Services
1. Build the HTTP transport layer with rate-limiting middleware, retry logic, and interceptors.
2. Implement REST wrappers for Trading (Orders, Idempotency) and Account/Position endpoints.
3. Write robust table-driven unit tests and mock server test suites.

### Phase 3: Real-Time MQTT Market Data Engine
1. Build the MQTT connection manager with auto-reconnection state machines and heartbeat checks.
2. Implement zero-allocation memory optimization patterns (`sync.Pool`) for high-frequency tick parsing loops.
3. Write integration and fuzz tests for data packet deserialization.

### Phase 4: DevOps, Observability, and Production Hardening
1. Integrate `log/slog` structured logging and OpenTelemetry hooks.
2. Construct GitHub Actions CI/CD workflows for linting, security scanning (`govulncheck`, `gosec`), testing (`-race`), and automated releases (`goreleaser`).
3. Compile the comprehensive `README.md`, GoDoc references, and runnable `/examples/`.

---

### Cross-Cutting Delivery Contract

Apply these gates to the Webull SDK:

* **Documentation-backed implementation:** Verify REST, MQTT, and gRPC endpoint paths, authentication, payload schemas, rate limits, reconnect behavior, and regional differences against official Webull documentation. Record unresolved assumptions in `docs/compatibility-matrix.md`.
* **Environment safety:** Default to mocks, paper, sandbox, or dry-run mode. Require an explicit live-trading configuration gate, and never place live orders in CI or examples.
* **Order safety:** Classify operations as read-only, idempotent, or non-idempotent. After an ambiguous order write, reconcile through client correlation, broker order status, or open-order queries before retrying. Never treat a timeout as rejection.
* **Stream recovery:** Track MQTT subscriptions and gRPC stream state, detect stale or missing events, bound queues, and resynchronize authoritative order/account state after reconnects.
* **Security evidence:** Test secret redaction, timestamp/signature validation where applicable, TLS settings, bounded payload allocation, malformed-frame rejection, and credential leakage through logs or traces.
* **Definition of done:** Do not claim production readiness until implementation, focused tests, `go test -race`, fuzz smoke tests, documentation, examples, CI configuration, coverage, and known limitations are verified and reported.
