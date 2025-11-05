# NexTrade Multi-Agent System: Quick Start Guide

**Get up and running in 3 minutes!** ⚡

---

## ⚡ Fastest Path (3 Commands)

```bash
# 1. Install dependencies
uv pip install -e .

# 2. Set up environment variables
cp .env.example .env  # Then edit with your API keys

# 3. Run the application
streamlit run streamlit_app.py
```

**Done!** Open http://localhost:8501 in your browser and start trading! 🚀

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Python 3.11+** installed
- ✅ **Git** installed
- ✅ **API Keys** ready:
  - Azure OpenAI API key (required)
  - Tavily API key (required)
  - Alpha Vantage API key (required)
  - LangSmith API key (optional, for monitoring)

---

## 🎯 Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AAIDC-Module2-MultiAgent
```

### 2. Create Virtual Environment

```bash
# Using uv (recommended)
uv venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# OR using standard Python
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
uv pip install -e .

# Verify installation
python check_setup.py
```

### 4. Configure Environment

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```bash
# Required
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

TAVILY_API_KEY=your-tavily-key
ALPHAVANTAGE_API_KEY=your-alphavantage-key

# Optional (for monitoring)
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=nextrade-production
```

### 5. Run the Application

```bash
streamlit run streamlit_app.py
```

**Access:** http://localhost:8501

---

## 🎮 Usage Examples

### Example 1: Research a Stock
```
You: "Research NVIDIA stock and provide analysis"
Agent: [Performs web search, analyzes data, provides insights]
```

### Example 2: Check Portfolio
```
You: "Show me my current portfolio"
Agent: [Retrieves and displays your positions]
```

### Example 3: Place an Order (with approval)
```
You: "Buy 10 shares of AAPL"
Agent: [Requests approval]
You: [Approve or reject the action]
Agent: [Executes the order]
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest -v
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# LLM-dependent tests
pytest -m llm

# Guardrails tests
pytest -m guardrails
```

### Check Test Coverage

```bash
pytest --cov=src --cov-report=html
```

View coverage report: `htmlcov/index.html`

---

## 🔧 Advanced: API Mode Setup

For production deployments with FastAPI backend:

### Terminal 1 - Start API Server

```bash
cd src
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Start Streamlit UI

```bash
streamlit run streamlit_app.py
```

**Access:**
- API Documentation: http://localhost:8000/docs
- Streamlit UI: http://localhost:8501 (select "API Mode" in sidebar)

---

## 📚 Next Steps

- 📖 **Full Documentation:** See [README.md](README.md)
- 🚀 **Setup & Deployment Guide:** See [SETUP.md](SETUP.md)
- 📊 **Production Status:** See [PRODUCTION_READY_SUMMARY.md](PRODUCTION_READY_SUMMARY.md)
- 🔍 **API Troubleshooting:** See [FASTAPI_FIX_GUIDE.md](FASTAPI_FIX_GUIDE.md)

---

## 🆘 Troubleshooting

### Issue: "API Key Not Found"

```bash
# Verify .env file exists and has correct keys
cat .env  # Linux/macOS
type .env  # Windows

# Make sure to restart terminal after editing .env
```

### Issue: "Module Not Found"

```bash
# Reinstall in editable mode
uv pip install -e .

# Verify
python -c "import agent; print('Success')"
```

### Issue: "Port Already in Use"

```bash
# Kill process on port 8501 (Streamlit)
# Windows
netstat -ano | findstr :8501
taskkill /PID <pid> /F

# Linux/macOS
lsof -ti:8501 | xargs kill -9
```

### Issue: "Database Locked"

```bash
# Remove lock file
rm data/trading_orders.db-journal

# Restart application
```

### Need More Help?

1. Check logs: Application logs appear in terminal
2. Review compliance logs: `compliance.log`
3. Run health check: `curl http://localhost:8000/health` (if using API mode)
4. See full documentation: [README.md](README.md)

---

## ✅ Production Readiness Checklist

Before deploying to production:

- [ ] All tests passing: `pytest -v`
- [ ] Environment variables configured
- [ ] API keys verified: `python check_setup.py`
- [ ] LangSmith monitoring enabled (optional)
- [ ] Database backup strategy in place
- [ ] Health checks configured
- [ ] Rate limits understood
- [ ] Security review completed

---

**Version:** 1.0.0  
**Last Updated:** November 4, 2025
