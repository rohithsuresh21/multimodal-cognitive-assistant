# Local Cognitive Assistant: State-Aware Offline RAG Pipeline

A fully private, local, and state-aware Retrieval-Augmented Generation (RAG) assistant that runs entirely offline on consumer hardware, optimized for an NVIDIA RTX 4060. Rather than relying on cloud abstractions or brittle wrappers, this project implements an end-to-end data pipeline combining high-throughput file ingestion, dense vector similarity search, deterministic state mutations, and grammar-guided local LLM orchestration.

---

## System Architecture

The application is divided into two core operational pipelines that handle separate concerns: document ingestion and conversational inference.

### Document Ingestion Pipeline

When a file is uploaded, it passes through a multi-stage asynchronous pipeline. The file handler extracts raw text from the supported format, which is then semantically chunked with token overlaps to prevent context loss at split boundaries. Each chunk is embedded using a local SentenceTransformer model and stored in a Qdrant vector collection for later retrieval.

### Conversational Runtime and RAG Loop

When a user submits a query, the system runs two processes in parallel. An intent parser feeds the message into the trust state machine, which updates behavioral indicators based on detected signals. Simultaneously, the retrieval module queries the Qdrant collection for semantically similar chunks using dense vector similarity. Both outputs are synthesized by the LLM engine, which uses Ollama with Mistral-7B under grammar-guided constraints to produce a structured JSON response sent back to the interface.

---

## Core Technical Features

**Dual-Stage Structural Ingestion**
Supports programmatic text extraction across PDF, TXT, CSV, and DOCX formats. Raw chunks are processed using semantic chunking with mathematical token overlaps to prevent contextual data loss at split boundaries.

**Dense Vector Database Querying**
Integrates a local Qdrant instance for vector storage and retrieval. The retrieval loop uses the modern query_points interface for low-latency similarity lookups across the personal memory collection.

**Grammar-Guided JSON Decoding**
Eliminates stochastic formatting errors from the LLM by constraining Mistral-7B output to valid JSON schemas via strict system execution parameters. This guarantees a reliable communication boundary between the Python parser and the frontend.

**Deterministic Trust State Machine**
An independent state management layer parses conversation payloads, mutates a trust variable based on configurable triggers, and maps the resulting behavioral mode to the UI in real time.

**High-Concurrency API Design**
Built with FastAPI to isolate the file processing and chat endpoints under explicit CORS routing, allowing both pipelines to operate independently without blocking each other.

---

## Technology Stack

| Layer | Component | Description |
|---|---|---|
| Backend Framework | FastAPI / Uvicorn | Asynchronous API gateway and network router |
| Vector Indexing | Qdrant (Local / Docker) | Dense vector database for embedding storage and retrieval |
| Embeddings Model | SentenceTransformers (all-MiniLM-L6-v2) | Locally executed embedding model |
| Inference Engine | Ollama | Local orchestration layer for quantized language models |
| Core LLM | Mistral-7B | Base language model for response generation |
| Frontend | Vanilla JS / HTML / CSS | Asynchronous dashboard that renders state changes |

---

## Repository Structure

The repository is organized around a single application package with clearly separated responsibilities:

- **main.py** — FastAPI initialization and routing
- **file_handler.py** — Multi-format document text extraction
- **ingest.py** — Semantic chunking and embedding generation
- **retrieval.py** — Qdrant client configuration and vector search
- **llm_engine.py** — System prompting, Ollama integration, and response formatting
- **trust_state.py** — TrustStateMachine class and intent mutation logic
- **templates/** — UI components and static assets
- **requirements.txt** — Python package dependencies

---

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- Docker Desktop, for running the local Qdrant vector store
- Ollama installed natively on the host machine

### Step 1: Start the Vector Database

Pull the Qdrant Docker image and run it bound to its standard network ports with a local storage volume mounted for persistence.

### Step 2: Pull the Language Model

Ensure Ollama is running in the background, then pull the Mistral model weights to your local machine.

### Step 3: Set Up the Python Environment

Clone the repository, create a virtual environment, activate it, and install the dependencies from requirements.txt.

### Step 4: Start the Application

Launch the server using Uvicorn pointed at the FastAPI application. Once running, open a browser and navigate to the local address to interact with the dashboard.

---

## Roadmap

- Integrate automated evaluation frameworks such as Ragas or TruLens to measure retrieval and generation quality.
- Replace basic string-based token tracking with a dedicated micro-classification model for more robust intent detection.
- Add vector deduplication layers to the ingestion pipeline to maintain efficiency at scale across large document uploads.
