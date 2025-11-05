# NexTrade Troubleshooting Guide & FAQ

**Version:** 1.0.0  
**Last Updated:** November 5, 2025  
**Status:** Production Support Guide

---

## 📋 Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Issues & Solutions](#common-issues--solutions)
3. [Installation & Setup Issues](#installation--setup-issues)
4. [Runtime Errors](#runtime-errors)
5. [API & Network Issues](#api--network-issues)
6. [Database Issues](#database-issues)
7. [Performance Issues](#performance-issues)
8. [Security & Safety Issues](#security--safety-issues)
9. [Deployment Issues](#deployment-issues)
10. [FAQ](#faq)
11. [Recovery Procedures](#recovery-procedures)
12. [Getting Help](#getting-help)

---

## Quick Diagnostics

### Health Check Commands

Run these commands to quickly diagnose system health:

```powershell
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1

# 2. Check Python version
python --version  # Should be 3.11+

# 3. Verify package installation
uv pip list | Select-String "langgraph|fastapi|streamlit|guardrails"

# 4. Test imports
python -c "from src.agent.graph import create_supervisor; print('✅ Imports OK')"

# 5. Check API health (if running)
curl http://localhost:8000/health

# 6. Check database file
Test-Path data\trading_orders.db
```

### Common Error Patterns

| Error Message | Likely Cause | Quick Fix |
|---------------|--------------|-----------|
| `ModuleNotFoundError` | Virtual environment not activated | Run `.venv\Scripts\Activate.ps1` |
| `ImportError: cannot import name` | Outdated packages | Run `uv pip install -e .` |
| `Connection refused` | API server not running | Start with `uvicorn src.api:app` |
| `Port already in use` | Another process on port | Kill process or use different port |
| `API key not found` | Missing `.env` file | Create `.env` with API keys |
| `Database locked` | Multiple access attempts | Close other connections |
| `429 Rate limit exceeded` | Too many API calls | Implement backoff, check quota |
| `Timeout error` | Network or LLM latency | Check internet, increase timeout |

---

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'src'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'src'
ImportError: cannot import name 'create_supervisor' from 'src.agent.graph'
```

**Cause:** Package not installed in editable mode or wrong directory.

**Solutions:**

**Solution A: Install in Editable Mode**
```powershell
# Activate venv
.venv\Scripts\Activate.ps1

# Install package
uv pip install -e .

# Verify installation
python -c "import src; print('✅ Package installed')"
```

**Solution B: Check Working Directory**
```powershell
# Ensure you're in project root
cd c:\Tech\AI\ReadyTensor\AAIDC-Module2-MultiAgent

# Verify pyproject.toml exists
Test-Path pyproject.toml
```

**Solution C: Add to Python Path (Temporary)**
```python
import sys
sys.path.insert(0, 'src')
from agent.graph import create_supervisor
```

---

### Issue 2: "API Key Not Found" or Authentication Errors

**Symptoms:**
```
openai.error.AuthenticationError: No API key provided
Error: OPENAI_API_KEY not found in environment
```

**Cause:** Missing or incorrectly configured `.env` file.

**Solutions:**

**Solution A: Create .env File**
```powershell
# Create .env file in project root
@"
OPENAI_API_KEY=sk-your-key-here
LANGCHAIN_API_KEY=lsv2_your-key-here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=nextrade
"@ | Out-File -FilePath .env -Encoding UTF8
```

**Solution B: Verify Environment Variables**
```powershell
# Check if .env exists
Test-Path .env

# Load and verify (in Python)
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', os.getenv('OPENAI_API_KEY')[:10] + '...')"
```

**Solution C: Set Environment Variables Directly**
```powershell
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"

# Linux/Mac
export OPENAI_API_KEY="sk-your-key-here"
```

---

### Issue 3: Streamlit App Won't Start

**Symptoms:**
```
streamlit: command not found
Address already in use
Error: No module named 'streamlit'
```

**Cause:** Streamlit not installed, port conflict, or venv not activated.

**Solutions:**

**Solution A: Install Streamlit**
```powershell
.venv\Scripts\Activate.ps1
uv pip install streamlit
```

**Solution B: Port Already in Use**
```powershell
# Use different port
streamlit run streamlit_app.py --server.port 8502

# Or kill existing process
Get-Process | Where-Object {$_.ProcessName -like "*streamlit*"} | Stop-Process

# Find process using port 8501
netstat -ano | Select-String ":8501"
Stop-Process -Id <PID>
```

**Solution C: Clear Streamlit Cache**
```powershell
# Remove cache directory
Remove-Item -Recurse -Force .streamlit

# Or clear from within app (sidebar button)
```

---

### Issue 4: FastAPI Server Errors

**Symptoms:**
```
uvicorn: command not found
Error loading ASGI app
ImportError: cannot import name 'app' from 'src.api'
```

**Cause:** Uvicorn not installed, wrong working directory, or import errors.

**Solutions:**

**Solution A: Install FastAPI & Uvicorn**
```powershell
.venv\Scripts\Activate.ps1
uv pip install "fastapi[all]" uvicorn
```

**Solution B: Start from Correct Directory**
```powershell
# Start from project root
cd c:\Tech\AI\ReadyTensor\AAIDC-Module2-MultiAgent

# Start server with correct module path
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

**Solution C: Check Import Structure**
```python
# Verify API app exists
python -c "from src.api import app; print('✅ API app found')"
```

**Solution D: Port Conflict**
```powershell
# Use different port
uvicorn src.api:app --port 8001

# Or kill process on port 8000
netstat -ano | Select-String ":8000"
Stop-Process -Id <PID>
```

---

### Issue 5: Database Errors

**Symptoms:**
```
sqlite3.OperationalError: database is locked
FileNotFoundError: [Errno 2] No such file or directory: 'data/trading_orders.db'
sqlite3.DatabaseError: database disk image is malformed
```

**Cause:** Database locked, missing, or corrupted.

**Solutions:**

**Solution A: Database Locked**
```powershell
# Close all connections
# Restart application

# If persistent, copy database
Copy-Item data\trading_orders.db data\trading_orders_backup.db

# Remove and recreate
Remove-Item data\trading_orders.db
python -c "from src.agent.database_tools import init_database; init_database()"
```

**Solution B: Database Missing**
```powershell
# Create data directory
New-Item -ItemType Directory -Force -Path data

# Initialize database
python -c "from src.agent.database_tools import init_database; init_database()"
```

**Solution C: Database Corrupted**
```powershell
# Check integrity
sqlite3 data\trading_orders.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
Copy-Item backups\trading_orders_latest.db data\trading_orders.db

# Or recreate (loses data)
Remove-Item data\trading_orders.db
python -c "from src.agent.database_tools import init_database; init_database()"
```

**Solution D: Repair Database**
```powershell
# Dump and restore
sqlite3 data\trading_orders.db ".dump" | sqlite3 data\trading_orders_new.db
Move-Item -Force data\trading_orders_new.db data\trading_orders.db
```

---

### Issue 6: LLM Response Timeouts

**Symptoms:**
```
asyncio.exceptions.TimeoutError
openai.error.Timeout: Request timed out
Connection timeout after 60s
```

**Cause:** Network latency, API overload, or slow LLM responses.

**Solutions:**

**Solution A: Increase Timeout**
```python
# In src/agent/graph.py or api.py
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    timeout=120.0,  # Increase to 120 seconds
    max_retries=3
)
```

**Solution B: Use Faster Model**
```python
# Switch to faster model
llm = ChatOpenAI(model="gpt-4o-mini")  # Faster than gpt-4o
```

**Solution C: Check Network**
```powershell
# Test OpenAI API connectivity
curl https://api.openai.com/v1/models -H "Authorization: Bearer $env:OPENAI_API_KEY"

# Check internet connection
Test-NetConnection api.openai.com -Port 443
```

**Solution D: Implement Retry Logic**
```python
# Already implemented in resilience.py
from src.agent.resilience import retry_with_backoff, RetryConfig

@retry_with_backoff(retry_config=RetryConfig(max_retries=3))
def call_llm():
    return llm.invoke(messages)
```

---

### Issue 7: Import Errors with Guardrails AI

**Symptoms:**
```
ModuleNotFoundError: No module named 'guardrails'
ImportError: cannot import name 'Guard' from 'guardrails'
```

**Cause:** Guardrails AI not installed or version mismatch.

**Solutions:**

**Solution A: Install Guardrails AI**
```powershell
.venv\Scripts\Activate.ps1
uv pip install guardrails-ai
```

**Solution B: Version Compatibility**
```powershell
# Check version
uv pip show guardrails-ai

# Upgrade to latest
uv pip install --upgrade guardrails-ai

# Or install specific version
uv pip install guardrails-ai==0.5.10
```

**Solution C: Fallback Without Guardrails**
```python
# Modify src/agent/guardrails_integration.py
try:
    from guardrails import Guard
    GUARDRAILS_AVAILABLE = True
except ImportError:
    GUARDRAILS_AVAILABLE = False
    print("Warning: Guardrails AI not available, using basic validation")
```

---

### Issue 8: "RuntimeError: cannot reuse already awaited coroutine"

**Symptoms:**
```
RuntimeError: cannot reuse already awaited coroutine
RuntimeError: This event loop is already running
```

**Cause:** Mixing sync and async code incorrectly.

**Solutions:**

**Solution A: Use Async Properly**
```python
# Wrong
result = supervisor.invoke(config)

# Right
result = await supervisor.ainvoke(config)

# Or in sync context
import asyncio
result = asyncio.run(supervisor.ainvoke(config))
```

**Solution B: In Streamlit (Sync Context)**
```python
# Use LangGraph's streaming API
for event in supervisor.stream(config):
    # Process event
    pass
```

**Solution C: In FastAPI (Async Context)**
```python
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    result = await supervisor.ainvoke(config)
    return result
```

---

### Issue 9: HITL Approval Not Working

**Symptoms:**
```
Approval workflow stuck
No interrupt detected
Command object not created
```

**Cause:** Incorrect interrupt handling or state management.

**Solutions:**

**Solution A: Check Interrupt Configuration**
```python
# Verify interrupt is configured in graph
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
supervisor = create_supervisor(memory)

# Interrupt should be on "supervisor" node
```

**Solution B: Verify Command Usage**
```python
# In approval endpoint
from langgraph.types import Command

# Resume with approval
config = {
    "configurable": {"thread_id": thread_id}
}

if approved:
    result = supervisor.invoke(
        Command(resume="approved"),
        config
    )
else:
    result = supervisor.invoke(
        Command(resume="rejected"),
        config
    )
```

**Solution C: Check State**
```python
# Get current state
state = supervisor.get_state(config)
print("Next node:", state.next)
print("Tasks:", state.tasks)
```

---

### Issue 10: High Memory Usage

**Symptoms:**
```
MemoryError
System running slow
Application crashes
```

**Cause:** Memory leaks, large chat history, or inefficient code.

**Solutions:**

**Solution A: Clear Chat History**
```python
# In Streamlit
if st.button("Clear History"):
    st.session_state.messages = []
    st.rerun()
```

**Solution B: Limit Context Window**
```python
# Keep only recent messages
MAX_HISTORY = 10
if len(messages) > MAX_HISTORY:
    messages = messages[-MAX_HISTORY:]
```

**Solution C: Monitor Memory**
```powershell
# Check memory usage
Get-Process python | Select-Object Name, @{Name="Memory(MB)";Expression={$_.WS / 1MB}}

# Or use Python
python -c "import psutil; print(f'Memory: {psutil.Process().memory_info().rss / 1024**2:.1f} MB')"
```

**Solution D: Restart Application**
```powershell
# Stop all Python processes
Get-Process python | Stop-Process

# Restart application
streamlit run streamlit_app.py
```

---

## Installation & Setup Issues

### Issue: UV Package Manager Not Found

**Symptoms:**
```
uv: command not found
The term 'uv' is not recognized
```

**Solutions:**

**Solution A: Install UV**
```powershell
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or use pip
pip install uv

# Verify installation
uv --version
```

**Solution B: Use pip Instead**
```powershell
# Use pip for all commands
pip install -e .
pip list
pip install --upgrade package-name
```

---

### Issue: Virtual Environment Creation Failed

**Symptoms:**
```
Failed to create virtual environment
Access denied
Permission error
```

**Solutions:**

**Solution A: Run as Administrator**
```powershell
# Right-click PowerShell → Run as Administrator
uv venv
```

**Solution B: Check Permissions**
```powershell
# Check directory permissions
Get-Acl . | Format-List

# Take ownership if needed
takeown /f . /r /d y
```

**Solution C: Use Python Built-in**
```powershell
# Use Python's built-in venv
python -m venv .venv

# Activate
.venv\Scripts\Activate.ps1

# Install packages
pip install -e .
```

---

### Issue: SSL Certificate Errors

**Symptoms:**
```
SSL: CERTIFICATE_VERIFY_FAILED
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**Solutions:**

**Solution A: Update Certificates**
```powershell
# Update CA certificates
uv pip install --upgrade certifi

# Or
python -m pip install --upgrade certifi
```

**Solution B: Temporary Bypass (Development Only)**
```python
# NOT for production!
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

**Solution C: Set Certificate Path**
```powershell
# Set environment variable
$env:SSL_CERT_FILE="C:\path\to\cacert.pem"
```

---

## Runtime Errors

### Issue: "RecursionError: maximum recursion depth exceeded"

**Symptoms:**
```
RecursionError: maximum recursion depth exceeded
```

**Cause:** Infinite loop in agent workflow or circular dependencies.

**Solutions:**

**Solution A: Set Recursion Limit**
```python
# In graph.py
supervisor = create_supervisor(
    max_iterations=25  # Limit agent loops
)
```

**Solution B: Check Agent Logic**
```python
# Ensure agents return properly
def agent_function(state):
    # Do work
    return {
        "messages": [response],
        "next": "END"  # Always specify next step
    }
```

**Solution C: Add Debug Logging**
```python
# Track execution path
import logging
logger.setLevel(logging.DEBUG)

# Monitor recursion
print(f"Recursion depth: {len(state['messages'])}")
```

---

### Issue: "KeyError" in State Management

**Symptoms:**
```
KeyError: 'messages'
KeyError: 'thread_id'
```

**Cause:** Missing state keys or incorrect state initialization.

**Solutions:**

**Solution A: Initialize State Properly**
```python
# Ensure all required keys exist
initial_state = {
    "messages": [],
    "user_id": "default_user",
    "thread_id": str(uuid.uuid4())
}
```

**Solution B: Use .get() Method**
```python
# Safer access
messages = state.get("messages", [])
user_id = state.get("user_id", "default_user")
```

**Solution C: Validate State**
```python
# Add validation
required_keys = ["messages", "user_id"]
for key in required_keys:
    if key not in state:
        raise ValueError(f"Missing required state key: {key}")
```

---

## API & Network Issues

### Issue: CORS Errors in Browser

**Symptoms:**
```
Access to fetch at 'http://localhost:8000' has been blocked by CORS policy
No 'Access-Control-Allow-Origin' header present
```

**Solutions:**

**Solution A: Enable CORS (Already Done)**
```python
# Verify in src/api.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Solution B: Use Proxy**
```javascript
// In frontend config
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
```

---

### Issue: API Returns 422 Validation Error

**Symptoms:**
```
{"detail": [{"loc": ["body", "message"], "msg": "field required", "type": "value_error.missing"}]}
```

**Cause:** Request body doesn't match Pydantic model.

**Solutions:**

**Solution A: Check Request Format**
```javascript
// Correct format
const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        message: "Hello",
        user_id: "user_123",
        thread_id: "thread_456"  // Optional
    })
});
```

**Solution B: Verify Pydantic Model**
```python
# Check model in src/api.py
class ChatRequest(BaseModel):
    message: str  # Required
    user_id: str  # Required
    thread_id: Optional[str] = None  # Optional
```

**Solution C: Use API Docs**
```
Open: http://localhost:8000/docs
Try out endpoints with correct schemas
```

---

## Database Issues

### Issue: Database Schema Mismatch

**Symptoms:**
```
sqlite3.OperationalError: no such table: orders
sqlite3.OperationalError: no such column: new_column
```

**Solutions:**

**Solution A: Check Database Schema**
```powershell
# Inspect database
sqlite3 data\trading_orders.db ".schema"

# List tables
sqlite3 data\trading_orders.db ".tables"
```

**Solution B: Recreate Database**
```powershell
# Backup existing
Copy-Item data\trading_orders.db data\trading_orders_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db

# Delete and recreate
Remove-Item data\trading_orders.db
python -c "from src.agent.database_tools import init_database; init_database()"
```

**Solution C: Migrate Schema**
```python
# Add migration script
import sqlite3

conn = sqlite3.connect('data/trading_orders.db')
cursor = conn.cursor()

# Add new column
cursor.execute("ALTER TABLE orders ADD COLUMN new_column TEXT")
conn.commit()
conn.close()
```

---

## Performance Issues

### Issue: Slow Application Response

**Symptoms:**
- Long wait times for responses
- UI freezing
- Timeout errors

**Solutions:**

**Solution A: Use Streaming**
```python
# In Streamlit
for event in supervisor.stream(config):
    if messages := event.get("messages"):
        st.write(messages[-1].content)
```

**Solution B: Optimize Prompts**
```python
# Shorter, clearer prompts
# Avoid overly long context
# Use specific instructions
```

**Solution C: Cache Results**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_stock_data(symbol: str):
    # Expensive operation
    return data
```

**Solution D: Use Faster Model**
```python
# gpt-4o-mini instead of gpt-4o
llm = ChatOpenAI(model="gpt-4o-mini")
```

---

## Security & Safety Issues

### Issue: Input Validation Failures

**Symptoms:**
```
Input validation failed: potentially malicious patterns detected
Safety violation: prompt injection attempt
```

**Cause:** User input triggered safety guardrails.

**Solutions:**

**Solution A: Review Input**
```python
# Check what triggered validation
from src.agent.guardrails_integration import SafetyLayer

safety = SafetyLayer()
result = safety.validate_input(user_message)
print("Validation result:", result)
```

**Solution B: Adjust Sensitivity**
```python
# In guardrails_integration.py
class InputGuard:
    def __init__(self, max_length: int = 10000):
        self.max_length = max_length
        # Adjust forbidden_patterns list
```

**Solution C: Whitelist Safe Patterns**
```python
# Add exceptions for legitimate use cases
safe_patterns = ["system:", "instructions:"]
if any(pattern in user_input for pattern in safe_patterns):
    # Allow if context is safe
    pass
```

---

## Deployment Issues

### Issue: Docker Build Fails

**Symptoms:**
```
ERROR: failed to solve
Cannot copy file
Dockerfile parse error
```

**Solutions:**

**Solution A: Check Dockerfile**
```dockerfile
# Ensure correct paths
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -e .
```

**Solution B: Build with No Cache**
```powershell
docker build --no-cache -t nextrade:latest .
```

**Solution C: Check .dockerignore**
```
# Don't copy unnecessary files
__pycache__/
*.pyc
.venv/
.git/
```

---

### Issue: Environment Variables Not Loading

**Symptoms:**
```
Config value not found
API key missing in production
```

**Solutions:**

**Solution A: Check .env File**
```powershell
# Verify .env exists
Test-Path .env

# Check contents (be careful with secrets!)
Get-Content .env | Select-String "OPENAI"
```

**Solution B: Set in Production**
```powershell
# Azure App Service
az webapp config appsettings set --name myapp --resource-group mygroup --settings OPENAI_API_KEY=sk-xxx

# Docker
docker run -e OPENAI_API_KEY=sk-xxx nextrade:latest
```

---

## FAQ

### General Questions

**Q: What Python version is required?**  
**A:** Python 3.11 or higher is required. Check with `python --version`.

**Q: Can I use this without an OpenAI API key?**  
**A:** No, the system requires OpenAI API access for the LLM. You can modify it to use other LLM providers (Anthropic, Azure OpenAI, etc.) but an LLM is required.

**Q: Is the system free to use?**  
**A:** The code is open-source, but you'll incur costs from:
- OpenAI API usage (pay-per-token)
- Cloud hosting (if deploying to cloud)
- LangSmith tracing (optional, has free tier)

**Q: How much does it cost to run?**  
**A:** Costs vary based on usage:
- Development: ~$1-5/day with moderate testing
- Production: Depends on user volume and request frequency
- Using `gpt-4o-mini` reduces costs significantly vs `gpt-4o`

**Q: Can I run this offline?**  
**A:** No, the system requires internet connectivity for:
- OpenAI API calls
- Package installation
- LangSmith tracing (if enabled)

### Technical Questions

**Q: What's the difference between Direct Mode and API Mode?**  
**A:** 
- **Direct Mode:** Streamlit directly uses LangGraph supervisor (simpler, single-user)
- **API Mode:** Streamlit connects via FastAPI (scalable, multi-user, stateless)

**Q: How do I add a new agent?**  
**A:** 
1. Define agent function in `src/agent/tools.py`
2. Register with supervisor in `src/agent/graph.py`
3. Add routing logic in supervisor
4. Update state management if needed

**Q: Can I use a different LLM provider?**  
**A:** Yes! Modify `src/agent/graph.py`:
```python
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-sonnet-20240229")
```

**Q: How do I customize the safety guardrails?**  
**A:** Edit `src/agent/guardrails_integration.py`:
- Modify `InputGuard.forbidden_patterns`
- Adjust `InputGuard.max_length`
- Add custom validators to `SafetyLayer`

**Q: Where are logs stored?**  
**A:**
- **Application logs:** stderr (console output)
- **Compliance logs:** `compliance.log` in root directory
- **LangSmith traces:** LangSmith dashboard (if enabled)

### Troubleshooting Questions

**Q: Why is the app so slow?**  
**A:** Common causes:
- Using `gpt-4o` instead of `gpt-4o-mini`
- Large conversation history
- Network latency
- LLM API throttling

**Solutions:** Use faster model, implement streaming, limit context

**Q: Why do I get "Module not found" errors?**  
**A:** 
- Virtual environment not activated (run `.venv\Scripts\Activate.ps1`)
- Package not installed (run `uv pip install -e .`)
- Wrong working directory (must be in project root)

**Q: How do I reset everything?**  
**A:**
```powershell
# 1. Stop all processes
Get-Process python,streamlit | Stop-Process

# 2. Remove virtual environment
Remove-Item -Recurse -Force .venv

# 3. Clear caches
Remove-Item -Recurse -Force __pycache__, .pytest_cache, .streamlit

# 4. Recreate environment
uv venv
.venv\Scripts\Activate.ps1
uv pip install -e .

# 5. Restart application
streamlit run streamlit_app.py
```

**Q: How do I view detailed error logs?**  
**A:**
```powershell
# Run with debug logging
$env:LANGCHAIN_VERBOSE="true"
streamlit run streamlit_app.py

# Or check compliance logs
Get-Content compliance.log -Tail 50
```

### Deployment Questions

**Q: Can I deploy to Heroku/AWS/Azure?**  
**A:** Yes! See `SETUP.md` for detailed instructions. The system is cloud-agnostic and supports:
- Azure App Service
- AWS Elastic Beanstalk
- Google Cloud Run
- Heroku
- Any Docker-compatible platform

**Q: How do I secure the API in production?**  
**A:** Add authentication:
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/chat")
async def chat(request: ChatRequest, token = Depends(security)):
    # Verify token
    if not verify_token(token.credentials):
        raise HTTPException(401, "Invalid token")
    # Continue...
```

**Q: How do I scale horizontally?**  
**A:**
- Use stateless API mode
- Deploy multiple API instances
- Add load balancer (Nginx, Azure Load Balancer, etc.)
- Use Redis for shared state
- Implement connection pooling

---

## Recovery Procedures

### Complete System Reset

Use when nothing else works:

```powershell
# 1. Stop all processes
Get-Process python,streamlit,uvicorn | Stop-Process -Force

# 2. Backup important data
New-Item -ItemType Directory -Force backups
Copy-Item data\trading_orders.db backups\db_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db
Copy-Item compliance.log backups\compliance_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').log

# 3. Clean environment
Remove-Item -Recurse -Force .venv, __pycache__, .pytest_cache, htmlcov, .streamlit

# 4. Recreate environment
uv venv
.venv\Scripts\Activate.ps1

# 5. Reinstall packages
uv pip install -e .

# 6. Verify installation
python -c "from src.agent.graph import create_supervisor; print('✅ Installation OK')"

# 7. Test database
python -c "from src.agent.database_tools import init_database; init_database(); print('✅ Database OK')"

# 8. Start application
streamlit run streamlit_app.py
```

### Database Recovery

When database is corrupted or inaccessible:

```powershell
# 1. Backup current database
Copy-Item data\trading_orders.db backups\corrupted_$(Get-Date -Format 'yyyyMMdd_HHmmss').db

# 2. Try integrity check
sqlite3 data\trading_orders.db "PRAGMA integrity_check;"

# 3a. If repairable, dump and restore
sqlite3 data\trading_orders.db ".dump" | sqlite3 data\trading_orders_repaired.db
Move-Item -Force data\trading_orders_repaired.db data\trading_orders.db

# 3b. If not repairable, restore from backup
Copy-Item backups\db_backup_latest.db data\trading_orders.db

# 3c. If no backup, recreate (loses data)
Remove-Item data\trading_orders.db
python -c "from src.agent.database_tools import init_database; init_database()"

# 4. Verify database
python -c "from src.agent.database_tools import get_user_orders; print(get_user_orders('test_user'))"
```

### API Server Recovery

When FastAPI server won't start:

```powershell
# 1. Kill all processes on port 8000
$port = 8000
$processId = (Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue).OwningProcess
if ($processId) { Stop-Process -Id $processId -Force }

# 2. Clear Python cache
Remove-Item -Recurse -Force src\__pycache__, src\agent\__pycache__

# 3. Test imports
python -c "from src.api import app; print('✅ API imports OK')"

# 4. Start with verbose logging
uvicorn src.api:app --reload --log-level debug

# 5. Verify health
Start-Sleep -Seconds 3
curl http://localhost:8000/health
```

### Configuration Recovery

When configuration is messed up:

```powershell
# 1. Backup current config
Copy-Item .env backups\.env.backup
Copy-Item langgraph.json backups\langgraph.json.backup

# 2. Restore default .env
@"
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here

# LangSmith Configuration (Optional)
LANGCHAIN_API_KEY=lsv2_your-key-here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=nextrade

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
"@ | Out-File -FilePath .env -Encoding UTF8

# 3. Verify environment loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key loaded:', bool(os.getenv('OPENAI_API_KEY')))"

# 4. Restart application
streamlit run streamlit_app.py
```

---

## Getting Help

### Self-Service Resources

1. **Documentation**
   - [README.md](../README.md) - Complete system documentation
   - [SETUP.md](SETUP.md) - Setup and deployment guide
   - [QUICK_START.md](QUICK_START.md) - Quick setup guide
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
   - [MONITORING.md](MONITORING.md) - Monitoring and maintenance

2. **Interactive Tools**
   - API Docs: http://localhost:8000/docs (when API running)
   - Health Check: http://localhost:8000/health
   - LangSmith Dashboard: https://smith.langchain.com

3. **Logs & Debugging**
   - Application logs: stderr output
   - Compliance logs: `compliance.log`
   - Test output: `pytest -v --log-cli-level=DEBUG`

### Support Channels

1. **GitHub Issues**
   - Repository: https://github.com/VeereshGowda/NexTrade-MultiAgent-Assistant
   - Search existing issues
   - Create new issue with:
     - Error message
     - Steps to reproduce
     - System information (OS, Python version)
     - Relevant log excerpts

2. **Community Support**
   - Stack Overflow: Tag with `langgraph`, `langchain`, `fastapi`
   - LangChain Discord: https://discord.gg/langchain
   - OpenAI Community Forum

3. **Documentation Bugs**
   - Submit PR with documentation fixes
   - Open issue for unclear instructions

### Before Asking for Help

Gather this information:

```powershell
# 1. System information
python --version
uv --version
Get-ComputerInfo | Select-Object WindowsVersion, OsArchitecture

# 2. Package versions
uv pip list | Select-String "langgraph|langchain|fastapi|streamlit|openai"

# 3. Recent errors
Get-Content compliance.log -Tail 20

# 4. Test results
pytest -v --tb=short

# 5. Configuration (redact secrets!)
Get-Content .env | Select-String -Pattern "KEY" -Context 0,0
```

---

## Quick Reference Card

### Essential Commands

```powershell
# Activate environment
.venv\Scripts\Activate.ps1

# Start Streamlit (Direct Mode)
streamlit run streamlit_app.py

# Start FastAPI (API Mode)
uvicorn src.api:app --reload

# Run tests
pytest -v

# Check health
curl http://localhost:8000/health

# View logs
Get-Content compliance.log -Tail 50 -Wait

# Reset database
Remove-Item data\trading_orders.db
python -c "from src.agent.database_tools import init_database; init_database()"

# Clear cache
Remove-Item -Recurse -Force __pycache__, .pytest_cache, .streamlit
```

### Emergency Recovery

```powershell
# Kill all processes
Get-Process python,streamlit,uvicorn | Stop-Process -Force

# Fresh start
Remove-Item -Recurse -Force .venv
uv venv
.venv\Scripts\Activate.ps1
uv pip install -e .

# Start application
streamlit run streamlit_app.py
```

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Nov 5, 2025 | Initial comprehensive troubleshooting guide |

---

**For additional support, refer to:**
- [README.md](../README.md) - Main documentation
- [MONITORING.md](MONITORING.md) - Operations guide
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference

**Need more help?** Open an issue on GitHub with detailed information about your problem.

---

**Version:** 1.0.0  
**Maintained By:** DevOps Team  
**Last Updated:** November 5, 2025
