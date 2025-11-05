# NexTrade Multi-Agent System: Deployment Guide

**Status:** Production-Ready | **Version:** 1.0.0

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Prerequisites](#-prerequisites)
3. [Installation](#-installation)
4. [Configuration](#-configuration)
5. [Deployment Options](#-deployment-options)
6. [API Reference](#-api-reference)
7. [Monitoring](#-monitoring)
8. [Troubleshooting](#-troubleshooting)

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
uv pip install -e .

# 2. Configure environment
cp .env.example .env  # Edit with your API keys

# 3. Start application
streamlit run streamlit_app.py
```

**That's it!** Open http://localhost:8501 in your browser.

---

## 📦 Prerequisites

### Required Accounts & API Keys

| Service | Purpose | Free Tier | Get Key |
|---------|---------|-----------|---------|
| **Azure OpenAI** | Primary LLM (GPT-4o) | No | [Azure Portal](https://portal.azure.com) |
| **Tavily API** | Web search | 1000 req/month | [tavily.com](https://tavily.com) |
| **Alpha Vantage** | Stock lookup | 25 req/day | [alphavantage.co](https://www.alphavantage.co) |
| **LangSmith** | Monitoring (optional) | Yes | [smith.langchain.com](https://smith.langchain.com) |
| **Groq** | Fallback LLM (optional) | Yes | [groq.com](https://groq.com) |

### System Requirements
- Python 3.11 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB disk space
- Stable internet connection

---

## 🔧 Installation

### 1. Clone & Setup

```bash
git clone <repository-url>
cd AAIDC-Module2-MultiAgent

# Create virtual environment
uv venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Install dependencies
uv pip install -e .
```

### 2. Install Guardrails AI (Optional)

```bash
uv pip install guardrails-ai
guardrails configure
guardrails hub install hub://guardrails/toxic_language
guardrails hub install hub://guardrails/pii_detection
```

### 3. Verify Installation

```bash
python check_setup.py
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file:

```bash
# LLM Configuration (Required)
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# External APIs (Required)
TAVILY_API_KEY=your-tavily-key
ALPHAVANTAGE_API_KEY=your-alphavantage-key

# Monitoring (Optional)
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=nextrade-production

# Fallback LLM (Optional)
GROQ_API_KEY=your-groq-api-key
```

---

## 🚀 Deployment Options

### Option 1: Direct Mode (Recommended)

**Best for:** Local development, quick testing

```bash
streamlit run streamlit_app.py
```

- ✅ No API server needed
- ✅ Instant startup
- ✅ 100% production-ready

**Access:** http://localhost:8501

### Option 2: API Mode

**Best for:** Production, multiple clients, microservices

**Terminal 1 - Start API Server:**
```bash
cd src
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Streamlit UI:**
```bash
streamlit run streamlit_app.py
```

**Access:**
- API Docs: http://localhost:8000/docs
- Streamlit UI: http://localhost:8501 (select "API Mode")

### Option 3: Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN pip install uv && uv pip install -e .

EXPOSE 8000 8501

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build & Run:

```bash
docker build -t nextrade:latest .
docker run -p 8000:8000 --env-file .env nextrade:latest
```

### Option 4: Azure App Service

```bash
# Login to Azure
az login

# Create resources
az group create --name nextrade-rg --location eastus
az appservice plan create --name nextrade-plan --resource-group nextrade-rg --sku B1 --is-linux
az webapp create --resource-group nextrade-rg --plan nextrade-plan --name nextrade-api --runtime "PYTHON:3.12"

# Deploy
az webapp deploy --resource-group nextrade-rg --name nextrade-api --src-path .

# Configure environment variables
az webapp config appsettings set --resource-group nextrade-rg --name nextrade-api --settings @.env
```

---

## 📡 API Reference

### Base URL
- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

### Core Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-04T10:30:00Z"
}
```

#### 2. Chat with Agent
```http
POST /chat
```

**Request:**
```json
{
  "message": "Research NVIDIA stock",
  "user_id": "user_12345",
  "thread_id": "thread_67890"
}
```

**Response:**
```json
{
  "response": "Based on my research...",
  "thread_id": "thread_67890",
  "requires_approval": false,
  "timestamp": "2025-11-04T10:30:00Z"
}
```

#### 3. Approve Action
```http
POST /approve
```

**Request:**
```json
{
  "thread_id": "thread_67890",
  "approved": true
}
```

**Response:**
```json
{
  "response": "Order placed successfully",
  "approved": true
}
```

#### 4. Get Portfolio
```http
GET /portfolio/{user_id}
```

**Response:**
```json
{
  "user_id": "user_12345",
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": 100,
      "average_price": 145.50
    }
  ]
}
```

#### 5. Get Order History
```http
GET /orders/{user_id}?limit=10
```

**Response:**
```json
{
  "user_id": "user_12345",
  "orders": [
    {
      "order_id": "ord_123",
      "symbol": "AAPL",
      "quantity": 10,
      "order_type": "buy",
      "status": "executed"
    }
  ]
}
```

### Error Responses

**Format:**
```json
{
  "error": "Detailed error message",
  "timestamp": "2025-11-04T10:30:00Z"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request
- `500`: Internal Server Error
- `503`: Service Unavailable

**Full API Documentation:** http://localhost:8000/docs (Swagger UI)

---

## 📊 Monitoring

### Health Checks

Monitor system health at `/health`:

```bash
curl http://localhost:8000/health
```

**Components Checked:**
- API availability
- LLM connectivity
- Database accessibility

**Monitoring Frequency:** Every 60 seconds recommended

### LangSmith Tracing

Enable in `.env`:

```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-key
LANGSMITH_PROJECT=nextrade-production
```

**View Traces:** https://smith.langchain.com

### Application Logs

**Log Files:**
- `compliance.log` - Safety violations and audit trail
- Console output - General application logs

**Log Levels:**
- INFO: Normal operations
- WARNING: Recoverable issues
- ERROR: Failed operations

---

## 🔧 Troubleshooting

### Common Issues

#### 1. API Key Errors
```
ValueError: AZURE_OPENAI_API_KEY not found
```

**Solution:**
```bash
# Verify .env file
cat .env | grep AZURE_OPENAI_API_KEY

# Restart terminal to reload environment
```

#### 2. Import Errors
```
ModuleNotFoundError: No module named 'agent'
```

**Solution:**
```bash
uv pip install -e .
python -c "import agent; print('Success')"
```

#### 3. Database Locked
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
rm data/trading_orders.db-journal
# Restart application
```

#### 4. Rate Limits
```
429 Too Many Requests
```

**Solution:**
- Wait for rate limit reset (automatic retry included)
- Upgrade API tier
- Check usage at provider dashboard

#### 5. Slow Responses

**Solution:**
```bash
# Check LangSmith traces for bottlenecks
# Review logs for errors
tail -f compliance.log
```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. **Check logs:** `tail -f compliance.log`
2. **Run tests:** `pytest -v`
3. **Verify health:** `curl http://localhost:8000/health`
4. **Review traces:** https://smith.langchain.com
5. **Documentation:** See [README.md](README.md) and [QUICK_START.md](QUICK_START.md)

---

## 🔄 Maintenance

### Regular Tasks

**Daily:**
- Monitor `/health` endpoint
- Review error logs
- Check API rate limits

**Weekly:**
- Review LangSmith traces
- Analyze compliance logs
- Update dependencies: `uv pip install --upgrade -e .`

**Monthly:**
- Database backup: `cp data/trading_orders.db data/backup_$(date +%Y%m%d).db`
- Security audit
- Performance review

### Backup & Recovery

**Database Backup:**
```bash
# Backup
cp data/trading_orders.db data/backup_$(date +%Y%m%d).db

# Restore
cp data/backup_20251104.db data/trading_orders.db
```

**Configuration Backup:**
```bash
cp .env .env.backup
```

### Updates

**Check for Updates:**
```bash
uv pip list --outdated
```

**Update Dependencies:**
```bash
# Update all
uv pip install --upgrade -e .

# Update specific package
uv pip install --upgrade langchain
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│         Client Applications             │
│      (Streamlit UI, API Clients)        │
└────────────────┬────────────────────────┘
                 │
                 │ HTTPS/REST
                 ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend (Optional)      │
│  ┌────────────────────────────────┐    │
│  │  Safety Layer (Guardrails AI)  │    │
│  │  Resilience (Retry/Circuit)    │    │
│  └────────────────────────────────┘    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Multi-Agent Supervisor System      │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │ Research │ │Portfolio │ │Database │ │
│  │  Agent   │ │  Agent   │ │  Agent  │ │
│  └──────────┘ └──────────┘ └─────────┘ │
└─────────────────────────────────────────┘
         │              │           │
         ▼              ▼           ▼
┌─────────────┐  ┌──────────┐  ┌────────┐
│   LLM       │  │External  │  │SQLite  │
│(Azure GPT4o)│  │APIs      │  │Database│
└─────────────┘  └──────────┘  └────────┘
```

### Technology Stack

**Core:**
- Python 3.12+
- LangGraph 0.6.7+ (Multi-agent orchestration)
- LangChain 0.3.27+ (LLM abstraction)

**APIs & UI:**
- FastAPI 0.121+ (REST API)
- Streamlit 1.49+ (Web UI)
- Guardrails AI 0.6.7+ (Safety)

**Testing:**
- Pytest 8.4+ (Testing framework)
- 80+ test cases (unit + integration)

---

## 📚 Additional Resources

- **Quick Start:** [QUICK_START.md](QUICK_START.md) - 3-minute setup guide
- **Production Summary:** [PRODUCTION_READY_SUMMARY.md](PRODUCTION_READY_SUMMARY.md) - Implementation status
- **Full Documentation:** [README.md](README.md) - Complete technical details

---

**Document Version:** 1.0.0  
**Last Updated:** November 4, 2025  
**Next Review:** February 4, 2026
