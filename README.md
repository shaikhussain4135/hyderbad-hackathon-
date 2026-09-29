# 🧠 Customer Support Memory Agent

> **An AI Customer Support Agent powered by persistent Hindsight Memory and Neon PostgreSQL.**  
> Built for the Hackathon to demonstrate how persistent memory transforms generic AI troubleshooting into personalized, fast, and context-aware customer support.

---

## 1. Project Overview

The **Customer Support Memory Agent** is an end-to-end support orchestration system designed to eliminate repetitive, generic troubleshooting across customer support interactions.

Traditional support bots treat every ticket in isolation. When a user experiences a recurring issue (such as a session timeout or quota cap), traditional bots ask the same initial generic diagnostic questions repeatedly.

By leveraging **Hindsight** as persistent memory alongside **Neon PostgreSQL** for structured relational records, this agent remembers:
- Past customer tickets and symptoms
- Verified root causes
- Successful solutions and failed approaches
- Customer environment and account context
- Resolution times and user feedback

When a similar issue recurs, the agent recalls verified past experiences, skips redundant diagnostic steps, and provides an immediate, highly personalized recommendation.

---

## 2. Problem Being Solved

| Traditional Support AI (Without Memory) | Customer Support Memory Agent (With Hindsight) |
|---|---|
| ❌ Repeats standard triage questions every single ticket. | ✅ Recognizes returning customers and repeat symptoms. |
| ❌ Ignores past solutions that already resolved the issue. | ✅ Immediately applies verified past fixes. |
| ❌ High mean time to resolution (MTTR). | ✅ Fast resolution with zero redundant steps. |
| ❌ Loses context as soon as the session closes. | ✅ Learns continuously across interactions via Hindsight. |

---

## 3. Architecture

```
                       ┌────────────────────────────────────────┐
                       │        Customer / Support User         │
                       └───────────────────┬────────────────────┘
                                           │ Submits Ticket
                                           ▼
                       ┌────────────────────────────────────────┐
                       │       Streamlit Multi-Page UI          │
                       │ (Dashboard, Ticket, Explorer, Analytics│
                       └───────────────────┬────────────────────┘
                                           │
                                           ▼
                       ┌────────────────────────────────────────┐
                       │         CustomerSupportAgent           │
                       │            (Orchestrator)              │
                       └─────┬────────────────────────────┬─────┘
                             │                            │
             1. Triage       │                            │ 2. Recall Memory
                             ▼                            ▼
            ┌───────────────────────┐            ┌──────────────────────┐
            │     Issue Analyzer    │            │  Hindsight Memory    │
            │ (Category / Severity) │            │ (Semantic TEMPR Bank)│
            └───────────┬───────────┘            └──────────┬───────────┘
                        │                                   │
                        └─────────────┬─────────────────────┘
                                      │ Context + Memories
                                      ▼
                        ┌───────────────────────────┐
                        │      Response Generator   │
                        │    (LLM Reasoning Engine) │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │  Personalized Support Fix │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │   Customer Feedback Loop  │
                        │    (Resolved / Unresolved)│
                        └───────┬───────────┬───────┘
                                │           │
              Save Structured   │           │ Retain Verified
              Relational Data   │           │ Experience
                                ▼           ▼
                   ┌──────────────────┐  ┌──────────────────┐
                   │ Neon PostgreSQL  │  │ Hindsight Memory │
                   │   Database       │  │   Bank Update    │
                   └──────────────────┘  └──────────────────┘
```

---

## 4. Technology Stack

- **Frontend:** Streamlit 1.64+ (Clean multi-page UI, real-time KPI metrics, interactive recall simulator)
- **Backend / Agent:** Python 3.10+ (Modular clean architecture)
- **Persistent AI Memory:** [Hindsight](https://github.com/vectorize-io/hindsight) (`hindsight-client` official SDK)
- **Structured Database:** [Neon PostgreSQL](https://neon.tech) (`SQLAlchemy 2.0` + `psycopg2-binary`)
- **LLM Reasoning:** Configurable multi-provider engine supporting [Groq](https://groq.com) (`llama-3.3-70b-versatile`), [OpenAI](https://openai.com) (`gpt-4o-mini`), or intelligent offline simulator.
- **Testing:** `pytest` test suite with 100% pass rate.

---

## 5. Component Roles

### Hindsight (Core Memory Component)
- Provides long-term semantic memory storage (`retain`) and retrieval (`recall`).
- Indexes root causes, troubleshooting steps, and successful resolutions into dedicated memory banks.
- Features resilient local memory bank fallback for seamless offline demonstration.

### Neon PostgreSQL (Relational Data Component)
- Stores ACID-compliant operational data: `Customers`, `Tickets`, `Messages`, and `Resolutions`.
- Enforces relational foreign keys, timestamps, and indexes.
- Transparently falls back to local SQLite when `DATABASE_URL` is omitted, and connects to live Neon with SSL when provided.

### LLM (Reasoning & Generation Component)
- Synthesizes customer environment context, issue symptoms, and recalled Hindsight memories.
- Adheres strictly to safety rules: never invents memories or states unproven root causes without evidence.

---

## 6. Installation

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/customer-support-memory-agent.git
cd customer-support-memory-agent
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv

# Windows:
.\venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 7. Environment Configuration

Copy `.env.example` to create your local `.env`:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```ini
# Hindsight Memory Server
HINDSIGHT_URL=http://localhost:8888
HINDSIGHT_API_KEY=

# Neon PostgreSQL Database
DATABASE_URL=postgresql://username:password@ep-sample-pool.us-east-2.aws.neon.tech/neondb?sslmode=require

# LLM Configuration (Supported: groq, openai, mock)
LLM_PROVIDER=groq
LLM_API_KEY=gsk_your_groq_api_key_here
LLM_MODEL=llama-3.3-70b-versatile
LLM_BASE_URL=
```

> **Security Note:** `.env` is listed in `.gitignore` and is never committed to Git. All secret inputs in the UI and logging output are automatically masked.

---

## 8. How to Obtain Credentials

- **Neon PostgreSQL:**
  1. Sign up at [neon.tech](https://neon.tech).
  2. Create a project and database.
  3. Copy the `DATABASE_URL` connection string from the dashboard (enable pooled or direct connection with `sslmode=require`).
- **Hindsight Server:**
  1. Run locally via Docker: `docker run -d -p 8888:8888 vectorizeio/hindsight`
  2. Or register for managed Hindsight at [vectorize.io](https://vectorize.io).
- **Groq API Key:**
  1. Sign up at [console.groq.com](https://console.groq.com).
  2. Navigate to **API Keys** -> Create Key.

---

## 9. How to Run Locally

Start the Streamlit application:
```bash
python -m streamlit run app.py
```

Open your browser at:
```
http://localhost:8501
```

---

## 10. How to Seed Demo Data

The application automatically seeds demo data on initial launch if the database is fresh. You can also re-seed at any time:
1. Navigate to the **📊 Dashboard** in the sidebar.
2. Click **⚡ Seed Demo Data**.
3. This creates:
   - **Customer 1:** John Smith (Document Cloud Enterprise, Windows 11 + Chrome) with historical PDF quota resolution.
   - **Customer 2:** Sarah Connor (Operations Center, macOS + Safari) with historical session timeout resolution.
   - **Customer 3:** Alex Rivera (API Gateway, Ubuntu + Firefox) fresh customer with no prior history (for demonstrating the "Without Memory" flow).

---

## 11. 60-Second Hackathon Demo Workflow

### Step 1: Baseline Interaction (Without Prior Memory)
1. Go to **🎫 New Support Ticket**.
2. Select customer **Alex Rivera**.
3. Enter issue: `"Receiving HTTP 403 Forbidden on our custom webhook endpoint"`.
4. Click **🚀 Analyze Issue & Consult Hindsight Memory**.
5. **Notice:**
   - ℹ️ *No relevant previous memory found in Hindsight.*
   - Agent delivers standard diagnostic troubleshooting steps.

### Step 2: The Recall Interaction (With Hindsight Memory)
1. Go to **🎫 New Support Ticket**.
2. Select customer **John Smith**.
3. Click the preset button: **Main Demo 1 (PDF Upload)**:
   - Issue: `"My PDF upload is failing again."`
4. Click **🚀 Analyze Issue & Consult Hindsight Memory**.
5. **Notice the Instant Contrast:**
   - 🧠 **MEMORY FOUND:** Recalls past incident `TCK-PDF-001`.
   - **Root Cause recalled:** 32MB payload exceeded 25MB account quota.
   - 🤖 **AI Recommendation:** Immediately advises checking file quota and compressing file before any reset.
   - Bypasses all redundant troubleshooting questions!

### Step 3: Feedback & Continuous Learning Loop
1. Under **Customer Feedback & Resolution Loop**, click **✅ YES — RESOLVED**.
2. Click **💾 Save Resolution & Retain Experience**.
3. Go to **🧠 Memory Explorer** to see the new memory unit live in the persistent Hindsight bank.

---

## 12. Testing

Run the automated test suite with pytest:
```bash
python -m pytest tests/ -v
```

All 13 tests verify:
- Database CRUD and foreign key constraints
- Safe connection testing without credential leakage
- Hindsight memory retention and precision semantic recall
- First interaction (no-memory) vs repeat interaction (with-memory)
- Full end-to-end learning lifecycle

---

## 13. Project Structure

```
customer-support-memory-agent/
├── app.py                     # Main Streamlit multi-page application
├── requirements.txt           # Python dependencies
├── README.md                  # Complete documentation
├── .env.example               # Safe configuration template
├── .gitignore                 # Git ignore rules (protects .env and local db)
│
├── agents/                    # AI Agent core logic
│   ├── issue_analyzer.py      # Triage and symptom parsing
│   ├── response_generator.py  # Context builder & prompt engineering
│   └── support_agent.py       # Central orchestrator
│
├── memory/                    # Persistent memory
│   └── hindsight_manager.py   # Hindsight SDK integration + offline bank
│
├── database/                  # Relational storage
│   ├── models.py              # SQLAlchemy schema (Customers, Tickets, Resolutions)
│   ├── database.py            # Neon & SQLite connection manager
│   └── repositories.py        # Data access layer
│
├── services/                  # Business logic
│   ├── customer_service.py
│   ├── ticket_service.py
│   └── resolution_service.py
│
├── llm/                       # LLM Provider integrations
│   └── llm_client.py          # Groq, OpenAI & offline simulator
│
├── pages/                     # Streamlit views
│   ├── dashboard.py           # KPIs, comparison banner, recent records
│   ├── new_ticket.py          # Ticket submission, reasoning & feedback loop
│   ├── ticket_history.py      # Ticket audit inspector
│   ├── memory_explorer.py     # Hindsight bank visualizer & recall tester
│   ├── analytics.py           # First vs later interaction metrics
│   └── integrations.py        # Safe credentials & connection diagnostics
│
├── data/
│   └── seed_data.py           # Realistic synthetic demo datasets
│
├── tests/                     # Unit and integration test suite
│   ├── test_database.py
│   ├── test_memory.py
│   ├── test_agent.py
│   └── test_integrations.py
│
└── utils/
    ├── config.py              # Dynamic configuration & secret masking
    └── logging.py             # Redacted logging formatter
```

---

## 14. Troubleshooting

- **Hindsight Server Unreachable:**  
  The agent automatically switches to its resilient local persistent memory bank so demos and testing never fail. To connect a live Hindsight server, ensure Docker is running with `docker run -d -p 8888:8888 vectorizeio/hindsight`.
- **Neon Database Connection Issues:**  
  Verify your Neon connection string contains `?sslmode=require`. Test the connection via the **Integrations** page.
- **Port 8501 Already in Use:**  
  Launch Streamlit on another port: `python -m streamlit run app.py --server.port 8502`.
