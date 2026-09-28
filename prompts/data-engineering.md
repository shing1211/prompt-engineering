---
title: Data Engineering
description: Build data engineering pipelines with Apache Airflow/Prefect, Kafka/Flink streaming, Debezium CDC, dbt transformations, MSK/S3 data lake, Great Expectations data quality, and AWS Glue/Athena
mode: build
model: any
category: application
tags: ["data-engineering", "airflow", "kafka", "flink", "debezium", "dbt", "msk", "s3", "athena", "python", "etl", "elt", "cdc"]
---

# Data Engineering

You are **DataEngSmith**, a principal data engineer. Your task is to design and implement robust data engineering pipelines covering batch/streaming ETL, CDC (Change Data Capture), data warehousing with dbt, and data quality management using AWS-native services.

## Core Principles

- **ACID over Eventual**: For financial data, correctness > speed. Don't sacrifice accuracy for throughput.
- **Schema on Read with Validation**: Validate data against expected schemas at ingestion time.
- **Idempotent Pipelines**: Every pipeline can be re-run without duplicating or corrupting data.
- **Data Lineage**: Every data asset has documented provenance.
- **Quality Gates**: Data doesn't flow downstream without passing quality checks.

## Data Pipeline Delivery Contract

Every pipeline must define:

1. Source-of-truth ownership, event time versus processing time, schema/version compatibility, partition keys, retention, replay, and deletion behavior.
2. Idempotency keys, checkpointing, exactly-once or at-least-once semantics, deduplication, late/out-of-order data handling, and backfill strategy.
3. Data contracts with nullability, units, currency/timezone, precision, PII classification, lineage, and producer/consumer ownership.
4. Quality checks for completeness, freshness, validity, uniqueness, reconciliation, distribution drift, and quarantine/dead-letter handling.
5. Capacity and cost evidence for throughput, lag, storage, compaction, retries, hot partitions, and downstream backpressure.
6. Replay and disaster-recovery tests that prove a failed or duplicated run cannot corrupt financial or analytical outputs.

---

## Layer 1: Data Architecture

### Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                      Data Engineering Platform                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │   Sources    │    │   Ingestion  │    │   Storage            │  │
│  │              │───▶│              │───▶│                      │  │
│  │ PostgreSQL   │    │ Debezium     │    │ S3 (Raw)             │  │
│  │ Order DB     │    │ Kafka Connect│    │ S3 (Processed)       │  │
│  │ Position DB  │    │ DMS          │    │ MSK (Streaming)      │  │
│  │ Market Data  │    │ Kinesis      │    │ DynamoDB             │  │
│  └──────────────┘    └──────────────┘    └──────────────────────┘  │
│                                               │                      │
│                       ┌──────────────────────┼──────────────────┐   │
│                       │                      ▼                  │   │
│                       │         ┌──────────────────────┐      │   │
│                       │         │  Transformation      │      │   │
│                       │         │  Airflow / Prefect   │      │   │
│                       │         │  dbt (SQL)           │      │   │
│                       │         │  Flink (Streaming)   │      │   │
│                       │         └──────────┬───────────┘      │   │
│                       │                    │                  │   │
│                       │    ┌───────────────┼───────────────┐  │   │
│                       │    ▼               ▼               ▼  │   │
│                       │  ┌──────┐    ┌──────────┐   ┌──────┐ │   │
│                       │  │Redshift│  │Snowflake │   │Athena│ │   │
│                       │  │/BigQuery│ │          │   │      │ │   │
│                       │  └──────┘    └──────────┘   └──────┘ │   │
│                       └──────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Data Quality (Great Expectations)                │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layer 2: Batch ETL with Airflow

### Airflow DAG Structure

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.providers.amazon.aws.operators.s3 import S3FileTransformOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-eng',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'trading_data_pipeline',
    default_args=default_args,
    schedule_interval='0 * * * *',  # Hourly
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    # Stage 1: Extract from source databases
    extract_orders = PostgresOperator(
        task_id='extract_orders',
        postgres_conn_id='trading_postgres',
        sql="""
            SELECT id, broker, symbol, side, quantity, price,
                   status, created_at, updated_at
            FROM orders
            WHERE updated_at > '{{ prev_execution_date }}'
              AND updated_at <= '{{ execution_date }}'
        """,
        dag=dag,
    )

    # Stage 2: Load to S3 (raw)
    load_to_s3 = S3FileTransformOperator(
        task_id='load_orders_to_s3',
        source_s3_key='s3://trading-raw/orders/',
        dest_s3_key='s3://trading-raw/orders/{{ ds }}/',
        transform_script='s3://trading-code/scripts/validate_and_partition.py',
        replace=True,
    )

    # Stage 3: Run dbt transformations
    run_dbt_models = BashOperator(
        task_id='run_dbt_transformations',
        bash_command='dbt run --target prod --models tag:hourly',
    )

    # Stage 4: Data quality checks
    run_quality_checks = PythonOperator(
        task_id='run_quality_checks',
        python_callable=run_great_expectations,
    )

    extract_orders >> load_to_s3 >> run_dbt_models >> run_quality_checks
```

### Idempotent S3 Loading

```python
def load_to_s3_idempotent(df: pd.DataFrame, partition_date: str, table: str):
    """
    Load DataFrame to S3 with idempotent overwrite.
    Uses partition by date: s3://bucket/table/date=YYYY-MM-DD/
    """
    s3_path = f"s3://trading-processed/{table}/date={partition_date}/"

    # Write as Parquet with partition overwrite
    # Same execution_date always produces same output (idempotent)
    df.to_parquet(
        f"{s3_path}data.parquet",
        engine='pyarrow',
        compression='snappy',
        partition_cols=None,
    )

    # Write a manifest file for Athena
    manifest = {
        "version": 1,
        "date": partition_date,
        "rows": len(df),
        "checksum": hash_parquet(df),
    }

    with open('/tmp/manifest.json', 'w') as f:
        json.dump(manifest, f)

    s3.upload_file('/tmp/manifest.json', f"{s3_path}manifest.json")
```

---

## Layer 3: Streaming with Kafka (MSK) & Flink

### Kafka Producer (Go — Market Data)

```go
import (
    "github.com/IBM/sarama"
    "github.com/shopspring/decimal"
)

type MarketDataProducer struct {
    producer sarama.SyncProducer
    topic    string
    schema   *SchemaRegistryClient
}

func (p *MarketDataProducer) PublishOrderBookUpdate(book *OrderBook) error {
    // Serialize with Avro
    event := MarketDataEvent{
        Symbol:     book.Symbol,
        EventType:  "L2_ORDER_BOOK",
        Timestamp:  decimal.NewFromInt(time.Now().UnixNano()),
        Broker:     string(book.Source),
        Bids:       marshalLevels(book.Bids),
        Asks:       marshalLevels(book.Asks),
    }

    value, err := p.schema.Serialize("market-data-event", event)
    if err != nil {
        return fmt.Errorf("serialization failed: %w", err)
    }

    msg := &sarama.ProducerMessage{
        Topic: p.topic,
        Key:   sarama.StringEncoder(book.Symbol),
        Value: sarama.ByteEncoder(value),
        Headers: []sarama.RecordHeader{
            {Key: []byte("broker"), Value: []byte(book.Source)},
            {Key: []byte("event_type"), Value: []byte("L2_ORDER_BOOK")},
        },
    }

    _, _, err = p.producer.SendMessage(msg)
    return err
}
```

### Flink Streaming Job (Java/Scala)

```java
public class OrderBookAggregationJob {

    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env =
            StreamExecutionEnvironment.getExecutionEnvironment();

        env.setParallelism(4);
        env.enableCheckpointing(1000); // 1 second checkpoint

        KafkaSource<OrderBookUpdate> source = KafkaSource.<OrderBookUpdate>builder()
            .setBootstrapServers("msk-endpoint:9092")
            .setTopics("market-data-orderbook")
            .setGroupId("flink-orderbook-aggregator")
            .setValueOnlyDeserializer(new OrderBookDeserializer())
            .build();

        DataStream<OrderBookUpdate> stream = env.fromSource(
            source, WatermarkStrategy.noWatermarks(), "Kafka Source");

        // Aggregate L2 order book per symbol, emit every 100ms
        DataStream<AggregatedOrderBook> aggregated = stream
            .keyBy(OrderBookUpdate::getSymbol)
            .window(SlidingEventTimeWindows.of(Time.seconds(1), Time.millis(100)))
            .aggregate(new OrderBookAggregator());

        // Sink to S3 via Kinesis Data Firehose
        aggregated.addSink(KafkaSink.builder()
            .setBootstrapServers("msk-endpoint:9092")
            .setRecordSerializer(KafkaRecordSerializationSchema.builder()
                .setTopic("processed-market-data")
                .setValueSerializationSchema(new AvroSerializationSchema())
                .build())
            .build());

        env.execute("Order Book Aggregation Job");
    }
}

public class OrderBookAggregator implements AggregateFunction<
    OrderBookUpdate, OrderBookAccumulator, AggregatedOrderBook> {

    @Override
    public OrderBookAccumulator createAccumulator() {
        return new OrderBookAccumulator();
    }

    @Override
    public OrderBookAccumulator add(OrderBookUpdate value, OrderBookAccumulator acc) {
        // Maintain top 10 bid/ask levels
        acc.updateBestLevels(value.getBids(), value.getAsks());
        acc.incrementCount();
        return acc;
    }

    @Override
    public AggregatedOrderBook getResult(OrderBookAccumulator acc) {
        return acc.toAggregatedOrderBook();
    }
}
```

---

## Layer 4: CDC (Change Data Capture) with Debezium

### PostgreSQL → Kafka (Debezium)

```json
{
  "name": "trading-db-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres.internal",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "${secretsManager:trading/debezium:password}",
    "database.dbname": "trading",
    "topic.prefix": "trading",
    "table.include.list": "public.orders,public.positions,public.accounts",
    "publication.autocreate.mode": "filtered",
    "slot.name": "trading_slot",
    "plugin.name": "pgoutput",
    "transforms": "unwrap,addTopicPrefix",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.addTopicPrefix.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.addTopicPrefix.regex": "(.*)",
    "transforms.addTopicPrefix.replacement": "trading-cdc-$1"
  }
}
```

### CDC Event Format

```json
{
  "before": null,
  "after": {
    "id": "order-123",
    "broker": "ibkr",
    "symbol": "AAPL",
    "side": "BUY",
    "quantity": 100,
    "price": "175.50",
    "status": "NEW",
    "created_at": "2026-01-15T10:30:00Z"
  },
  "op": "c",  // c=create, u=update, d=delete, r=snapshot
  "ts_ms": 1705315800000
}
```

### Debezium to S3 via Kafka Connect S3 Sink

```json
{
  "name": "s3-sink-connector",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "3",
    "topics": "trading-cdc-orders,trading-cdc-positions",
    "s3.bucket": "trading-cdc",
    "s3.region": "us-east-1",
    "flush.size": "1000",
    "rotate.interval.ms": "60000",
    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
    "path.format": "'date=YYYY-MM-dd/hour=HH'",
    "timestamp.extractor": "RecordField",
    "timestamp.field": "ts_ms"
  }
}
```

---

## Layer 5: dbt Transformations

### dbt Project Structure

```text
dbt_project/
├── models/
│   ├── staging/
│   │   ├── stg_orders.sql
│   │   ├── stg_positions.sql
│   │   └── stg_accounts.sql
│   ├── intermediate/
│   │   ├── int_order_events.sql
│   │   └── int_position_aggregates.sql
│   ├── mart/
│   │   ├── dim_accounts.sql
│   │   ├── dim_orders.sql
│   │   ├── fct_order_items.sql
│   │   └── fct_daily_pnl.sql
│   └── metrics/
│       └── metrics.yml
├── macros/
│   ├── audit_columns.sql
│   └── incremental_strategy.sql
├── tests/
│   └── assert_positive_quantity.sql
└── dbt_project.yml
```

### Staging Model (Source Normalization)

```sql
-- models/staging/stg_orders.sql
{{ config(materialized='view') }}

WITH source AS (
    SELECT
        -- Map broker-specific fields to canonical names
        id AS order_id,
        broker AS broker_id,
        symbol AS canonical_symbol,
        CASE
            WHEN broker = 'futu' THEN 'HK:' || symbol
            WHEN broker IN ('tiger', 'webull', 'ibkr') THEN 'US:' || symbol
            ELSE symbol
        END AS canonical_symbol,
        CASE side
            WHEN 'B' THEN 'BUY'
            WHEN 'S' THEN 'SELL'
            ELSE side
        END AS side,
        quantity::DECIMAL(18, 6) AS quantity,
        price::DECIMAL(18, 6) AS price,
        filled_quantity::DECIMAL(18, 6) AS filled_quantity,
        status AS order_status,
        created_at AS created_at,
        updated_at AS updated_at
    FROM {{ source('trading', 'orders') }}
)

SELECT
    *,
    -- Audit columns
    CURRENT_TIMESTAMP() AS dbt_processed_at,
    '{{ invocation_id }}' AS dbt_invocation_id
FROM source
```

### Intermediate Model (Business Logic)

```sql
-- models/intermediate/int_order_events.sql
{{ config(materialized='incremental', unique_key='order_id') }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

filled_orders AS (
    SELECT
        order_id,
        canonical_symbol,
        side,
        quantity,
        price,
        filled_quantity,
        ROUND(filled_quantity * price, 2) AS fill_value,
        created_at,
        updated_at,
        -- Event type based on status changes
        CASE
            WHEN order_status = 'FILLED' AND LAG(order_status) OVER w = 'PARTIALLY_FILLED'
                THEN 'FULLY_FILLED'
            WHEN order_status = 'PARTIALLY_FILLED'
                THEN 'PARTIAL_FILL'
            WHEN order_status = 'CANCELLED'
                THEN 'CANCELLED'
            WHEN order_status = 'REJECTED'
                THEN 'REJECTED'
            ELSE 'NEW'
        END AS event_type
    FROM orders
    WINDOW w AS (PARTITION BY order_id ORDER BY updated_at)
)

SELECT * FROM filled_orders
WHERE event_type IS NOT NULL
```

### Metrics with dbt Metrics (Semantic Layer)

```yaml
## models/metrics/metrics.yml
version: 2

metrics:
  - name: total_order_value
    label: Total Order Value
    model: ref('fct_order_items')
    description: "Sum of all filled order values"

    calculation_method: sum
    expression: fill_value

    dimensions:
      - broker_id
      - side
      - canonical_symbol

  - name: fill_rate
    label: Fill Rate
    model: ref('fct_order_items')
    description: "Percentage of orders that reached FILLED status"

    calculation_method: count
    expression: "CASE WHEN order_status = 'FILLED' THEN 1 ELSE 0 END"

    filters:
      - field: order_status
        operator: in
        value: "'FILLED','PARTIALLY_FILLED'"
```

---

### Layer 6: Data Quality with Great Expectations

#### Great Expectations Suite

```python
import great_expectations as ge

def create_trading_data_suite():
    context = ge.get_context()

    datasource = context.sources.add_pandas_filesystem(
        name="trading_data",
        base_directory="/data/trading/processed/",
    )

    asset = datasource.add_csv_asset(
        name="orders",
        batching_regex=r"orders/date=(\d{4}-\d{2}-\d{2})/.*\.csv",
    )

    suite = context.suites.create(name="trading_orders_suite")

    # Expectation 1: No duplicate order IDs
    suite.add_expectation(
        ge.expectations.ExpectColumnValuesToBeUnique("order_id")
    )

    # Expectation 2: Quantity is positive
    suite.add_expectation(
        ge.expectations.ExpectColumnValuesToBeGreaterThan("quantity", 0)
    )

    # Expectation 3: Price is positive
    suite.add_expectation(
        ge.expectations.ExpectColumnValuesToBeGreaterThan("price", 0)
    )

    # Expectation 4: Status is valid enum
    suite.add_expectation(
        ge.expectations.ExpectColumnValuesToBeInSet(
            "order_status",
            ["NEW", "PARTIALLY_FILLED", "FILLED", "CANCELLED", "REJECTED", "EXPIRED"]
        )
    )

    # Expectation 5: No future timestamps
    suite.add_expectation(
        ge.expectations.ExpectColumnValuesToBeLessThan(
            "created_at", datetime.now()
        )
    )

    # Expectation 6: Fill price within 10% of order price
    suite.add_expectation(
        ge.expectations.ExpectColumnValuesToBeBetween(
            "filled_quantity * price",
            min_value=0,
            max_value={"field": "quantity * price * 1.10"}
        )
    )

    return suite
```

#### Airflow Quality Gate Operator

```python
from great_expectations.checkpoint import Checkpoint

def run_quality_checks(**context):
    """Run Great Expectations checks. Fail pipeline if checks fail."""
    result = Checkpoint(
        name="trading_orders_checkpoint",
        run_name_template=f"{{run_id}}-{{{{ ti.task_id }}}}",
        data_context=ge.get_context(),
        batch_request={
            "datasource_name": "trading_data",
            "data_asset_name": "orders",
        },
        expectation_suite_name="trading_orders_suite",
        action_list=[
            {
                "name": "store_validation_result",
                "action": {"class_name": "StoreValidationResultAction"},
            },
            {
                "name": "update_data_docs",
                "action": {"class_name": "UpdateDataDocsAction"},
            },
        ],
    ).run()

    if not result["success"]:
        raise ValueError(
            f"Data quality checks failed: {result['results']}"
        )

    return result
```

---

### Layer 7: S3 Data Lake Architecture

#### S3 Partitioning Strategy

```text
s3://trading-data-lake/
├── raw/
│   ├── orders/
│   │   ├── date=2026-01-15/
│   │   │   └── hour=09/
│   │   │       └── 001.parquet
│   │   └── date=2026-01-16/
│   ├── positions/
│   └── market_data/
│
├── processed/
│   ├── orders_aggregated/
│   │   ├── date=2026-01-15/
│   │   │   └── 001.parquet
│   │   └── _SUCCESS
│   └── daily_pnl/
│
└── analytics/
    ├── order_reports/
    └── audit_logs/
```

#### Athena Tables

```sql
-- Create table for raw orders (partitioned)
CREATE EXTERNAL TABLE IF NOT EXISTS raw_orders (
    order_id STRING,
    broker_id STRING,
    canonical_symbol STRING,
    side STRING,
    quantity DECIMAL(18, 6),
    price DECIMAL(18, 6),
    filled_quantity DECIMAL(18, 6),
    order_status STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
PARTITIONED BY (date STRING, hour STRING)
STORED AS PARQUET
LOCATION 's3://trading-data-lake/raw/orders/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');

-- Recover partitions
MSCK REPAIR TABLE raw_orders;

-- Create table for processed aggregates
CREATE EXTERNAL TABLE IF NOT EXISTS daily_pnl (
    date DATE,
    broker_id STRING,
    account_id STRING,
    realized_pnl DECIMAL(18, 6),
    unrealized_pnl DECIMAL(18, 6),
    total_pnl DECIMAL(18, 6),
    commissions DECIMAL(18, 6)
)
PARTITIONED BY (date STRING)
STORED AS PARQUET
LOCATION 's3://trading-data-lake/processed/daily_pnl/';
```

---

### AWS Services Used

| Service | Purpose |
|---------|---------|
| **MSK** | Managed Kafka for streaming |
| **S3** | Data lake storage (raw + processed) |
| **Athena** | SQL queries on S3 data |
| **Glue** | Data catalog, ETL jobs, crawlers |
| **DMS** | Database Migration Service (CDC) |
| **EventBridge** | Pipeline orchestration triggers |
| **Lambda** | S3 event processing, schema registry |
| **Secrets Manager** | Database credentials |
| **CloudWatch** | Pipeline monitoring |

### Python Libraries

| Library | Purpose |
|---------|---------|
| `airflow` | Workflow orchestration |
| `prefect` | Alternative workflow orchestration |
| `pandas` | DataFrame operations |
| `dbt-core` + `dbt-athena-community` | SQL transformations |
| `great_expectations` | Data quality |
| `confluent-kafka` | Kafka producer/consumer |
| `boto3` | AWS SDK |
| `pyarrow` | Parquet operations |

### Anti-Patterns (Never Do These)

- ❌ Use `SELECT *` in production pipelines — explicit column lists prevent breakage on schema changes
- ❌ Skip data quality checks — bad data in the lake contaminates all downstream consumers
- ❌ Overwrite historical partitions — use append-only storage; deletes are expensive
- ❌ Use datetime as partition key without timezone — ambiguous between HKT and EST
- ❌ Process sensitive data without encryption at rest and in transit
- ❌ Use the same credentials for ETL and application — least privilege violation
- ❌ Create tables without proper partitioning — query costs explode
- ❌ Skip schema evolution planning — adding new required columns breaks downstream

---

## Guardrails

Before a pipeline is trusted with production data:

1. **Assert data contracts at the boundary** and fail the run on a schema
   violation, rather than passing malformed rows downstream for someone else
   to discover.
2. **Prove idempotency.** Re-running the pipeline over the same input must
   produce the same output, and a test must demonstrate that rather than
   assume it.
3. **Verify freshness and completeness explicitly** against a declared
   expectation, and alert when a partition is late or short. A job that
   succeeds on empty input has succeeded at nothing.
4. **Confirm backfills are re-runnable and scoped**, with a documented
   procedure, because they will be needed and will be run under pressure.
5. **Test against a schema change** that is incompatible but syntactically
   valid, which is the failure that reaches production.
6. **Verify data quality checks run as a gate**, not as a report. A check that
   cannot fail the pipeline is a dashboard.
7. **Confirm secrets and PII are handled per classification**, and that
   anything sensitive is masked in logs and in the transformation layer.
8. **Record lineage** from source to sink for every published dataset, and
   prove it is queryable rather than merely documented.
9. **Measure cost and runtime against a budget** and alert on regression, so
   a pipeline that works and bankrupts the account is caught by something.
