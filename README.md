# Faiss Vector Store API

A FastAPI-based application that provides vector search capabilities using LlamaIndex and Faiss. This API allows you to build document indexes from text files and query them using natural language.

## Features

- **Document Indexing**: Build vector indexes from directories containing text/markdown files
- **File Upload**: Upload documents directly through the API to create indexes
- **Vector Search**: Query indexes using natural language with semantic search
- **Index Management**: List, check status, and manage multiple indexes
- **Persistent Storage**: Indexes are automatically persisted to disk
- **OpenAI Integration**: Uses OpenAI embeddings and LLM for processing

## Prerequisites

- Python 3.13+
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd simple-rag-server
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
# OR if using uv:
uv sync
```

4. Create a `.env` file in the root directory with your configuration:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_EMBED_DIM=1536
OPENAI_LLM=gpt-4o-mini
STORAGE_DIR=./storage
```

## Running the Application

### Development Mode

```bash
uv run fastapi dev app/main.py
```

### Production Mode

```bash
uv run fastapi run app/main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Root Endpoint

- **GET** `/` - Health check and basic information

### Index Management Endpoints

#### Build Index from Directory
- **POST** `/build`
  - Build a vector index from documents in a specified directory
  - **Request Body**:
  ```json
  {
    "index_name": "my_index",
    "documents_path": "./data"
  }
  ```
  - **Response**:
  ```json
  {
    "index_name": "my_index",
    "status": "success",
    "message": "Index built and persisted successfully from 5 documents."
  }
  ```

#### Upload and Build Index
- **POST** `/upload-build/{index_name}`
  - Upload documents (.txt or .md files) and create/update an index
  - **Parameters**: `index_name` (path parameter)
  - **Request**: Form data with multiple file uploads
  - **Supported file types**: `.txt`, `.md`
  - **Response**:
  ```json
  {
    "index_name": "uploaded_index",
    "status": "success",
    "message": "Uploaded and indexed 3 documents successfully."
  }
  ```

#### Get Index Status
- **GET** `/status/{index_name}`
  - Get detailed status information about a specific index
  - **Response**:
  ```json
  {
    "index_name": "my_index",
    "loaded": true,
    "last_accessed": "2025-09-28T10:30:00Z",
    "storage_path": "./storage/my_index"
  }
  ```

#### List Available Indexes
- **GET** `/list_available_indexes`
  - Get a list of all available indexes (both loaded and persisted)
  - **Response**: `["index1", "index2", "index3"]`

#### List Loaded Indexes
- **GET** `/list_loaded_indexes`
  - Get a list of currently loaded indexes in memory
  - **Response**: `["index1", "index2"]`

### Query Endpoints

#### Query Index
- **POST** `/query`
  - Search through a specific index using natural language
  - **Request Body**:
  ```json
  {
    "index_name": "my_index",
    "query": "What is the impact of technology on education?",
    "similarity_top_k": 5
  }
  ```
  - **Response**:
  ```json
  {
    "response": "Technology has significantly transformed education by enabling online courses, digital textbooks, and interactive platforms...",
    "sources": [
      "Content of relevant document chunks that were used to generate the response..."
    ]
  }
  ```

## Usage Examples

### Using curl

1. **Build an index from local directory**:
```bash
curl -X POST "http://localhost:8000/build" \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "sample_docs",
    "documents_path": "./data"
  }'
```

2. **Upload files and build index**:
```bash
curl -X POST "http://localhost:8000/upload-build/my_documents" \
  -F "files=@document1.txt" \
  -F "files=@document2.md"
```

3. **Query an index**:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "sample_docs",
    "query": "What are the privacy concerns with technology?",
    "similarity_top_k": 3
  }'
```

4. **List available indexes**:
```bash
curl -X GET "http://localhost:8000/list_available_indexes"
```

### Using Python requests

```python
import requests

# Build an index
response = requests.post("http://localhost:8000/build", json={
    "index_name": "my_index",
    "documents_path": "./data"
})
print(response.json())

# Query the index
response = requests.post("http://localhost:8000/query", json={
    "index_name": "my_index",
    "query": "Tell me about communication technology",
    "similarity_top_k": 5
})
print(response.json())
```

## Directory Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── state.py             # Global application state management
│   ├── llm.py              # LLM configuration
│   ├── embed_model.py      # Embedding model configuration
│   ├── routers/
│   │   ├── index.py        # Index management endpoints
│   │   ├── query.py        # Query endpoints
│   │   └── schema.py       # Pydantic models
│   └── utils/
│       ├── faiss.py        # Faiss-specific utilities
│       ├── index.py        # Index utilities
│       └── storage.py      # Storage management
├── data/                   # Sample documents directory
├── storage/               # Persisted indexes storage
├── pyproject.toml         # Project configuration
└── README.md
```

## Configuration

The application uses environment variables for configuration. Create a `.env` file with:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_EMBED_MODEL` | OpenAI embedding model | `text-embedding-3-small` |
| `OPENAI_EMBED_DIM` | Embedding dimensions | `1536` |
| `OPENAI_LLM` | OpenAI LLM model | `gpt-4o-mini` |
| `STORAGE_DIR` | Directory for index storage | `./storage` |

## Supported File Types

Currently supported document formats:
- `.txt` - Plain text files
- `.md` - Markdown files

## Index Persistence

- Indexes are automatically persisted to the `storage/` directory
- Each index is stored in its own subdirectory
- On startup, the application automatically discovers and loads persisted indexes
- Indexes include vector stores, document stores, and metadata

## Error Handling

The API provides detailed error messages for common scenarios:
- Invalid index names
- Missing documents or directories
- File upload errors
- Query errors
- Index not found errors

## Performance Notes

- Indexes are loaded into memory on first access for faster queries
- Large document collections may require significant memory
- Consider the `similarity_top_k` parameter to control response time and relevance

## Development

To contribute to this project:

1. Install development dependencies
2. Run tests (if available)
3. Follow the existing code structure and patterns
4. Ensure proper error handling and validation

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.