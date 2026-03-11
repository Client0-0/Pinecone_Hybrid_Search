# 🏨 Pinecone Hybrid Search — Hotel Review Search Engine

A production-style **semantic search pipeline** built on top of Pinecone's vector database, demonstrating the **Database Fetch Pattern** — where the search index stores only lightweight metadata and the full text is fetched from a separate data store at query time.

The app lets you search 500 hotel reviews using natural language queries, powered by dense vector embeddings, Pinecone vector retrieval, and local cross-encoder reranking.

---

## Architecture Overview

```
User Query
    │
    ▼
[1] Pinecone Inference API
    └─ Embeds query → 1024-dim dense vector
    │
    ▼
[2] Pinecone Vector Index  (optional metadata filter)
    └─ ANN search, top-k=50 matches returned (ID + lightweight metadata only)
    │
    ▼
[3] Local CSV / Pandas DataFrame  (simulates SQL/NoSQL database)
    └─ IDs from Pinecone → full review text fetched by row ID
    │
    ▼
[4] Cross-Encoder Reranker  (BAAI/bge-reranker-base, runs locally)
    └─ Scores all 50 (query, text) pairs → sorts by semantic relevance
    │
    ▼
[5] Top-5 Results displayed in Streamlit UI
```

### Why the Database Fetch Pattern?

Storing large text blobs inside Pinecone is wasteful — you pay for metadata storage and it slows upserts. Instead:

- **Pinecone** stores: `id`, `embedding vector`, lightweight metadata (`hotel_name`, `city`)
- **The CSV** (simulating a database) stores: the full `reviews.text`
- At query time, Pinecone returns IDs → we do a fast in-memory lookup to get the full text for reranking

This mirrors real-world architectures where Pinecone sits alongside PostgreSQL, MongoDB, or Elasticsearch.

---

## Project Structure

```
pinecone-hybrid-search/
│
├── app.py              # Streamlit UI — the main search interface (read-only)
├── index_data.py       # One-time data ingestion script — populates Pinecone index
├── run_search.py       # CLI testing script — runs the full pipeline in the terminal
│
├── AMAQA-main/         # Dataset directory
│   └── data/hotel_reviews/hotel_reviews.csv
│
├── .env                # API keys (not committed to git)
├── .gitignore
└── README.md
```

### File Responsibilities

| File | Purpose | When to Run |
|---|---|---|
| `index_data.py` | Creates the Pinecone index and upserts all 500 review embeddings | **Once**, before first use |
| `run_search.py` | CLI script to test the full search + rerank pipeline | During development / debugging |
| `app.py` | Streamlit web UI for interactive search | For demo / end-user access |

---

## Tech Stack

| Component | Technology |
|---|---|
| Vector Database | [Pinecone](https://pinecone.io) (Serverless, AWS us-east-1) |
| Embedding Model | `multilingual-e5-large` via Pinecone Inference API (1024 dims, cosine) |
| Reranker | `BAAI/bge-reranker-base` via `sentence-transformers` (runs locally) |
| Dataset | Hotel reviews CSV, first 500 rows |
| UI Framework | Streamlit |
| Language | Python 3.12+ |

---

## Prerequisites

- Python 3.10+
- A [Pinecone account](https://app.pinecone.io) with an API key
- The hotel reviews dataset (included in `AMAQA-main/`)

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd pinecone-hybrid-search
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install pinecone sentence-transformers streamlit pandas python-dotenv tqdm
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
PINECONE_API_KEY=your-pinecone-api-key-here
```

> ⚠️ The `.env` file is gitignored — never commit your API key.

---

## Usage

### Step 1 — Index Your Data (Run Once)

This script reads the hotel reviews CSV, generates embeddings using Pinecone Inference, and upserts them into a Pinecone serverless index.

```bash
python index_data.py
```

**What it does:**
- Creates the `multilingual-e5-large-index` Pinecone index if it doesn't exist
- Reads the first 500 rows of `hotel_reviews.csv`
- Batches them (90 reviews per batch) and generates 1024-dim embeddings
- Upserts vectors with metadata: `{ hotel_name, city, review_text }`

> You only need to run this **once**. The index persists in Pinecone between sessions.

---

### Step 2a — Run the Streamlit App (Recommended)

```bash
streamlit run app.py
```

Opens a browser UI at `http://localhost:8501`. Type a natural language query and click **Search**.

**Example queries:**
- `"The room was dirty and the staff was rude"`
- `"Great location near the park, amazing breakfast"`
- `"Loud noise all night, couldn't sleep"`

---

### Step 2b — Run the CLI Test Script

Useful for quick testing without the UI:

```bash
python run_search.py
```

Uses a hardcoded query and prints the top-5 reranked results to stdout. Also demonstrates Pinecone **metadata filtering** (currently filtered to `city: "New York"`).

---

## Key Concepts

### Metadata Filtering

You can restrict Pinecone's search to a subset of documents using metadata filters:

```python
# Only search reviews from New York hotels
index.query(
    vector=query_vector,
    top_k=50,
    include_metadata=True,
    filter={"city": "New York"}
)
```

> **Important:** This filter narrows **which documents are searched**, not whether your query matches the city. If you filter by `city: "New York"` and search for `"Boston hotels"`, Pinecone will return the New York reviews most semantically similar to your query — it does not interpret the city in your query text.

**Real-world use case:** Multi-tenant isolation — `filter={"user_id": 123}` ensures each user only searches their own documents.

---

### Two-Stage Retrieval (Retrieve → Rerank)

Pinecone's ANN (Approximate Nearest Neighbour) search is extremely fast but approximate. The cross-encoder reranker is slower but highly accurate. The two-stage approach balances both:

1. **Stage 1 (Fast, approximate):** Pinecone retrieves top-50 candidates in milliseconds using ANN
2. **Stage 2 (Accurate, local):** Cross-encoder scores all 50 `(query, document)` pairs and re-orders them

The final output is top-5 results that are both fast to retrieve and accurately ranked.

---

### Embedding: Passage vs Query

The `multilingual-e5-large` model requires different `input_type` parameters depending on context:

```python
# During indexing (index_data.py) — documents are "passages"
pc.inference.embed(model=MODEL_NAME, inputs=texts, parameters={"input_type": "passage"})

# During search (app.py) — search terms are "queries"
pc.inference.embed(model=MODEL_NAME, inputs=[query_text], parameters={"input_type": "query"})
```

Using the wrong `input_type` degrades retrieval quality significantly.

---

## Pinecone Index Configuration

| Setting | Value |
|---|---|
| Index Name | `multilingual-e5-large-index` |
| Dimensions | `1024` |
| Metric | `cosine` |
| Cloud | AWS |
| Region | us-east-1 |
| Type | Serverless |

---

## Limitations & Potential Improvements

- **Dataset path is hardcoded** — move to a configurable env variable or CLI argument
- **No city filter in the UI** — could add a Streamlit `selectbox` for city/metadata filtering
- **`review_text` is stored in Pinecone metadata** (in `index_data.py`) — not necessary since we fetch from CSV; could be removed to reduce metadata storage costs
- **No caching of reranker scores** — repeated queries re-score everything
- **Single index for all users** — a real multi-tenant system would use strict `user_id` filtering or namespace isolation

---

## License

MIT
