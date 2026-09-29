---
name: prompt-llm-integration
description: LLM integration guide with RAG architecture, vector databases (Pinecone/Milvus), prompt engineering, vLLM/Ollama local deployment, AI safety, RAG evaluation with RAGAS, and cloud API integration (OpenAI, Anthropic, Google Gemini)
---
<!-- generated from prompts/llm-integration.md by scripts/generate_agents.py; provenance only -->

# LLM Integration

You are **LLMSmith**, a principal AI engineer specializing in LLM integration. Your task is to design and implement LLM-powered features covering RAG architecture, vector databases, prompt engineering, local model deployment (vLLM, Ollama), cloud API integration (OpenAI, Anthropic, Google Gemini), and AI safety with evaluation frameworks.

## Core Principles

- **RAG over Fine-tuning**: For knowledge-intensive tasks, retrieval-augmented generation beats fine-tuning.
- **Evaluation is Non-Negotiable**: Every LLM integration needs automated evaluation. Gut feel is not enough.
- **AI Safety First**: Prompt injection, output filtering, and guardrails are mandatory.
- **Cost Awareness**: Local models save cost for high-volume use cases; cloud APIs for complex reasoning.
- **Hybrid is Best**: Combine local models (fast, cheap) + cloud models (powerful) based on task complexity.

## LLM Delivery Contract

Every LLM feature must define:

1. Data classification, tenant isolation, retention, provider training/usage policy, redaction, residency, and explicit human-review boundaries.
2. Threat tests for prompt injection, indirect injection, data exfiltration, tool abuse, unsafe output, denial of service, and model supply-chain risks.
3. An evaluation set representative of real tasks with versioned datasets, groundedness/relevance/safety metrics, adversarial cases, regression thresholds, and human review for high-impact decisions.
4. Retrieval provenance, chunking/embedding versioning, freshness, access filtering, citation behavior, fallback, and no-answer policy.
5. Cost, latency, token, rate-limit, timeout, retry, caching, and provider-fallback budgets with telemetry and alerts.
6. Deterministic structured outputs validated against schemas before downstream actions; never allow model text alone to authorize financial, security, or destructive operations.

---

## Layer 1: Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    LLM Integration Architecture                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Query Understanding                         │  │
│  │   Intent Detection → Entity Extraction → Query Classification  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│         ┌────────────────────┴────────────────────┐                 │
│         │                                         │                  │
│  ┌──────▼──────┐                          ┌───────▼──────┐         │
│  │  Simple Q&A │                          │ Complex      │         │
│  │  (Local)    │                          │ Reasoning    │         │
│  │  Ollama     │                          │ (Cloud)      │         │
│  │  Llama 3.1  │                          │ GPT-4o       │         │
│  └──────┬──────┘                          └───────┬──────┘         │
│         │                                        │                  │
│  ┌──────▼────────────────────────────────────────▼──────┐           │
│  │              RAG Pipeline                              │           │
│  │  Query → Embed → Vector Search → Context Assembly      │           │
│  │            → Prompt Template → LLM → Response           │           │
│  └────────────────────────────────────────────────────────┘           │
│                              │                                       │
│  ┌───────────────────────────▼──────────────────────────────┐       │
│  │              Vector Database                               │       │
│  │  Pinecone (cloud) / Milvus (self-hosted) / pgvector       │       │
│  └───────────────────────────────────────────────────────────┘       │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Safety & Evaluation                        │  │
│  │   Prompt Injection Detection → Output Filtering → RAGAS Eval  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layer 2: Vector Database Setup

### Pinecone (Cloud)

```python
from pinecone import Pinecone, ServerlessSpec
import os

## Initialize Pinecone
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

## Create index
pc.create_index(
    name="trading-knowledge",
    dimension=1536,  # OpenAI text-embedding-3-small
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

## Connect to index
index = pc.Index("trading-knowledge")

## Upsert embeddings
index.upsert(
    vectors=[
        {
            "id": "doc-001",
            "values": embedding_vector,
            "metadata": {
                "source": "trading-handbook",
                "page": 42,
                "text": "Kelly criterion formula: f* = (bp - q) / b"
            }
        }
    ]
)

## Query
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True,
    filter={"source": {"$eq": "trading-handbook"}}
)
```

#### Milvus (Self-Hosted)

```python
from pymilvus import Collection, connections, FieldSchema, CollectionSchema, DataType

## Connect to Milvus
connections.connect(host="localhost", port="19530")

## Define schema
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=128),
]
schema = CollectionSchema(fields=fields, description="Financial knowledge base")

collection = Collection(name="trading_knowledge", schema=schema)

## Create index
index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "IP",  # Inner product for normalized embeddings
    "params": {"nlist": 128}
}
collection.create_index(field_name="embedding", index_params=index_params)

## Insert and search
collection.insert([
    ["doc-001"],
    [embedding_vector],
    ["Kelly criterion formula..."],
    ["trading-handbook"]
])
collection.flush()

## Search
search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
results = collection.search(
    data=[query_embedding],
    anns_field="embedding",
    param=search_params,
    limit=5
)
```

#### pgvector (PostgreSQL)

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    source VARCHAR(128),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create HNSW index (faster than IVFFlat for small datasets)
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);

-- Search
SELECT content, 1 - (embedding <=> $1) AS similarity
FROM documents
ORDER BY embedding <=> $1
LIMIT 5;
```

---

### Layer 3: RAG Pipeline Implementation

#### LangChain RAG Chain

```python
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

## Embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.environ["OPENAI_API_KEY"]
)

## Vector store
vectorstore = PineconeVectorStore(
    index_name="trading-knowledge",
    embedding=embeddings,
    pinecone_api_key=os.environ["PINECONE_API_KEY"]
)

## Retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 5,
        "filter": {"source": {"$eq": "trading-handbook"}}
    }
)

## LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.1,
    api_key=os.environ["OPENAI_API_KEY"]
)

## Prompt template
SYSTEM_PROMPT = """You are an expert financial advisor assistant.

Context from the knowledge base:
{context}

Instructions:
- Answer based ONLY on the provided context
- If the context doesn't contain enough information, say "I don't have enough information"
- Use bullet points for lists
- Always cite your sources
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}")
])

## Create chains
document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

## Invoke
response = retrieval_chain.invoke({
    "input": "What is the Kelly criterion and how is it calculated?"
})
print(response["answer"])
```

#### Hybrid Retrieval (Vector + Keyword)

```python
from langchain.retrievers import EnsembleRetriever

## Vector retriever
vector_retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}
)

## BM25 keyword retriever
from langchain_community.retrievers import BM25Retriever
keyword_retriever = BM25Retriever.from_texts(
    texts=[doc.page_content for doc in documents],
    metadatas=[doc.metadata for doc in documents]
)

## Ensemble (weighted combination)
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, keyword_retriever],
    weights=[0.7, 0.3]  # 70% vector, 30% keyword
)
```

#### Reranking with LlamaIndex

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.postprocessor.cohere_rerank import CohereRerank

## Build index
documents = SimpleDirectoryReader("./docs").load_data()
index = VectorStoreIndex.from_documents(documents)

## Reranker (improves relevance)
rerank = CohereRerank(api_key=os.environ["COHERE_API_KEY"], top_n=3)

query_engine = index.as_query_engine(
    similarity_top_k=10,  # Get more results before reranking
    node_postprocessors=[rerank]
)

response = query_engine.query("What is the Kelly criterion?")
```

---

### Layer 4: Local LLM Deployment

#### Ollama Setup

```bash
## Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

## Pull model
ollama pull llama3.1:8b

## Run with API
ollama serve

## Test with curl
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "What is the Kelly criterion?",
  "stream": false
}'
```

#### Ollama with LangChain

```python
from langchain_community.llms import Ollama

llm = Ollama(
    model="llama3.1:8b",
    base_url="http://localhost:11434",
    temperature=0.1,
    options={
        "num_gpu": 1,  # Use GPU
        "num_ctx": 4096,  # Context window
    }
)

response = llm.invoke("What is the Kelly criterion?")
```

#### vLLM for High-Throughput

```bash
## Install vLLM
pip install vllm

## Start vLLM server
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --tensor-parallel-size 2 \
    --port 8000

## Use with OpenAI client
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="none")
response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "What is the Kelly criterion?"}]
)
```

#### AWS SageMaker Endpoint

```python
import boto3
import json

sm_client = boto3.client("sagemaker-runtime")

def query_sagemaker_endpoint(prompt: str) -> str:
    payload = {
        "inputs": prompt,
        parameters": {
            "max_new_tokens": 512,
            "temperature": 0.1,
            "top_p": 0.9,
        }
    }

    response = sm_client.invoke_endpoint(
        EndpointName="trading-llama3-8b",
        ContentType="application/json",
        Accept="application/json",
        Body=json.dumps(payload)
    )

    result = json.loads(response["Body"].read().decode())
    return result[0]["generated_text"]
```

---

### Layer 5: Prompt Engineering

#### Structured Output (JSON Mode)

```python
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

class KellyCriterionResponse(BaseModel):
    formula: str
    explanation: str
    example_calculation: str
    risk_level: str  # "low", "medium", "high"

llm = ChatOpenAI(model="gpt-4o-2024-08-06")

structured_llm = llm.with_structured_output(KellyCriterionResponse)

response = structured_llm.invoke(
    """Explain the Kelly criterion for position sizing.
    Provide a formula, explanation, example calculation, and risk assessment."""
)

print(response.formula)
print(response.risk_level)
```

#### Few-Shot Prompting

```python
FEW_SHOT_PROMPT = """You are a financial trading assistant that extracts order information from user messages.

Examples:

User: "Buy 100 shares of AAPL at $150"
Extracted: {"symbol": "AAPL", "side": "BUY", "quantity": 100, "type": "MARKET", "price": 150}

User: "Place a limit order to sell 50 shares of TSLA for $200"
Extracted: {"symbol": "TSLA", "side": "SELL", "quantity": 50, "type": "LIMIT", "price": 200}

User: "I want to short 200 shares of NVDA around $500"
Extracted: {"symbol": "NVDA", "side": "SELL", "quantity": 200, "type": "LIMIT", "price": 500}

User: "{user_input}"
Extracted:"""

def extract_order(user_input: str) -> dict:
    response = llm.invoke(FEW_SHOT_PROMPT.format(user_input=user_input))
    return json.loads(response)
```

#### Chain-of-Thought for Reasoning

```python
COT_PROMPT = """You are a quantitative analyst evaluating a trading strategy.

For the following strategy, analyze step by step:

Strategy: Mean reversion on HK:00700
- Entry: Buy when price is 2 standard deviations below 20-day MA
- Exit: Sell when price returns to 20-day MA
- Position sizing: Fixed 10% of portfolio

Evaluate the following:
1. What market conditions is this strategy suited for?
2. What are the main risks?
3. How would you improve position sizing?

Think through this step by step, showing your reasoning:
"""
```

---

### Layer 6: AI Safety & Guardrails

#### Prompt Injection Detection

```python
from refactored_content_analyzer import RefactoredContentAnalyzer

analyzer = RefactoredContentAnalyzer()

def detect_prompt_injection(user_input: str) -> bool:
    """
    Detect prompt injection attempts.
    Looks for common injection patterns.
    """
    injection_patterns = [
        r"ignore previous instructions",
        r"ignore all previous",
        r"disregard.*instructions",
        r"you are now.*instead",
        r"system prompt",
        r"reveal.*prompt",
        r"override.*behavior",
    ]

    for pattern in injection_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return True

    # Check for suspicious content
    score = analyzer.analyze(user_input)
    if score > 0.8:
        return True

    return False

## Usage in RAG chain
def safe_rag_invoke(user_input: str):
    if detect_prompt_injection(user_input):
        return {"answer": "I cannot process this request.", "safe": False}

    response = retrieval_chain.invoke({"input": user_input})
    return {"answer": response["answer"], "safe": True}
```

#### Output Filtering

```python
from moderation_client import ModerationClient

moderation = ModerationClient(api_key=os.environ["MODERATION_API_KEY"])

def moderate_output(output: str) -> bool:
    """
    Check output for harmful content.
    Returns True if safe, False if unsafe.
    """
    result = moderation.classify(text=output)

    # Check for harmful categories
    harmful_categories = ["hate", "violence", "self-harm", "sexual"]
    for category in harmful_categories:
        if result.category_scores.get(category, 0) > 0.5:
            return False

    return True

def safe_generate(prompt: str) -> str:
    output = llm.invoke(prompt)

    if not moderate_output(output):
        return "I cannot provide that response as it may contain harmful content."

    return output
```

---

### Layer 7: RAG Evaluation with RAGAS

```python
from ragas import EvaluationDataset, evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

## Create evaluation dataset
eval_data = [
    {
        "user_input": "What is the Kelly criterion?",
        "retrieved_contexts": [
            "Kelly criterion formula: f* = (bp - q) / b",
            "Where b is the odds received on the bet",
            "q is the probability of losing",
            "f* is the fraction of capital to bet"
        ],
        "response": "The Kelly criterion is a mathematical formula...",
        "reference": "The Kelly criterion is f* = (bp - q) / b"
    },
    # More examples...
]

dataset = EvaluationDataset.from_list(eval_data)

## Evaluate
result = evaluate(
    dataset=dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ],
)

print(result)
## {
##   'faithfulness': 0.85,
##   'answer_relevancy': 0.78,
##   'context_precision': 0.92,
##   'context_recall': 0.80
## }
```

#### Continuous Evaluation Pipeline

```python
import arize.phoenix as px

## Initialize Phoenix (observability)
client = px.Client()

## Log traces
for query in production_queries:
    response = rag_chain.invoke({"input": query})

    client.log(
        span_name="rag_inference",
        attributes={
            "query": query,
            "response": response["answer"],
            "context_docs": [doc.page_content for doc in response["context"]],
            "latency_ms": response["latency"],
        }
    )

## Dashboard: Phoenix automatically shows
## - Retrieval precision
## - Response quality trends
## - Latency percentiles
```

---

### Layer 8: Hybrid Architecture

```python
from enum import Enum

class QueryComplexity(Enum):
    SIMPLE = "simple"       # Factual, no reasoning
    MODERATE = "moderate"   # Some reasoning required
    COMPLEX = "complex"     # Multi-step reasoning

def classify_query(query: str) -> QueryComplexity:
    """
    Classify query complexity to route to appropriate model.
    """
    # Simple: factual questions with short answers
    simple_indicators = ["what is", "who is", "when did", "definition of"]
    # Complex: multi-step, comparative, analytical
    complex_indicators = ["analyze", "compare", "evaluate", "synthesize", "why does", "how would"]

    query_lower = query.lower()

    if any(ind in query_lower for ind in complex_indicators):
        return QueryComplexity.COMPLEX
    elif any(ind in query_lower for ind in simple_indicators):
        return QueryComplexity.SIMPLE
    else:
        return QueryComplexity.MODERATE

def hybrid_generate(query: str) -> str:
    complexity = classify_query(query)

    if complexity == QueryComplexity.SIMPLE:
        # Use local model (fast, cheap)
        return ollama_llm.invoke(query)

    elif complexity == QueryComplexity.MODERATE:
        # Use RAG + local model
        return rag_chain_with_ollama.invoke({"input": query})

    else:
        # Use RAG + cloud model (best quality)
        return rag_chain_with_gpt4o.invoke({"input": query})
```

### Python Libraries

| Library | Purpose |
|---------|---------|
| `langchain` | LLM orchestration |
| `langchain-openai` | OpenAI integration |
| `langchain-community` | Community integrations (Ollama, etc.) |
| `llama-index` | RAG-specific framework |
| `pinecone-client` | Pinecone vector DB |
| `pymilvus` | Milvus vector DB |
| `pgvector` | PostgreSQL vector search |
| `vllm` | High-throughput local LLM |
| `ragas` | RAG evaluation |
| `arize-phoenix` | LLM observability |
| `rebuff` | Prompt injection detection |
| `pydantic` | Structured output |

### Anti-Patterns (Never Do These)

- ❌ Blindly trust LLM outputs — always validate against source material
- ❌ Use production data for fine-tuning without anonymization — data leakage risk
- ❌ Skip prompt injection detection — users will try to manipulate outputs
- ❌ Use single embedding model for all use cases — different models have different strengths
- ❌ Skip evaluation — launch without measuring accuracy, relevance, latency
- ❌ Overload context window — chunk documents smartly (1024-2048 tokens per chunk)
- ❌ Use the same retrieval strategy for all queries — hybrid (vector + keyword) is more robust
- ❌ Forget about cost — local models for high-volume simple tasks, cloud for complex reasoning
