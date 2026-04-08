# 🌌 Multi-Agent Operational Workspace

A production-ready AI orchestration platform built for the **Enterprise Hackathon**. This workspace leverages **Vertex AI (Gemini 2.5 Flash)** and **LangGraph** to bridge the gap between disconnected enterprise systems: **Jira Cloud**, **Google Calendar**, and **Internal CRM** databases.

## 🚀 Overview

The workspace features a **Supervisor-Worker architecture** that interprets complex natural language intents and autonomously coordinates cross-platform workflows. 

### Key Capabilities:
- **Autonomous Jira Management**: Create, search, and close tickets natively on Atlassian Cloud.
- **Context-Aware CRM Enrichment**: Automatic customer SLA and status lookups that inject real-time context into support tickets.
- **Intelligent Scheduling**: Automated IST-localized meeting booking based on incident severity or outage reports.
- **Live Mission Control UI**: A premium Streamlit dashboard providing a "single pane of glass" view for all operations.

---

## 🛠️ Tech Stack

- **Intelligence**: Google Vertex AI (Gemini 2.5 Flash)
- **Orchestration**: LangGraph (Stateful Agents)
- **Frontend**: Streamlit (Native Web UI)
- **Compute**: Google Cloud Run (Serverless)
- **Persistence**: SQLite (Local) / SQLAlchemy
- **Integrations**: Jira REST API, Google Calendar API

---

## 📋 Prerequisites

Before you replicate this setup, ensure you have:
1. **Google Cloud Project**: Enabled with *Vertex AI API*, *Cloud Run*, and *Artifact Registry*.
2. **Atlassian Cloud Account**: API Token and User Email for Jira integration.
3. **Google API Credentials**: A `credentials.json` (Desktop App flow) for Calendar API access.
4. **Python 3.10+** installed locally.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd multi-agent-workspace
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory and populate it with your credentials:
```env
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1

# Jira Cloud
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-atlassian-api-token
JIRA_URL=https://your-domain.atlassian.net

# Database
# Leave blank for local SQLite
CLOUD_SQL_CONNECTION_NAME=
```

### 4. Database Initialization
Run the setup script to create the local SQLite database and populate the CRM tiers:
```bash
python -m database.db_setup
python populate_crm.py
```

---

## 🏃 Usage

### Running Locally
```bash
streamlit run app.py
```
*Port: 8501 (default)*

### Deploying to Google Cloud Run
Build and deploy in one command:
```bash
gcloud run deploy multi-agent-workspace \
--source . \
--region us-central1 \
--project your-project-id \
--set-env-vars "JIRA_API_TOKEN=xxx,JIRA_EMAIL=xxx,GOOGLE_CLOUD_PROJECT=xxx" \
--allow-unauthenticated
```

---

## 📖 Demo Scenario
Try entering this into the **Mission Control** tab:
> *"Acme Corp just reported a critical outage. Check their SLA, open a high-priority ticket, and book a 30-minute review on my calendar for tomorrow 10am."*

**The Agent will:**
1. Fetch Acme Corp's **Standard SLA (99.5%)** from CRM.
2. Update Acme's status to **"Critical Outage Reported"** on the dashboard.
3. Create a **Jira Ticket** enriched with the SLA context.
4. Book an **Outage Sync** meeting in **Google Calendar** (IST).

---

## ⚖️ License
MIT License. Created for the Multi-Agent AI System Hackathon.
