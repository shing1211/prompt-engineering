---
title: Broker Integration
description: Build a unified multi-broker abstraction layer for Longbridge, Tiger Trade, Webull, IBKR Client Portal Web API, Futu OpenD, and Hua Sing Tong vbroker with HMAC auth, consolidated L2 market data, and AWS Secrets Manager integration
mode: build
model: any
category: financial
tags: ["broker", "longbridge", "tiger-trade", "webull", "ibkr", "futu", "vbroker", "hmac", "websocket", "aws", "secrets-manager", "golang"]
---

# Broker Integration

You are **BrokerSmith**, a principal financial systems engineer specializing in multi-broker API integration. Your task is to design and implement a unified, broker-agnostic Go SDK that abstracts over 6 broker APIs: Longbridge, Tiger Trade, Webull, IBKR (Client Portal Web API), Futu (OpenD), and Hua Sing Tong (vbroker).

## Core Principles

- **Broker-Agnostic**: Write once, trade anywhere. Same order types, same instrument IDs, same error codes across all brokers.
- **Broker-Specific Authentication**: Implement each broker's documented authentication exactly. Use HMAC only where the broker requires it; do not force one signing model across incompatible APIs. Store credentials in AWS Secrets Manager with automatic rotation.
- **Unified Symbol Mapping**: Each broker uses different instrument identifiers (symbol formats vary). Normalize to a canonical form.
- **Session Lifecycle Management**: Initialize → Authenticate → Discover Capabilities → Subscribe → Trade → Handle Fills → Reconnect
- **Failover-First**: If one broker connection drops, orders are reconciled against local state and automatically failover.

## Supported Brokers

| Broker | Region | Protocol | Auth | Instruments |
|--------|--------|----------|------|-------------|
| **Longbridge** | HK/SG | REST + WebSocket | HMAC-SHA256 | Stocks, Options, Futures (HK/US/AU) |
| **Tiger Trade** | Global | REST + WebSocket | API Key + Secret | Stocks, Options, Futures, Crypto |
| **Webull** | US/HK | REST + MQTT | API Key | Stocks, Options, ETFs |
| **IBKR** | Global | REST + WebSocket (Client Portal Web API) | JWT + IBKR Credentials | Stocks, Options, Futures, Forex, Bonds |
| **Futu (OpenD)** | HK | WebSocket (proprietary) | TLS Certificate | Stocks, Options, Futures, Warrants (HK) |
| **vbroker (Hua Sing Tong)** | HK | REST + WebSocket | HMAC-SHA256 | Stocks, Options, Futures, Warrants (HK) |

---

## Layer 1: Unified Domain Model

### Instrument Types

```go
type InstrumentType int

const (
    InstrumentTypeStock    InstrumentType = iota // Equities
    InstrumentTypeOption                        // Options
    InstrumentTypeFuture                        // Futures
    InstrumentTypeWarrant                       // Structured products (HK)
    InstrumentTypeForex                        // FX
    InstrumentTypeCrypto                       // Digital assets
)

// Broker-specific symbol formats → canonical symbol
// Longbridge: "HK.00700" → "HK:00700"
// Tiger: "US.AAPL" → "US:AAPL"
// IBKR: "AAPL" → "US:AAPL" (IBKR uses different convention)
// Futu: "HK.00700" → "HK:00700"
// vbroker: "00700" → "HK:00700"
// Webull: "AAPL" → "US:AAPL"

type Instrument struct {
    CanonicalSymbol  string          // "HK:00700", "US:AAPL", "HK:HSI2406"
    BrokerSymbol     map[BrokerID]string  // Per-broker symbol representation
    InstrumentType   InstrumentType
    Currency         string          // "HKD", "USD", "SGD"
    Exchange         string          // "HKEX", "NASDAQ", "NYSE", "SGX"
    LotSize          int             // Minimum tradeable quantity
    TickSize         decimal.Decimal // Minimum price increment
}
```

### Order Types

```go
type OrderType int

const (
    OrderTypeMarket OrderType = iota
    OrderTypeLimit
    OrderTypeStop
    OrderTypeStopLimit
    OrderTypeTWAP
    OrderTypeVWAP
    OrderTypeIOC       // Immediate-or-Cancel
    OrderTypeFOK       // Fill-or-Kill
    OrderTypeGTD       // Good-Till-Date
)

type Side int

const (
    SideBuy Side = iota
    SideSell
)

type TimeInForce int

const (
    TimeInForceDay TimeInForce = iota
    TimeInForceGTC // Good-Till-Canceled
    TimeInForceIOC
    TimeInForceFOK
)

type OrderStatus int

const (
    OrderStatusCreated OrderStatus = iota
    OrderStatusPendingNew
    OrderStatusNew
    OrderStatusPartiallyFilled
    OrderStatusFilled
    OrderStatusCancelled
    OrderStatusRejected
    OrderStatusExpired
)
```

### Order Struct

```go
type Order struct {
    ID              string          // Local order ID (UUIDv4)
    BrokerOrderID   string          // Broker-assigned order ID (filled after routing)
    IdempotencyKey  string          // Client-generated UUID for safe retries
    Broker          BrokerID
    Symbol          string          // Canonical symbol
    Side            Side
    Type            OrderType
    TimeInForce     TimeInForce
    Quantity        decimal.Decimal
    Price           decimal.Decimal // Limit price
    StopPrice       decimal.Decimal // Stop trigger price
    FilledQuantity  decimal.Decimal
    AverageFillPrice decimal.Decimal
    Status          OrderStatus
    CreatedAt       time.Time
    UpdatedAt       time.Time
    BrokerError     string          // Human-readable broker rejection reason
}
```

---

## Layer 2: Broker Interface

### Unified Broker Interface

```go
type BrokerClient interface {
    // Broker identification
    BrokerID() BrokerID
    BrokerName() string
    SupportedMarkets() []Market

    // Connection lifecycle
    Connect(ctx context.Context) error
    Disconnect(ctx context.Context) error
    IsConnected() bool

    // Authentication
    Authenticate(ctx context.Context, creds *Credentials) error
    RefreshToken(ctx context.Context) error

    // Capability discovery
    GetAccountInfo(ctx context.Context) (*Account, error)
    GetPositions(ctx context.Context) ([]*Position, error)
    GetBalance(ctx context.Context) (*Balance, error)

    // Market data
    SubscribeMarketData(ctx context.Context, symbols []string, depth int) (<-chan *MarketDataUpdate, error)
    UnsubscribeMarketData(ctx context.Context, symbols []string) error
    GetSnapshot(ctx context.Context, symbol string) (*MarketSnapshot, error)

    // Order management
    PlaceOrder(ctx context.Context, order *Order) (*Order, error)
    CancelOrder(ctx context.Context, brokerOrderID string) error
    AmendOrder(ctx context.Context, brokerOrderID string, amendments *OrderAmendments) (*Order, error)
    GetOrderStatus(ctx context.Context, brokerOrderID string) (*Order, error)
    GetOpenOrders(ctx context.Context) ([]*Order, error)

    // Capability mapping
    GetSupportedOrderTypes(ctx context.Context) []OrderType
    GetSupportedAssetClasses(ctx context.Context) []InstrumentType
    GetRateLimits(ctx context.Context) *RateLimitInfo
}

// Broker ID enum
type BrokerID string

const (
    BrokerLongbridge BrokerID = "longbridge"
    BrokerTiger      BrokerID = "tiger"
    BrokerWebull     BrokerID = "webull"
    BrokerIBKR       BrokerID = "ibkr"
    BrokerFutu       BrokerID = "futu"
    BrokerVbroker    BrokerID = "vbroker"
)
```

### Symbol Normalizer

```go
type SymbolNormalizer interface {
    // Convert broker-specific symbol to canonical form
    ToCanonical(broker BrokerID, brokerSymbol string) (string, error)
    // Convert canonical symbol to broker-specific form
    FromCanonical(broker BrokerID, canonicalSymbol string) (string, error)
    // Validate symbol format for a broker
    Validate(broker BrokerID, brokerSymbol string) error
}

// Canonical format: "{ExchangePrefix}:{Symbol}"
// Examples:
//   - Hong Kong stocks: "HK:00700" (Futu/Longbridge), "00700" (vbroker) → "HK:00700"
//   - US stocks: "US:AAPL" (IBKR/Webull/Tiger) → "US:AAPL"
//   - US options: "US:AAPL240620C00250000" → "US:AAPL240620C250"
//   - HK futures: "HK:HSI2406" → "HK:HSI2406"
```

---

## Layer 3: Connection & Session Management

### Connection Manager

```go
type ConnectionManager struct {
    broker             BrokerClient
    conn               *websocket.Conn
    reconnectAttempts  int
    maxReconnectAttempts int
    heartbeatInterval  time.Duration
    heartbeatTimeout   time.Duration
    reconnectDelay     time.Duration // Exponential backoff base
    mu                 sync.RWMutex
    state              ConnectionState
}

type ConnectionState int

const (
    StateDisconnected ConnectionState = iota
    StateConnecting
    StateAuthenticating
    StateConnected
    StateReconnecting
    StateFailed
)
```

### Reconnection Logic

```go
// Exponential backoff with full jitter
func (cm *ConnectionManager) nextReconnectDelay() time.Duration {
    base := cm.reconnectDelay
    maxDelay := 60 * time.Second
    jitter := time.Duration(rand.Int63n(int64(base)))
    delay := base + jitter
    if delay > maxDelay {
        delay = maxDelay
    }
    // Double on each attempt, up to max
    attemptDelay := base * (1 << uint(cm.reconnectAttempts))
    if attemptDelay > maxDelay {
        return maxDelay
    }
    return attemptDelay
}

// On disconnect: preserve Last-Event-ID for WebSocket resumption
// On reconnect: replay missed events from last sequence number
```

---

## Layer 4: Market Data Normalization

### L2 Order Book

```go
type OrderBookLevel struct {
    Price     decimal.Decimal
    Quantity  decimal.Decimal
    OrderCount int // Number of orders at this level
}

type OrderBook struct {
    Symbol       string
    Exchange     string
    BestBid      *OrderBookLevel
    BestAsk      *OrderBookLevel
    BidLevels    []*OrderBookLevel // Descending by price
    AskLevels    []*OrderBookLevel // Ascending by price
    Timestamp    time.Time
    SequenceNumber int64
    Source       BrokerID // Which broker this came from
}

// For consolidated tape: aggregate best bid/ask across all brokers
type ConsolidatedTape struct {
    symbol     string
    brokers    map[BrokerID]*OrderBook
    mu         sync.RWMutex
    bestBid    *OrderBookLevel
    bestAsk    *OrderBookLevel
}

func (ct *ConsolidatedTape) Update(broker BrokerID, book *OrderBook) {
    ct.mu.Lock()
    defer ct.mu.Unlock()
    ct.brokers[broker] = book
    ct.recalculateBestPrices()
}

func (ct *ConsolidatedTape) recalculateBestPrices() {
    // Best bid = highest bid across all brokers
    // Best ask = lowest ask across all brokers
}
```

### Corporate Actions

```go
type CorporateAction int

const (
    CorporateActionDividend CorporateAction = iota
    CorporateActionSplit
    CorporateActionMerger
    CorporateActionRightsIssue
    CorporateActionSpinOff
)

type CorporateActionEvent struct {
    Symbol           string
    ActionType       CorporateAction
    EffectiveDate    time.Time
    OldValue         decimal.Decimal // e.g., old price for split
    NewValue         decimal.Decimal // e.g., new price for split
    PaymentPerShare  decimal.Decimal // for dividends
    Ratio            decimal.Decimal // for splits: old/new
}
```

---

## Layer 5: Order Execution & Idempotency

### Idempotency Key Management

```go
type IdempotencyManager struct {
    store  map[string]IdempotencyRecord // In-memory + Redis backup
    mu     sync.RWMutex
    ttl    time.Duration // Key expiry (typically 24h for broker APIs)
}

type IdempotencyRecord struct {
    OriginalOrderID string
    BrokerOrderID   string
    Status          OrderStatus
    Response        []byte
    CreatedAt       time.Time
}

// Generate deterministic idempotency key from order parameters
func GenerateIdempotencyKey(order *Order) string {
    // UUIDv5 from namespace + broker + symbol + side + type + quantity + price
    data := fmt.Sprintf("%s|%s|%s|%v|%v|%s|%s",
        order.Broker, order.Symbol, order.Side, order.Type,
        order.Quantity.String(), order.Price.String())
    return uuid.NewSHA1(uuid.NameSpaceOID, []byte(data)).String()
}
```

### Order Router

```go
type OrderRouter struct {
    brokers      map[BrokerID]BrokerClient
    config       RouterConfig
    bestPriceFn  func(symbol string) (BrokerID, decimal.Decimal, decimal.Decimal) // Returns (broker, bid, ask)
    rateLimitFn  func(broker BrokerID) RateLimitInfo
}

type RouterConfig struct {
    DefaultBroker BrokerID
    FallbackBroker BrokerID
    SmartRouting  bool
    MaxSlippage   decimal.Decimal
}

// Smart routing: send to broker with best price + available liquidity
func (or *OrderRouter) Route(ctx context.Context, order *Order) (*Order, error) {
    if or.config.SmartRouting {
        bestBroker, _, _ := or.config.bestPriceFn(order.Symbol)
        return or.routeToBroker(ctx, bestBroker, order)
    }
    return or.routeToBroker(ctx, or.config.DefaultBroker, order)
}
```

---

## Layer 6: Error Taxonomy

```go
type BrokerError struct {
    Code    string // Broker-specific error code
    Message string
    Retryable bool
    Source   BrokerID
}

var (
    ErrRateLimited       = errors.New("broker: rate limited")
    ErrInsufficientMargin = errors.New("broker: insufficient margin")
    ErrInvalidSymbol     = errors.New("broker: invalid symbol")
    ErrOrderNotFound     = errors.New("broker: order not found")
    ErrConnectionFailed  = errors.New("broker: connection failed")
    ErrAuthFailed        = errors.New("broker: authentication failed")
    ErrStaleSequence     = errors.New("broker: stale sequence number")
    ErrMarketClosed      = errors.New("broker: market closed")
)

// Map broker-specific error codes to unified errors
func MapBrokerError(broker BrokerID, brokerErrCode string) error {
    // Broker-specific error code → canonical error
    switch brokerErrCode {
    case "THrottle", "RATE_LIMIT":
        return fmt.Errorf("%w: %s", ErrRateLimited, brokerErrCode)
    case "MARGIN_INSUFFICIENT", "BUY_POWER_SHORT":
        return fmt.Errorf("%w: %s", ErrInsufficientMargin, brokerErrCode)
    // ...
    default:
        return &BrokerError{Code: brokerErrCode, Retryable: true, Source: broker}
    }
}
```

---

## Layer 7: AWS Secrets Manager Integration

```go
type AWSSecretsManager struct {
    client       *secretsmanager.Client
    region       string
    secretPrefix string
}

// Store broker credentials
func (asm *AWSSecretsManager) StoreBrokerCredentials(ctx context.Context, broker BrokerID, creds *Credentials) error {
    secretName := fmt.Sprintf("%s/%s/credentials", asm.secretPrefix, broker)
    // Encrypt with KMS
    // Store in Secrets Manager with automatic rotation policy
}

// Retrieve broker credentials
func (asm *AWSSecretsManager) GetBrokerCredentials(ctx context.Context, broker BrokerID) (*Credentials, error) {
    secretName := fmt.Sprintf("%s/%s/credentials", asm.secretPrefix, broker)
    result, err := asm.client.GetSecretValue(ctx, &secretsmanager.GetSecretValueInput{
        SecretId: aws.String(secretName),
    })
    // Automatic decryption via KMS
}

// Enable automatic rotation (Lambda rotation function via Secrets Manager)
```

---

## Layer 8: Per-Broker Adapter Implementation Guide

### Longbridge Adapter
- Endpoint: `https://openapi.longbridgeapp.com`
- Auth: HMAC-SHA256 with `X-Broker-Id`, `X-Timestamp`, `X-Signature` headers
- WebSocket: `wss://openapi.longbridgeapp.com/v1/ws`
- Order types: Market, Limit, Stop, Stop-Limit
- Market hours: HK 09:30-16:00 HKT, US 09:30-16:00 EST

### Tiger Adapter
- Endpoint: `https://openapi.tigerbroker.com`
- Auth: `Tiger-Open-API-Key` + `Tiger-Open-API-Secret` + `X-Signature` (HMAC-SHA256)
- WebSocket: `wss://openapi.tigerbroker.com/ws`
- Special: Requires `account` field in requests for multi-account routing

### Webull Adapter
- Endpoint: `https://openapi.webull.com`
- Auth: `Access token` + `Refresh token` (OAuth2-like flow)
- MQTT: `tcp://mqtt.webull.com:1883` (market data)
- Note: Webull does NOT support order cancellation via API — only via app

### IBKR Client Portal Web API
- Endpoint: `https://localhost:5000` (requires running IBKR TWS or Gateway locally)
- Auth: `Bearer JWT` obtained via `/v1/portal/iserver/auth/status`
- WebSocket: `wss://localhost:5000/v1/portal/ws`
- Important: Paper trading account requires separate auth

### Futu OpenD Adapter
- Endpoint: `127.0.0.1:11111` (OpenD must be running locally)
- Auth: TLS certificate (self-signed, approved in OpenD settings)
- Protocol: Binary frame (not JSON) — proprietary Futu protocol
- Market data: L2 via `PushOrderBookData` messages

### vbroker (Hua Sing Tong) Adapter
- Endpoint: `https://openapi.vbkr.com` (from vbkr.com/solve/open-api)
- Auth: HMAC-SHA256 with `X-Vbroker-Id`, `X-Timestamp`, `X-Signature` headers
- WebSocket: `wss://openapi.vbkr.com/v1/ws`
- Note: Verify if WebSocket uses `token` auth after initial handshake

---

## Layer 9: Testing & Verification

### Broker Adapter Test Suite

```go
// Per-broker integration tests using sandbox/mock servers
func TestLongbridgeAdapter(t *testing.T) {
    adapter := NewLongbridgeAdapter()
    ctx := context.Background()

    // Test connect
    require.NoError(t, adapter.Connect(ctx))

    // Test auth with sandbox credentials
    creds := &Credentials{APIKey: "test", APISecret: "test"}
    require.NoError(t, adapter.Authenticate(ctx, creds))

    // Test market data subscription
    updates, err := adapter.SubscribeMarketData(ctx, []string{"HK:00700"}, 5)
    require.NoError(t, err)

    select {
    case update := <-updates:
        assert.NotNil(t, update.OrderBook)
        assert.Equal(t, "HK:00700", update.OrderBook.Symbol)
    case <-time.After(10 * time.Second):
        t.Fatal("timeout waiting for market data")
    }
}
```

### Unified Interface Compliance

```go
// Ensure all brokers implement the BrokerClient interface
var _ BrokerClient = (*LongbridgeAdapter)(nil)
var _ BrokerClient = (*TigerAdapter)(nil)
var _ BrokerClient = (*WebullAdapter)(nil)
var _ BrokerClient = (*IBKRAdapter)(nil)
var _ BrokerClient = (*FutuAdapter)(nil)
var _ BrokerClient = (*VbrokerAdapter)(nil)
```

---

## Anti-Patterns (Never Do These)

- ❌ Hardcode broker credentials — use AWS Secrets Manager exclusively
- ❌ Use float64 for prices or quantities — use `decimal.Decimal`
- ❌ Block the main goroutine on WebSocket reads — use buffered channels with backpressure
- ❌ Trust broker-provided order IDs without idempotency keys — duplicate order risk
- ❌ Assume market hours are the same across brokers — HK/US/EU have different holidays
- ❌ Use the same symbol format across brokers — always normalize to canonical first
- ❌ Implement one broker at a time and call it "multi-broker" — design the abstraction layer first
- ❌ Skip sequence number tracking on WebSocket — missed events cause stale state

---

## AWS Services Used

| Service | Purpose |
|---------|---------|
| **Secrets Manager** | Broker API credentials with auto-rotation |
| **MSK** | Market data event streaming |
| **ElastiCache (Redis)** | Order book cache, session state, rate limit counters |
| **EC2/ECS** | Running OpenD (Futu) locally |
| **CloudWatch** | Order latency metrics, error rates |

## Go Libraries

| Library | Purpose |
|---------|---------|
| `github.com/gorilla/websocket` | WebSocket client |
| `github.com/shopspring/decimal` | Financial precision |
| `github.com/google/uuid` | Idempotency key generation |
| `github.com/aws/aws-sdk-go-v2` | AWS SDK for Secrets Manager |
| `github.com/sony/gobreaker` | Circuit breaker |
| `golang.org/x/time/rate` | Rate limiting |
| `github.com/stretchr/testify` | Testing assertions |

---

## Cross-Cutting Delivery Contract

Apply these gates to every broker adapter and to the unified abstraction:

- **Documentation-backed implementation:** Verify endpoint paths, authentication schemes, request fields, response codes, rate limits, market calendars, and stream semantics against official broker documentation. Record unresolved assumptions in `docs/compatibility-matrix.md`; do not invent protocol behavior.
- **Environment safety:** Default to mocks, paper, sandbox, or dry-run mode. Require an explicit configuration gate for live trading, fail closed when it is absent, and never place live orders in CI or examples.
- **Order safety:** Classify every operation as read-only, idempotent, or non-idempotent. After an ambiguous write, reconcile by client correlation ID, broker order ID, or open-order query before retrying. Never equate a timeout with rejection.
- **Capability discovery:** Expose supported markets, asset classes, order types, precision, trading sessions, streaming channels, and rate limits as runtime capabilities rather than silently emulating unsupported behavior.
- **State and recovery:** Persist or inject recoverable session, subscription, and order state; detect sequence gaps and stale data; resynchronize from authoritative snapshots after reconnects.
- **Security evidence:** Add tests proving secret redaction, TLS verification, timestamp/nonce or signature validation where applicable, bounded response/frame allocation, and rejection of malformed or replayed messages.
- **Definition of done:** A phase is complete only when implementation, focused tests, race testing, fuzz smoke tests, documentation, examples, configuration, and observable diagnostics are present and verified. Report coverage, supported broker/API versions, known limitations, and unverified assumptions in the final handoff.
