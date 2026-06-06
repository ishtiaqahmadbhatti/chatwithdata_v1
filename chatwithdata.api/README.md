# ChatWithData FastAPI 🚀

A professional, industry-level FastAPI backend application dedicated to **YouTube Tools** (metadata, transcripts, comment fetching, and video downloading) and **Agentic RAG** (local indexing, query routing, and answer synthesis using LangGraph, LangChain, and Ollama).

## Features

- **YouTube Data Extraction**: Retrieve comprehensive video details including transcripts, description, comment threads, and metadata.
- **YouTube Media Downloader**: Download video or audio tracks directly via custom formats and quality metrics (via `yt-dlp`).
- **Local Agentic RAG**: Ingest transcripts and comment datasets into a local vector store (**FAISS**) and query using a smart LLM agent workflow (**LangGraph** + **Ollama**).
- **Dual-Database Support Ready**: Configured for lightweight offline development or integration with AWS S3 storage for download caches.
- **Model Context Protocol**: MCP server interface ready (`mcpserver.py` using `FastMCP`).

---

## Project Structure

```text
├── app/
│   ├── main.py                     # FastAPI application entry point
│   ├── app_core/
│   │   ├── config.py               # Pydantic Settings & Env configurations
│   │   ├── exceptions.py           # Standardized custom application exceptions
│   │   └── middleware.py           # Security headers and request timing middlewares
│   ├── app_services/
│   │   ├── agent_service.py        # LangGraph Agentic RAG Pipeline
│   │   ├── rag_service.py          # YouTube video indexing & FAISS search service
│   │   ├── youtube_service.py      # Metadata extraction & video downloading
│   │   ├── file_service.py         # File utilities and automated cleanup
│   │   └── s3_service.py           # AWS S3 Storage operations
│   └── app_api/
│       └── v1/
│           ├── api.py              # Main API router binding
│           └── endpoints/
│               ├── youtube_tools.py # YouTube Extraction / Download endpoints
│               └── rag_tools.py    # Agentic RAG Ingest / Query endpoints
├── faiss_db/                       # Persisted FAISS vector stores (auto-created)
├── uploads/                        # Upload cache folder (auto-created)
├── outputs/                        # Download outputs folder (auto-created)
├── pyproject.toml                  # Python build & dependency metadata (uv)
├── requirements.txt                # Listed python packages
├── start_app.py                    # Hot-reloaded startup runner script
└── README.md                       # This documentation
```

---

## Quick Start

### 1. Setup Virtual Environment

```bash
# Create virtual environment using uv
uv venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies using uv
uv pip install -r requirements.txt

# Or simply sync dependencies using uv sync (if using pyproject.toml / uv.lock)
uv sync
```

### 2. Configure Environment

Create a `.env` file in the root folder using `.env.example` as a template:

```env
# Server Configurations
HOST=0.0.0.0
PORT=8001
DEBUG=True

# Optional: YouTube API Key (needed to fetch nested replies for comments, 
# otherwise defaults to basic metadata extraction)
YOUTUBE_API_KEY=your-youtube-data-api-v3-key-here

# Ollama Models & Base URL
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=gemma4:latest          # LLM model for RAG queries
OLLAMA_EMBED_MODEL=qwen3-embedding:latest # Embedding model for FAISS
FAISS_PERSIST_DIR=faiss_db
```

### 3. Run Ollama Locally

Ensure Ollama is installed and running locally, and pull the required models:

```bash
# Pull the LLM model
ollama pull gemma4:latest

# Pull the embedding model
ollama pull qwen3-embedding:latest
```

### 4. Run the Application

Start the FastAPI application with hot reload enabled:

```bash
python start_app.py
```

### 5. Access the API & Docs

- **Interactive Swagger Docs**: [Swagger Docs](http://127.0.0.1:8001/docs)
- **ReDoc Documentation**: [ReDoc Docs](http://127.0.0.1:8001/redoc)
- **Root Endpoint**: [Root API](http://127.0.0.1:8001/)

---

## API Endpoints

### YouTube Tools

#### 1. Extract Comprehensive Data

```http
POST /api/v1/youtubetools/extract-data
```

Extracts metadata, transcripts, and comment threads from a YouTube URL.

#### 2. Download Video or Audio

```http
POST /api/v1/youtubetools/download
```

Downloads video/audio locally using custom format (e.g. mp4, mp3) and quality profiles.

---

### Agentic RAG Tools

#### 1. Ingest Video Details

```http
POST /api/v1/ragtools/ingest
```

Takes the extraction response from `/youtubetools/extract-data`, splits it into documents, generates embeddings, and saves a FAISS index locally.

#### 2. Query Video Content

```http
POST /api/v1/ragtools/query
```

Starts a LangGraph retrieval pipeline using local Ollama models to answer complex user questions relative to the video transcript and comments.
