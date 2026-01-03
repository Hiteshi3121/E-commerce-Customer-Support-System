# 🛒 NovaCart AI Assistant

NovaCart AI Assistant is an **end-to-end, agentic AI customer support system for an e-commerce platform**, designed to simulate a real-world production-grade support workflow. It combines **LLM-based reasoning**, **rule-based routing**, **RAG (Retrieval-Augmented Generation)**, **stateful conversations**, **human escalation**, and **evaluation metrics** into a single cohesive system.

This project is intentionally built to demonstrate **how modern AI agents behave in real business scenarios**, not just how they generate text.

---

## 🎯 Project Objectives

The core goals of this project are:

- Build a **realistic e-commerce AI support assistant** (not a toy chatbot)
- Demonstrate **agent orchestration using LangGraph**
- Separate **reasoning (LLM)** from **business logic (tools + DB)**
- Handle **multi-turn conversations with memory**
- Safely integrate **RAG for company policies & FAQs**
- Support **human escalation** when AI confidence is low or user is frustrated
- Provide **human-in-the-loop (HITL) evaluation metrics**

This project mirrors how AI assistants are built in **real companies**.

---

## 🧠 What Problems Does NovaCart AI Solve?

| Problem                               | How NovaCart Solves It                                      |
|---------------------------------------|-------------------------------------------------------------|
| Users ask vague or partial queries    | Router + state tracking resolves intent over multiple turns |
| Users give order ID before intent     | System stores order ID and asks what to do                  |
| Users ask FAQs                        | RAG-based FAQ agent answers strictly from PDF               |
| Users want to place orders            | Order agent extracts entities and creates DB entries        |
| Users want to track orders            | Track agent fetches DB data and computes ETA                |
| Users want to return orders           | Return agent validates ownership + creates return request   |
| Users are confused or frustrated      | Automatic human escalation & ticket creation                |
| AI hallucinations                     | Tools-first design + strict RAG rules                       |
| No way to measure AI quality          | Evaluation dashboard with metrics                           |

---

## 🧩 High-Level Architecture

```
Frontend (Streamlit)
        │
        ▼
FastAPI Backend (main.py)
        │
        ▼
LangGraph Workflow
        │
        ├── Intent Router (rule-based + LLM fallback)
        │
        ├── Order Agent
        ├── Track Agent
        ├── Return Agent
        ├── Ticket Agent (with escalation)
        ├── FAQ RAG Agent
        │
        ▼
Persistence Layer
- SQLite (orders, tickets, returns, users)
- Memory DB (conversation history)
- ChromaDB (RAG)
```


## 📁 Project Structure

NovaCart_Ecom_AI_Assistant/
│
├── frontend/
│   ├── streamlit_app.py        # Chat UI + Evaluation Dashboard
│   └── evaluation_matrix.py   # Manual & automated evaluation metrics
│
├── backend/
│   │
│   ├── agents/                # 🤖 AI Agents
│   │   ├── order_agent.py     # Order placement agent
│   │   ├── return_agent.py    # Return handling (ReAct + @tool)
│   │   ├── track_agent.py     # Order tracking agent
│   │   ├── ticket_agent.py    # Support & escalation agent
│   │
│   ├── graph/                 # 🧠 LangGraph Orchestration
│   │   ├── router.py          # Intent routing logic
│   │   ├── workflow.py        # Graph nodes & edges
│   │   └── state.py           # Shared conversation state
│   │
│   ├── rag/                   # 📚 RAG System
│   │   ├── faq_agent.py       # FAQ + document QA
│   │   ├── vectorstore.py     # Chroma vector DB
│   │   └── tools.py           # RAG tools
│   │
│   ├── auth/
│   │   └── auth_routes.py     # Login & signup APIs
│   │
│   ├── db.py                  # SQLite DB & migrations
│   ├── memory.py              # Conversation memory
│   └── main.py                # FastAPI entrypoint
│
├── chroma_store/              # Vector DB persistence
├── memory.db                  # Chat memory database
│
├── NovaCart.pdf               # Knowledge base (company info)
├── NovaCart_Enhanced.pdf      # Expanded FAQ & policies
│
├── requirements.txt
└── README.md


---

## 🧭 Core Workflow (How the System Thinks)

### 1️⃣ User Message Enters System

Every message goes through the **Intent Router**.

### 2️⃣ Intent Router Responsibilities

The router is the brain of the system:

- Extracts **order IDs** (`ORD-XXXX`)
- Detects **explicit human escalation requests**
- Handles **multi-turn flows** using:
  - `active_order_id`
  - `pending_intent`
- Uses **rule-based detection first** (safe & fast)
- Falls back to **LLM intent classification only if needed**

This ensures **predictable behavior**.

---

## 🤖 Agents & Their Responsibilities

### 🛍️ Order Agent

**Purpose:** Place new orders
**Capabilities:**
- Uses LLM to extract:
  - Product name
  - Quantity
- Validates extracted entities
- Creates order in database
- Responds with order confirmation

**Why LLM is used:** Natural language entity extraction

---

### 📦 Track Agent

**Purpose:** Track existing orders
**Capabilities:**
- Validates order ownership
- Fetches order details from DB
- Calculates **5–7 business day ETA** (logic, not LLM)
- Uses LLM only to explain status clearly

**Why this matters:** LLM does NOT calculate dates or business logic

---

### ↩️ Return Agent
**Purpose:** Handle product returns

**Capabilities:**
- Ensures order ID exists
- Validates order belongs to user
- Uses LLM to extract return reason
- Updates orders + returns tables

---

### 🎫 Ticket Agent
**Purpose:** Raise support tickets

Supports two modes:

#### Normal Ticket
- Requires order ID
- Extracts issue using LLM
- Creates support ticket

#### 🚨 Human Escalation Ticket
- No order ID required
- Triggered when:
  - User explicitly asks for human
  - Numeric confusion
  - Repeated failures
- Creates ESCALATED ticket

---

### 📚 FAQ Agent (RAG)

**Purpose:** Answer company-related questions
**Design Principles:**
- Uses **only** the PDF (`NovaCart_Enhanced.pdf`)
- No hallucinations
- Uses:
  - ChromaDB
  - MMR retrieval
  - Forced summarization

If answer is not in document → AI explicitly says so.

---

## 🧠 Memory & State Management

### Conversation State Includes:

- `messages` – chat history
- `user_id` – persistent identity
- `session_id` – conversation context
- `active_order_id` – resolved order ID
- `pending_intent` – waiting intent
- `escalation_reason` – human escalation context

Only **last 2 messages** are persisted per turn to keep memory lean.

---

## 🔐 Authentication

- Username/password authentication
- User ID generated on signup
- Session ID generated per chat
- User identity persists across conversations

---

## 📊 Evaluation & HITL (Human-in-the-Loop)

The system includes **built-in evaluation tooling**.

### Metrics Tracked:

- Intent Accuracy
- Average Response Rating (1–5)
- Task Success Rate
- Confidence Score (heuristic) //Bot is evaluation

### Evaluation UI:

- Manual feedback per interaction
- CSV export
- Confidence vs accuracy visualization

This enables **continuous improvement**.

---

## 🖥️ Frontend (Streamlit)

Features:

- Login / Signup
- Chat interface
- Personalized greetings
- Confidence-based warnings
- Evaluation dashboard

---

## 🗄️ Databases Used

| DB          | Purpose                         |
|-------------|---------------------------------|
| SQLite      | Orders, tickets, returns, users |
| Memory DB   | Conversation history            |
| ChromaDB    | Vector search for RAG           |

---
## 🧪 Example User Queries

- “Place an order for headphones”
- “Track my order ORD-1234”
- “I want to return my order because it’s damaged”
- “Raise a support ticket”
- “What is NovaCart’s refund policy?”

---

## 🛠 Tech Stack

- Python
- FastAPI
- Streamlit
- LangChain
- LangGraph
- Groq LLM (LLaMA 3)
- ChromaDB
- SQLite

---

## ▶️ Setup Instructions: How to Run the Project

1️⃣ Install dependencies
(First run in terminal)

>> uv pip install -r requirements.txt

//Make sure all dependencies the installed then next, //

2️⃣ Start backend (Terminal 1)

>> uvicorn backend.main:app --reload

3️⃣ Start frontend (Terminal 2)

>> streamlit run frontend/streamlit_app.py

---

## 🚀 Why This Project Matters

This is **not just a chatbot**.

It demonstrates:

- Agentic AI design
- Real business workflows
- Tool-first architecture
- Safety against hallucinations
- Scalable routing patterns
- Evaluation-driven AI development

This project can be extended into:
- Voice bots
- MCP servers
- Multi-agent systems
- Production SaaS

---

## 🧩 Future Extensions (Optional)

- Web scraping product catalog
- Payment gateway simulation
- Order cancellation flows
- Voice integration (LiveKit)
- Role-based human dashboards

---




