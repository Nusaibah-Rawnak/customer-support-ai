# Customer Support AI - Multi-Agent System

A Generative AI-powered Multi-Agent System that enables customer support executives to interact with both structured customer data and unstructured policy documents using natural language.

---

## Overview

This system helps customer support agents to:
- Query customer profiles and support ticket history from a SQL database using plain English
- Search company policy documents uploaded as PDFs through a vector knowledge base
- Get accurate, context-aware responses routed to the right AI agent automatically

---

## Architecture

The system is built around a supervisor agent that sits in the middle and decides where to send each query.

When a user sends a message, the LangGraph Supervisor first classifies the intent. If it looks like a question about a customer or their tickets, it goes to the SQL Agent. If it looks like a policy question, it goes to the RAG Agent. Simple greetings or general questions are handled directly by the LLM.

Each specialist agent has access to a set of MCP tools it can call. The SQL Agent uses tools that query a SQLite database. The RAG Agent uses tools that search a ChromaDB vector store built from uploaded PDFs. The results come back, the LLM synthesizes a natural language response, and that gets sent back to the user.

```
┌─────────────────────────────────────────────────────────┐
│                      Streamlit UI                       │
│             Chat interface + PDF Upload Sidebar         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              LangGraph Supervisor Agent                 │
│        Classifies query → sql / rag / general           │
└──────────┬──────────────────────────────┬───────────────┘
           │                              │
           ▼                              ▼
  ┌─────────────────┐            ┌─────────────────┐
  │    SQL Agent    │            │    RAG Agent    │
  │ LangChain+Gemini│            │ LangChain+Gemini│
  └────────┬────────┘            └────────┬────────┘
           │                              │
           ▼                              ▼
  ┌─────────────────┐            ┌─────────────────┐
  │  FastMCP Server │            │  FastMCP Server │
  │    SQL Tools    │            │    RAG Tools    │
  └────────┬────────┘            └────────┬────────┘
           │                              │
           ▼                              ▼
  ┌─────────────────┐            ┌─────────────────┐
  │    SQLite DB    │            │    ChromaDB     │
  │Customers+Tickets│            │Policy Embeddings│
  └─────────────────┘            └─────────────────┘

           LLM: Google Gemini 2.5 Flash Lite
     Embeddings: sentence-transformers/all-MiniLM-L6-v2
```

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Google Gemini 2.5 Flash Lite |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Orchestration | LangGraph |
| Agent Framework | LangChain |
| MCP Server | FastMCP |
| SQL Database | SQLite |
| Vector Database | ChromaDB |
| UI | Streamlit |

---

## Project Structure

```
customer-support-ai/
├── app.py                    # Streamlit UI entry point
├── agents/
│   ├── supervisor.py         # LangGraph orchestrator
│   ├── sql_agent.py          # SQL specialist agent
│   └── rag_agent.py          # RAG specialist agent
├── mcp_server/
│   ├── server.py             # FastMCP server
│   ├── sql_tools.py          # Customer/ticket DB tools
│   └── rag_tools.py          # Policy search/ingest tools
├── data/
│   └── seed_data.py          # Generates 100 synthetic customers and 376 tickets
├── assets/
│   └── CustomerSupportAI_Demo_Slides.pptx  # Demo presentation
├── policies/                 # Upload policy PDFs here
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup and Installation

### Prerequisites
- Python 3.10+
- A Google Gemini API key (free tier works, get one at aistudio.google.com)

### 1. Clone the repository
```bash
git clone https://github.com/Nusaibah-Rawnak/customer-support-ai.git
cd customer-support-ai
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```

Edit .env and add your Gemini API key:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 5. Seed the database
```bash
python3 data/seed_data.py
```

This generates 100 synthetic customers and ~376 support tickets using the Faker library.

### 6. Run the app
```bash
streamlit run app.py
```

The app will open at http://localhost:8501

---

## Usage

### Querying Customer Data

Ask questions about customers and their support tickets in plain English:
- "Give me an overview of Ema's profile and support tickets"
- "Who are our Enterprise customers?"
- "Show me all open and in-progress tickets"
- "How many customers do we have from the USA?"
- "Who are our highest value Enterprise customers?"
- "Which customers have a satisfaction score below 3?"
- "What is the average resolution time for high priority tickets?"
- "Which agent handles the most tickets?"
- "Show me all open billing tickets"

### Querying Policy Documents

1. Upload one or more policy PDFs using the sidebar
2. Ask questions about the policies:
   - "What is the refund policy?"
   - "How long does a customer have to return a product?"
   - "What are the terms for Enterprise plan customers?"

### Route Indicators

Each response shows a badge indicating which agent handled the query:
- Customer Data: answered by the SQL agent
- Policy Docs: answered by the RAG agent
- General: answered directly by the LLM

---

## Database Schema

### customers
| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| name | TEXT | Customer name |
| email | TEXT | Email address |
| phone | TEXT | Phone number |
| plan | TEXT | Basic / Premium / Enterprise |
| joined_date | TEXT | Account creation date |
| country | TEXT | Country of residence |
| company | TEXT | Company the customer belongs to |
| account_value | REAL | Annual spend in USD |
| satisfaction_score | REAL | Customer satisfaction rating (1.0 to 5.0) |

### support_tickets
| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| customer_id | INTEGER | Foreign key to customers |
| subject | TEXT | Ticket subject |
| description | TEXT | Issue description |
| status | TEXT | Open / In Progress / Resolved / Closed |
| priority | TEXT | Low / Medium / High |
| category | TEXT | Billing / Technical / Account / Feature Request |
| agent_assigned | TEXT | Support agent handling the ticket |
| created_date | TEXT | Date created |
| resolved_date | TEXT | Date resolved (if applicable) |
| resolution_time_hours | INTEGER | Hours taken to resolve (null if unresolved) |

---

## MCP Server Tools

### SQL Tools
- `tool_get_customer_by_name` - Look up a customer by name
- `tool_get_tickets_by_customer_name` - Get all tickets for a customer
- `tool_get_open_tickets` - List all open or in-progress tickets
- `tool_get_all_customers` - List all customers
- `tool_run_sql_query` - Run a custom SELECT query

### RAG Tools
- `tool_search_policies` - Semantic search over policy documents
- `tool_list_uploaded_documents` - List all ingested documents
- `tool_ingest_pdf` - Ingest a new PDF into the knowledge base

---

## Presentation

A slide deck covering the problem, solution, architecture, and tech stack is available in [`assets/CustomerSupportAI_Demo_Slides.pptx`](assets/CustomerSupportAI_Demo_Slides.pptx).

---

## Notes

This project uses the free tier of the Gemini API which has rate limits. For heavy testing or production use, consider upgrading to a paid tier.