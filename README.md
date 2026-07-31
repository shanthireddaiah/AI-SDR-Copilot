# AI SDR Copilot – Intelligent Sales Research & Outreach Assistant 🚀

An enterprise-ready, AI-powered Sales Development Representative (SDR) Research Assistant built using **Python, Django 5, MySQL, OpenAI API (GPT-4o-mini & Embeddings), LangChain, LangGraph, ChromaDB, PyPDF2, and Bootstrap 5**.

Designed specifically as a production-grade, fresher-to-mid-level portfolio project demonstrating modern AI engineering, RAG architecture, agentic graph workflows, and enterprise software practices.

---

## 🏗️ System Architecture

```
                                +-----------------------------------------+
                                |     Bootstrap 5 Light SaaS Dashboard    |
                                |  (Dashboard, Research, Outreach, Chat)  |
                                +--------------------+--------------------+
                                                     |
                                            REST APIs / CSRF
                                                     |
                                +--------------------v--------------------+
                                |             Django Backend              |
                                | +----------+ +----------+ +-----------+ |
                                | | accounts | | research | |  outreach | |
                                | +----------+ +----------+ +-----------+ |
                                | |   rag    | |   chat   | | dashboard | |
                                | +----------+ +----------+ +-----------+ |
                                | | settings |                            |
                                | +----------+                            |
                                +---------+-------------------+-----------+
                                          |                   |
                        +-----------------v----+        +-----v-------------------+
                        |  LangGraph Workflow  |        |        ChromaDB         |
                        | (OpenAI GPT-4o-mini) |        | Vector DB (RAG Storage) |
                        +----------------------+        +-------------------------+
                                          |                   |
                                +---------v-------------------v-----------+
                                |             MySQL Database              |
                                |  (Users, Companies, Documents, Chat)    |
                                +-----------------------------------------+
```

---

## 🛠️ Tech Stack & Prerequisites

- **Language**: Python 3.10+
- **Backend Framework**: Django 5.0+
- **Database**: MySQL Server 8.0+ (via PyMySQL)
- **Frontend**: HTML5, Vanilla CSS, Bootstrap 5, JavaScript (Fetch API & Clipboard API)
- **AI Stack**: OpenAI API (`gpt-4o-mini`, `text-embedding-3-small`), LangChain, LangGraph StateGraph, ChromaDB, PyPDF2
- **Document Export Engine**: ReportLab & Plain Text Formatted Downloads
- **Containerization**: Docker & Docker Compose
- **Environment**: `python-dotenv`

---

## 📁 7-App Modular Project Structure

```
AI-SDR-Copilot/
├── sdr_copilot/         # Django Core Settings, Logging & Central URL Routing
│   ├── settings.py      # Environment validation, MySQL DB, Python Logging
│   ├── urls.py          # Central Routing & Custom 404/500 handlers
│   └── wsgi.py
├── accounts/            # Authentication (Register, Login, Logout, Password Reset)
├── dashboard/           # SaaS Metrics, Global Search & Activity Timeline
├── research/            # Target Company Research Engine & AI Insights
├── outreach/            # Multi-channel AI Outreach Generator & Export Engine
├── rag/                 # PyPDF2 Text Extractor & ChromaDB Vector Store RAG Engine
├── chat/                # LangGraph StateGraph Sales Copilot Workflow Engine
├── settings/            # User Profile, Role-Based Access (Admin/User), API Keys
├── templates/           # Centralized Bootstrap 5 Templates (Light SaaS Theme)
├── static/              # CSS Stylesheets, JavaScript, Loading Spinners
├── media/               # Uploaded PDF Storage
├── chromadb_store/      # Local ChromaDB Vector Storage Directory
├── logs/                # System Execution Log Files (sdr_copilot.log)
├── init_db.py           # MySQL Auto-Initializer Script
├── Dockerfile           # Docker Container Build File
├── docker-compose.yml   # Multi-container Docker Orchestration File
├── manage.py
├── requirements.txt
├── .env.example
├── .env
└── README.md
```

---

## 🤖 Demo Mode vs Live OpenAI API

The application features an automatic **Zero-Dependency Demo Mode**:
- If `OPENAI_API_KEY` is not configured or set to `demo`, the application runs completely out of the box using built-in mock AI intelligence, local ChromaDB embeddings, and structured outreach copy.
- To enable live OpenAI models, insert a valid key into `.env`:
  `OPENAI_API_KEY=sk-proj-...`

---

## 🗄️ MySQL Database Setup

1. Ensure MySQL Server is running on port 3306.
2. Configure `.env` credentials:
   ```env
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=ai_sdr_db
   DB_USER=root
   DB_PASSWORD=shanthi
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```
3. Run the automatic database initializer script:
   ```bash
   python init_db.py
   ```
4. Execute Django migrations:
   ```bash
   python manage.py migrate
   ```

---

## 🏃 Local Setup & Run Commands

### Step 1: Create & Activate Virtual Environment
```bash
python -m venv venv
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Application
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/`.

---

## 🐳 Docker Deployment

To launch the full stack (Django Web App + MySQL 8.0 Container + ChromaDB Volume) in Docker:

```bash
docker-compose up --build
```
Access the application at `http://localhost:8000`.

---

## 🧪 Testing Guide

To run the automated Django unit test suite across all 7 custom apps:

```bash
python manage.py test
```

Expected Output:
```
Ran 5 tests in ~12s
OK
```

---

## 📡 REST API Documentation

### 1. Company Research API
- **Endpoint**: `GET /research/api/` / `POST /research/api/`
- **Method**: `POST`
- **Body**: `{"name": "Stripe", "website": "https://stripe.com", "industry": "FinTech"}`
- **Response**:
  ```json
  {
    "status": "success",
    "id": 1,
    "name": "Stripe",
    "overview": "Stripe is a financial infrastructure platform...",
    "products": "1. Payments API\n2. Billing...",
    "pain_points": "...",
    "sales_insights": "..."
  }
  ```

### 2. AI Sales Copilot Chat API (LangGraph Workflow)
- **Endpoint**: `POST /chat/api/`
- **Body**: `{"question": "How should I position our security feature to Stripe?", "company_id": 1}`
- **Response**:
  ```json
  {
    "status": "success",
    "chat_id": 4,
    "question": "How should I position our security feature to Stripe?",
    "answer": "1. Target Account Approach...",
    "company": "Stripe",
    "timestamp": "2026-07-31 04:00:00"
  }
  ```

### 3. PDF Upload API (RAG Engine)
- **Endpoint**: `POST /rag/api/upload/`
- **Form Data**: `title="Product Specs", pdf_file=@brochure.pdf`
- **Response**:
  ```json
  {
    "status": "success",
    "doc_id": 2,
    "title": "Product Specs",
    "file_name": "brochure.pdf",
    "chunk_count": 14
  }
  ```

### 4. RAG Query API
- **Endpoint**: `POST /rag/api/query/`
- **Body**: `{"query": "What is the uptime SLA limit?", "top_k": 3}`
- **Response**:
  ```json
  {
    "status": "success",
    "query": "What is the uptime SLA limit?",
    "results": ["Chunk content 1...", "Chunk content 2..."]
  }
  ```

---

## 💼 Resume Project Description

**AI SDR Copilot – Intelligent Sales Research & Outreach Assistant** *(Python, Django, MySQL, OpenAI, LangGraph, ChromaDB, Docker)*
- Architected a 7-module Django AI sales platform integrating OpenAI GPT-4o-mini and ChromaDB vector store for automated prospect research and contextual outreach generation.
- Implemented a LangGraph `StateGraph` agentic workflow orchestrating company context retrieval, ChromaDB RAG similarity search, prompt synthesis, and response persistence in MySQL.
- Built a PDF processing pipeline using PyPDF2 text extraction, `RecursiveCharacterTextSplitter` chunking, and OpenAI `text-embedding-3-small` vectors with automatic Demo Mode fallback.
- Optimized Django ORM query performance using `select_related`/`prefetch_related` and indexed MySQL database schemas, reducing database lookup latencies.
- Designed a modern, responsive Light SaaS UI with Bootstrap 5, export options (PDF, TXT, Clipboard), pagination, global search, and Dockerized deployment.

---

## ❓ Technical Interview Questions & Answers

### Q1: What is Retrieval-Augmented Generation (RAG) and how did you implement it in this project?
**Answer**: RAG enhances LLM responses by fetching relevant context from an external vector database before generating an answer. In this project, PDFs are parsed with PyPDF2, split into text chunks using `RecursiveCharacterTextSplitter`, embedded using OpenAI `text-embedding-3-small` vectors, and indexed in ChromaDB. When a user asks a question, ChromaDB retrieves top-K matching chunks via cosine similarity search and injects them into the prompt.

### Q2: Why did you use LangGraph instead of simple sequential chains?
**Answer**: LangGraph introduces stateful, graph-based agentic workflows (`StateGraph`). It explicitly defines state nodes (`retrieve_company_context`, `retrieve_rag_context`, `format_prompt`, `call_llm`) and directed edges. This allows conditional branching, state persistence, error boundaries, and scalable orchestration compared to basic chains.

### Q3: How does Demo Mode work without an OpenAI API key?
**Answer**: All service layers (`research/services.py`, `rag/services.py`, `chat/graph.py`, `outreach/services.py`) invoke an `is_demo_mode()` checker that verifies if `OPENAI_API_KEY` is missing, empty, or set to `'demo'`. If active, the app synthesizes structured mock intelligence and defaults ChromaDB to local embeddings, making the application 100% testable without API costs.

### Q4: How did you optimize Django ORM database queries in MySQL?
**Answer**: To prevent N+1 query bottlenecks, views utilize `select_related('company')` and `select_related('user')` for single-valued ForeignKeys. Frequently queried columns (`user_id`, `created_at`, `name`, `message_type`) are indexed using `db_index=True` in Django models.

### Q5: How do you handle vector cleanup when a document is deleted?
**Answer**: When an `UploadedDocument` record is deleted, `delete_document_vectors(doc_id)` queries ChromaDB's `sdr_knowledge_base` collection using the metadata filter `where={"doc_id": str(doc_id)}` to purge corresponding vectors before removing the file from disk and database.
