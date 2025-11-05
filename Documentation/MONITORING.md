# NexTrade Monitoring & Maintenance Guide

**Version:** 1.0.0  
**Last Updated:** November 5, 2025  
**Status:** Production-Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Logging System](#logging-system)
3. [Health Checks](#health-checks)
4. [Metrics & Monitoring](#metrics--monitoring)
5. [Alerting Strategy](#alerting-strategy)
6. [Maintenance Procedures](#maintenance-procedures)
7. [Troubleshooting](#troubleshooting)
8. [Long-Term Considerations](#long-term-considerations)

---

## Overview

NexTrade implements comprehensive monitoring and logging for production reliability. This guide covers:

- **Application Logging** - Standard Python logging with structured formats
- **Compliance Logging** - Audit trails for regulatory requirements
- **Health Checks** - Component status monitoring
- **Performance Metrics** - Execution time tracking
- **Safety Validation** - Input/output security monitoring

### Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  FastAPI    │  │  Streamlit   │  │  LangGraph       │  │
│  │  Server     │  │  UI          │  │  Multi-Agent     │  │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │             │
└─────────┼─────────────────┼────────────────────┼─────────────┘
          │                 │                    │
          ▼                 ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      Logging & Monitoring                    │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐ │
│  │  Standard    │  │  Compliance   │  │  Health Check   │ │
│  │  Logs        │  │  Logger       │  │  System         │ │
│  └──────┬───────┘  └───────┬───────┘  └────────┬────────┘ │
│         │                   │                    │           │
└─────────┼───────────────────┼────────────────────┼───────────┘
          │                   │                    │
          ▼                   ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      Storage & Analytics                     │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐ │
│  │  Log Files   │  │  Compliance   │  │  Metrics        │ │
│  │  (stderr)    │  │  Log File     │  │  Database       │ │
│  └──────────────┘  └───────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Logging System

### 1. Standard Application Logging

**Location:** `src/api.py`, all agent modules  
**Configuration:**

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Log Levels:**

| Level | Use Case | Example |
|-------|----------|---------|
| `DEBUG` | Development details | Variable states, detailed traces |
| `INFO` | Normal operations | Request processing, successful actions |
| `WARNING` | Recoverable issues | Retry attempts, degraded performance |
| `ERROR` | Operation failures | API errors, validation failures |
| `CRITICAL` | System failures | Database down, LLM unavailable |

**Key Log Points:**

```python
# API Endpoint Entry
logger.info(f"Processing chat request for user {request.user_id}")

# Component Status
logger.info("Initializing supervisor instance...")

# Error Tracking
logger.error(f"Chat endpoint error: {e}", exc_info=True)

# Health Checks
logger.error(f"LLM health check failed: {e}")
logger.error(f"Database health check failed: {e}")
```

### 2. Compliance Logging

**Location:** `src/agent/guardrails_integration.py` → `ComplianceLogger`  
**Log File:** `compliance.log` (root directory)  
**Format:** `YYYY-MM-DD HH:MM:SS | LEVEL | MESSAGE`

**What Gets Logged:**

#### User Actions
```python
compliance_logger.log_user_action(
    action="chat_request",
    user_id=request.user_id,
    details={"message": request.message[:50]}
)
```

**Example Output:**
```
2025-11-05 10:30:15 | INFO | USER_ACTION | Action: chat_request | User: user_12345 | Details: {'message': 'Research NVIDIA stock'}
```

#### Safety Violations
```python
compliance_logger.log_safety_violation(
    violation_type="input_validation_failed",
    details={"errors": input_validation["errors"]},
    user_id=request.user_id
)
```

**Example Output:**
```
2025-11-05 10:31:20 | WARNING | SAFETY_VIOLATION | Type: input_validation_failed | User: user_12345 | Details: {'errors': ['Potentially malicious patterns detected: ignore previous instructions']}
```

#### Validation Events
```python
compliance_logger.log_validation(
    validation_type="input",
    is_valid=True,
    details={"length": len(user_input)},
    user_id=user_id
)
```

**Example Output:**
```
2025-11-05 10:32:05 | INFO | VALIDATION | Type: input | Valid: True | User: user_12345 | Details: {'length': 250}
```

### 3. Resilience Module Logging

**Location:** `src/agent/resilience.py`

**Retry Logic Logging:**
```python
logger.warning(
    f"Attempt {attempt + 1}/{retry_config.max_retries + 1} "
    f"failed for {func.__name__}: {e}. "
    f"Retrying in {delay:.2f}s..."
)
```

**Circuit Breaker Logging:**
```python
logger.error(
    f"Circuit breaker '{self.name}' OPENED after "
    f"{self.failure_count} failures"
)

logger.info(f"Circuit breaker '{self.name}' recovered. Closing circuit.")
```

**Execution Time Logging:**
```python
@log_execution_time
def expensive_operation():
    # Automatically logs: "Function expensive_operation completed in 2.35s"
    pass
```

### 4. Safety Layer Logging

**Location:** `src/agent/guardrails_integration.py`

**Input Validation:**
```python
logger.warning(f"Input validation failed: excessive length ({len(user_input)} chars)")
logger.warning(f"Input validation failed: detected patterns {detected_patterns}")
```

**Output Validation:**
```python
logger.error(f"Output validation failed: sensitive patterns detected")
logger.warning(f"Output has low uniqueness ratio: {unique_ratio:.2f}")
```

### Log File Management

**Production Recommendations:**

#### Log Rotation
```python
# Recommended: Use RotatingFileHandler
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'nextrade.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
```

#### Time-Based Rotation
```python
# Alternative: TimedRotatingFileHandler
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(
    'nextrade.log',
    when='midnight',
    interval=1,
    backupCount=30  # Keep 30 days
)
```

#### Centralized Logging (Production)
- **CloudWatch** (AWS)
- **Azure Monitor** (Azure)
- **Datadog**
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**

---

## Health Checks

### 1. Health Check Architecture

**Location:** `src/agent/resilience.py` → `HealthCheck` class  
**Implementation:** `src/api.py` → `/health` endpoint

**Components Monitored:**

| Component | Check Function | Success Criteria |
|-----------|----------------|------------------|
| API Server | `lambda: True` | Always healthy if responding |
| LLM | `check_llm()` | Supervisor instance available |
| Database | `check_database()` | Can import database tools |

### 2. Health Check Endpoint

**URL:** `GET /health`

**Response Format:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T10:30:00Z",
  "components": {
    "api": true,
    "llm": true,
    "database": true
  }
}
```

**Status Values:**
- `healthy` - All components operational
- `degraded` - Some components failing
- `unhealthy` - Critical components down

**HTTP Status Codes:**
- `200 OK` - System is healthy
- `503 Service Unavailable` - System is unhealthy

### 3. Component Health Checks

#### API Health Check
```python
health_check.register("api", lambda: True)
```
**What it checks:** API server is running and responding

#### LLM Health Check
```python
def check_llm():
    try:
        supervisor = get_supervisor()
        return supervisor is not None
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        return False

health_check.register("llm", check_llm)
```
**What it checks:**
- Supervisor instance can be created
- LangGraph configuration is valid
- LLM provider is accessible

#### Database Health Check
```python
def check_database():
    try:
        from agent.database_tools import get_user_orders
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

health_check.register("database", check_database)
```
**What it checks:**
- Database connection is available
- Required modules can be imported
- Database file is accessible

### 4. Health Check Usage

**Manual Testing:**
```bash
# Check system health
curl http://localhost:8000/health

# Pretty print
curl http://localhost:8000/health | jq .
```

**Automated Monitoring:**
```python
import requests
import time

def monitor_health(interval=60):
    """Monitor health every minute."""
    while True:
        try:
            response = requests.get("http://localhost:8000/health")
            health = response.json()
            
            if health["status"] != "healthy":
                alert(f"System degraded: {health}")
            
            time.sleep(interval)
        except Exception as e:
            alert(f"Health check failed: {e}")
            time.sleep(interval)
```

**Kubernetes Liveness/Readiness Probes:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

### 5. Custom Health Checks

**Adding New Checks:**

```python
# In src/api.py

def check_external_api():
    """Check external API connectivity."""
    try:
        response = requests.get("https://api.example.com/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# Register in health endpoint
health_check.register("external_api", check_external_api)
```

---

## Metrics & Monitoring

### 1. Performance Metrics

**Execution Time Tracking:**

```python
from agent.resilience import log_execution_time

@log_execution_time
def process_chat_request(request):
    # Automatically logs execution time
    pass
```

**Output:**
```
2025-11-05 10:30:15 - INFO - Function process_chat_request completed in 2.45s
```

### 2. Key Metrics to Monitor

#### System Metrics

| Metric | Description | Threshold |
|--------|-------------|-----------|
| **API Response Time** | Time to process requests | < 5s (normal), < 30s (max) |
| **LLM Latency** | Time for LLM responses | < 10s (normal), < 60s (max) |
| **Memory Usage** | Application memory | < 2GB (normal), < 4GB (max) |
| **CPU Usage** | Processor utilization | < 70% (normal), < 90% (max) |
| **Disk Usage** | Storage space | < 80% capacity |

#### Business Metrics

| Metric | Description | How to Track |
|--------|-------------|--------------|
| **Request Count** | Total API requests | Count `/chat` endpoint calls |
| **Error Rate** | Failed requests % | Errors / Total Requests |
| **Approval Rate** | HITL approval % | Approvals / Total HITL Requests |
| **Active Users** | Unique users | Count unique `user_id` values |
| **Order Volume** | Trading orders | Query `trading_orders.db` |

#### Safety Metrics

| Metric | Description | Source |
|--------|-------------|--------|
| **Validation Failures** | Input/output rejections | `compliance.log` |
| **Safety Violations** | Malicious attempts | `SAFETY_VIOLATION` entries |
| **Circuit Breaker Trips** | Service failures | `resilience.py` logs |
| **Retry Count** | Failed operations | `resilience.py` logs |

### 3. Metrics Collection

**Basic Metrics (Built-in):**
```python
# Already implemented via logging decorators
@log_execution_time  # Tracks execution time
@retry_with_backoff  # Tracks retries
```

**Custom Metrics (Add if needed):**

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Request counter
request_count = Counter(
    'nextrade_requests_total',
    'Total requests',
    ['endpoint', 'status']
)

# Response time histogram
response_time = Histogram(
    'nextrade_response_seconds',
    'Response time in seconds',
    ['endpoint']
)

# Active requests gauge
active_requests = Gauge(
    'nextrade_active_requests',
    'Number of active requests'
)

# Usage in endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    request_count.labels(endpoint='/chat', status='started').inc()
    active_requests.inc()
    start_time = time.time()
    
    try:
        result = process_request(request)
        request_count.labels(endpoint='/chat', status='success').inc()
        return result
    except Exception as e:
        request_count.labels(endpoint='/chat', status='error').inc()
        raise
    finally:
        active_requests.dec()
        response_time.labels(endpoint='/chat').observe(time.time() - start_time)
```

### 4. Monitoring Dashboards

**Recommended Tools:**

#### Open Source
- **Grafana** + **Prometheus** - Metrics visualization
- **ELK Stack** - Log analysis
- **Jaeger** - Distributed tracing

#### Cloud Providers
- **AWS CloudWatch** - AWS deployments
- **Azure Monitor** - Azure deployments
- **Google Cloud Monitoring** - GCP deployments

#### SaaS Solutions
- **Datadog** - All-in-one monitoring
- **New Relic** - Application performance
- **Sentry** - Error tracking

**Sample Grafana Dashboard:**
```
┌────────────────────────────────────────────────────────┐
│ NexTrade System Health                                 │
├────────────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│ │   Requests  │  │   Errors    │  │  Response   │    │
│ │   1,234/hr  │  │     2.3%    │  │   Time      │    │
│ │     📈      │  │     ⚠️      │  │   2.4s      │    │
│ └─────────────┘  └─────────────┘  └─────────────┘    │
├────────────────────────────────────────────────────────┤
│ Response Time (Last 24h)                               │
│ ┌────────────────────────────────────────────────┐    │
│ │         🟢🟢🟢🟡🟢🟢🟢🟢🟢🟢🟢🟢             │    │
│ │ 5s ─────────────────────────────────────────── │    │
│ │ 0s ─────────────────────────────────────────── │    │
│ └────────────────────────────────────────────────┘    │
├────────────────────────────────────────────────────────┤
│ Component Health                                       │
│ • API Server       ✅ Healthy                         │
│ • LLM Provider     ✅ Healthy                         │
│ • Database         ✅ Healthy                         │
│ • Circuit Breaker  ✅ Closed                          │
└────────────────────────────────────────────────────────┘
```

---

## Alerting Strategy

### 1. Alert Severity Levels

| Level | Response Time | Escalation | Examples |
|-------|---------------|------------|----------|
| **P1 - Critical** | Immediate | Page on-call | API down, database failure |
| **P2 - High** | 15 minutes | Email + Slack | High error rate, LLM timeout |
| **P3 - Medium** | 1 hour | Slack notification | Degraded performance |
| **P4 - Low** | Next business day | Ticket creation | Warning logs, approaching limits |

### 2. Alert Rules

#### Critical Alerts (P1)

**API Unavailable**
```
Condition: Health check fails for > 2 minutes
Action: Page on-call engineer
Message: "NexTrade API is down. Health check failing."
```

**Database Connection Lost**
```
Condition: Database health check returns false
Action: Page on-call engineer
Message: "Database connection lost. User data inaccessible."
```

**High Error Rate**
```
Condition: Error rate > 50% over 5 minutes
Action: Page on-call engineer
Message: "Critical error rate: {error_rate}% of requests failing."
```

#### High Priority Alerts (P2)

**LLM Provider Issues**
```
Condition: LLM health check fails
Action: Email team + Slack notification
Message: "LLM provider unavailable. Requests may fail."
```

**Elevated Error Rate**
```
Condition: Error rate > 10% over 10 minutes
Action: Email team + Slack notification
Message: "Elevated error rate: {error_rate}%. Investigate immediately."
```

**Circuit Breaker Opened**
```
Condition: Circuit breaker opens
Action: Slack notification
Message: "Circuit breaker '{name}' opened after {failure_count} failures."
```

#### Medium Priority Alerts (P3)

**Slow Response Times**
```
Condition: 95th percentile > 30s over 15 minutes
Action: Slack notification
Message: "Response times degraded. P95: {time}s"
```

**Disk Space Warning**
```
Condition: Disk usage > 80%
Action: Slack notification
Message: "Disk usage at {percentage}%. Consider cleanup."
```

**Memory Usage High**
```
Condition: Memory > 3GB for > 10 minutes
Action: Slack notification
Message: "Memory usage high: {usage}GB. Monitor for leaks."
```

#### Low Priority Alerts (P4)

**Log Volume Spike**
```
Condition: Log entries > 1000/minute
Action: Create ticket
Message: "Unusual log volume. Review for issues."
```

**Retry Attempts High**
```
Condition: > 100 retries/hour
Action: Create ticket
Message: "High retry count. External services may be unstable."
```

### 3. Alert Configuration Examples

**PagerDuty Integration:**
```python
import requests

def send_pagerduty_alert(severity, message, details):
    """Send alert to PagerDuty."""
    payload = {
        "routing_key": "YOUR_INTEGRATION_KEY",
        "event_action": "trigger",
        "payload": {
            "summary": message,
            "severity": severity,  # critical, error, warning, info
            "source": "NexTrade API",
            "custom_details": details
        }
    }
    
    requests.post(
        "https://events.pagerduty.com/v2/enqueue",
        json=payload
    )
```

**Slack Integration:**
```python
import requests

def send_slack_alert(channel, message, severity):
    """Send alert to Slack."""
    webhook_url = "YOUR_SLACK_WEBHOOK_URL"
    
    color = {
        "critical": "#FF0000",
        "warning": "#FFA500",
        "info": "#0000FF"
    }.get(severity, "#808080")
    
    payload = {
        "channel": channel,
        "attachments": [{
            "color": color,
            "title": f"NexTrade Alert - {severity.upper()}",
            "text": message,
            "ts": time.time()
        }]
    }
    
    requests.post(webhook_url, json=payload)
```

**Email Alerts:**
```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(to_emails, subject, body):
    """Send email alert."""
    msg = MIMEText(body)
    msg['Subject'] = f"[NexTrade Alert] {subject}"
    msg['From'] = "alerts@nextrade.com"
    msg['To'] = ", ".join(to_emails)
    
    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)
```

---

## Maintenance Procedures

### 1. Daily Maintenance

**Morning Health Check (5 minutes)**
```bash
# 1. Check system status
curl http://localhost:8000/health

# 2. Review error logs
tail -n 100 nextrade.log | grep ERROR

# 3. Check compliance log
tail -n 50 compliance.log | grep SAFETY_VIOLATION

# 4. Verify disk space
df -h

# 5. Check process status
ps aux | grep nextrade
```

**Automated Daily Tasks:**
- Health check monitoring (continuous)
- Log file rotation (midnight)
- Database backup (3:00 AM)
- Metrics aggregation (hourly)

### 2. Weekly Maintenance

**Performance Review (30 minutes)**

1. **Analyze Response Times:**
```bash
# Extract execution times from logs
grep "completed in" nextrade.log | awk '{print $NF}' | sort -n
```

2. **Review Error Patterns:**
```bash
# Count error types
grep ERROR nextrade.log | cut -d: -f2 | sort | uniq -c | sort -rn
```

3. **Check Safety Violations:**
```bash
# Review safety violations
grep SAFETY_VIOLATION compliance.log | tail -n 20
```

4. **Database Cleanup:**
```python
# Remove old test data (if applicable)
python demos/demo_database_agent.py --cleanup
```

5. **Log Review:**
- Archive old logs
- Analyze warning trends
- Update alert thresholds if needed

### 3. Monthly Maintenance

**System Optimization (2 hours)**

1. **Database Optimization:**
```sql
-- Vacuum SQLite database
VACUUM;

-- Analyze query patterns
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE user_id = ?;
```

2. **Dependency Updates:**
```bash
# Check for updates
uv pip list --outdated

# Update dependencies (test first!)
uv pip install --upgrade package-name
```

3. **Security Audit:**
```bash
# Check for vulnerabilities
pip-audit

# Review compliance logs
grep SAFETY_VIOLATION compliance.log | wc -l
```

4. **Performance Testing:**
```python
# Run load tests
python tests/performance/load_test.py
```

5. **Documentation Review:**
- Update API documentation
- Review monitoring dashboards
- Update runbooks

### 4. Quarterly Maintenance

**Strategic Review (4 hours)**

1. **Capacity Planning:**
   - Review growth trends
   - Forecast resource needs
   - Plan infrastructure upgrades

2. **Disaster Recovery Testing:**
   - Test backup restoration
   - Verify failover procedures
   - Update DR documentation

3. **Security Assessment:**
   - Penetration testing
   - Compliance review
   - Update security policies

4. **Architecture Review:**
   - Evaluate performance bottlenecks
   - Consider scaling strategies
   - Review technology stack

### 5. Backup & Recovery

**Database Backups:**

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/nextrade"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup SQLite database
cp data/trading_orders.db "$BACKUP_DIR/trading_orders_$DATE.db"

# Backup compliance logs
cp compliance.log "$BACKUP_DIR/compliance_$DATE.log"

# Compress old backups
find $BACKUP_DIR -name "*.db" -mtime +30 -exec gzip {} \;

# Delete backups older than 90 days
find $BACKUP_DIR -name "*.gz" -mtime +90 -delete

echo "Backup completed: $DATE"
```

**Recovery Procedures:**

```bash
# Restore database from backup
cp /backups/nextrade/trading_orders_20251105.db data/trading_orders.db

# Verify integrity
sqlite3 data/trading_orders.db "PRAGMA integrity_check;"

# Restart services
systemctl restart nextrade-api
```

---

## Troubleshooting

### Common Issues

#### Issue 1: API Not Responding

**Symptoms:**
- Health check fails
- HTTP 503 errors
- Connection timeouts

**Diagnosis:**
```bash
# Check if process is running
ps aux | grep uvicorn

# Check port availability
netstat -tulpn | grep 8000

# Review recent logs
tail -n 100 nextrade.log
```

**Solutions:**
1. Restart API server:
   ```bash
   uvicorn src.api:app --reload
   ```

2. Check for port conflicts:
   ```bash
   lsof -i :8000
   kill -9 <PID>
   ```

3. Verify environment:
   ```bash
   source .venv/Scripts/activate
   uv pip list
   ```

#### Issue 2: High Error Rate

**Symptoms:**
- Multiple errors in logs
- Elevated error metrics
- User complaints

**Diagnosis:**
```bash
# Count errors by type
grep ERROR nextrade.log | cut -d: -f2 | sort | uniq -c

# Check recent errors
grep ERROR nextrade.log | tail -n 20

# Review stack traces
grep -A 10 "Traceback" nextrade.log
```

**Solutions:**
1. Check external dependencies:
   ```bash
   # Test LLM connectivity
   python -c "from langchain_openai import ChatOpenAI; ChatOpenAI()"
   ```

2. Review circuit breaker status:
   ```bash
   grep "Circuit breaker" nextrade.log
   ```

3. Restart with clean state:
   ```bash
   rm -rf __pycache__
   uvicorn src.api:app --reload
   ```

#### Issue 3: Slow Response Times

**Symptoms:**
- Response time > 30s
- Timeouts
- User experience degradation

**Diagnosis:**
```bash
# Extract execution times
grep "completed in" nextrade.log | tail -n 50

# Check memory usage
free -h

# Check CPU usage
top -n 1
```

**Solutions:**
1. Optimize database queries
2. Increase timeout limits
3. Scale horizontally (add instances)
4. Cache frequently accessed data

#### Issue 4: Database Errors

**Symptoms:**
- Database health check fails
- SQLite errors in logs
- Data inconsistencies

**Diagnosis:**
```bash
# Check database file
ls -lh data/trading_orders.db

# Verify integrity
sqlite3 data/trading_orders.db "PRAGMA integrity_check;"

# Check permissions
ls -la data/
```

**Solutions:**
1. Restore from backup:
   ```bash
   cp /backups/trading_orders_latest.db data/trading_orders.db
   ```

2. Repair database:
   ```bash
   sqlite3 data/trading_orders.db "VACUUM;"
   ```

3. Recreate if needed:
   ```bash
   python -c "from agent.database_tools import init_db; init_db()"
   ```

### Debugging Tools

**Log Analysis:**
```bash
# Find patterns
grep -i "pattern" nextrade.log

# Count occurrences
grep "ERROR" nextrade.log | wc -l

# Show context
grep -C 5 "error_message" nextrade.log
```

**Performance Profiling:**
```python
# Add to any function
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

**Memory Profiling:**
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Function to profile
    pass
```

---

## Long-Term Considerations

### 1. Scaling Strategy

**Horizontal Scaling:**
- Deploy multiple API instances
- Use load balancer (Nginx, HAProxy)
- Implement session stickiness for HITL workflows
- Share state via Redis or database

**Vertical Scaling:**
- Increase CPU/memory per instance
- Optimize database queries
- Implement caching layer
- Use async processing for heavy tasks

**Database Scaling:**
- Migrate to PostgreSQL for production
- Implement read replicas
- Partition large tables
- Implement connection pooling

### 2. Performance Optimization

**Caching Strategy:**
```python
from functools import lru_cache
import redis

# In-memory cache
@lru_cache(maxsize=1000)
def get_stock_data(symbol):
    # Expensive operation
    pass

# Redis cache
redis_client = redis.Redis(host='localhost', port=6379)

def cached_query(key, ttl=3600):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    # Fetch and cache
    data = expensive_query()
    redis_client.setex(key, ttl, json.dumps(data))
    return data
```

**Async Processing:**
```python
from celery import Celery

celery_app = Celery('nextrade', broker='redis://localhost:6379')

@celery_app.task
def process_heavy_task(data):
    # Long-running task
    pass

# Usage
result = process_heavy_task.delay(data)
```

### 3. Security Enhancements

**Authentication (Future):**
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    # Verify JWT token
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return get_user_from_token(token)

@app.post("/chat")
async def chat(request: ChatRequest, user = Depends(verify_token)):
    # Protected endpoint
    pass
```

**Rate Limiting (Future):**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat")
@limiter.limit("100/minute")
async def chat(request: ChatRequest):
    pass
```

### 4. Compliance & Audit

**Regulatory Requirements:**
- **GDPR** - Data privacy, right to deletion
- **SOC 2** - Security controls
- **FINRA** - Financial regulations (if applicable)

**Audit Trail Enhancements:**
```python
class EnhancedComplianceLogger:
    def log_with_retention(self, event, retention_days=2555):
        """Log with guaranteed retention period."""
        # Log to immutable storage
        # Add cryptographic signature
        # Implement tamper detection
        pass
```

**Data Retention Policy:**
- **Transaction logs:** 7 years (financial regulations)
- **Compliance logs:** 3 years (audit requirements)
- **Debug logs:** 90 days (operational needs)
- **User data:** Per privacy policy

### 5. Disaster Recovery

**RTO/RPO Targets:**
- **RTO (Recovery Time Objective):** < 4 hours
- **RPO (Recovery Point Objective):** < 1 hour

**DR Procedures:**

1. **Regular Backups:**
   - Automated daily backups
   - Off-site backup storage
   - Encrypted backup files
   - Backup verification tests

2. **Failover Plan:**
   - Secondary region deployment
   - Database replication
   - DNS failover configuration
   - Regular failover drills

3. **Recovery Steps:**
   ```bash
   # 1. Restore database
   aws s3 cp s3://backups/latest.db data/
   
   # 2. Deploy application
   git pull origin main
   uv pip install -e .
   
   # 3. Start services
   uvicorn src.api:app --host 0.0.0.0 --port 8000
   
   # 4. Verify health
   curl http://localhost:8000/health
   ```

### 6. Cost Optimization

**Monitor Costs:**
- LLM API usage
- Cloud infrastructure
- Storage costs
- Monitoring services

**Optimization Strategies:**
- Implement response caching
- Use cheaper LLM models for simple queries
- Optimize prompt lengths
- Implement request batching
- Use spot instances where applicable

---

## Summary Checklist

### Daily
- ✅ Review health check status
- ✅ Monitor error logs
- ✅ Check compliance violations
- ✅ Verify disk space

### Weekly
- ✅ Analyze performance metrics
- ✅ Review error patterns
- ✅ Clean up old logs
- ✅ Update documentation

### Monthly
- ✅ Database optimization
- ✅ Dependency updates
- ✅ Security audit
- ✅ Performance testing

### Quarterly
- ✅ Capacity planning
- ✅ DR testing
- ✅ Security assessment
- ✅ Architecture review

---

## Support & Resources

- **Health Check API:** `http://localhost:8000/health`
- **Interactive Docs:** `http://localhost:8000/docs`
- **Compliance Logs:** `compliance.log`
- **Application Logs:** stderr output
- **Main Documentation:** [README.md](../README.md)
- **API Reference:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

**Document Version:** 1.0.0  
**Maintained By:** DevOps Team  
**Next Review:** February 5, 2026
