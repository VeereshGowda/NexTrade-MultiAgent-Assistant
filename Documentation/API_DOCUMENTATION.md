# NexTrade API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000` (Development) | `https://your-domain.com` (Production)  
**Protocol:** REST API over HTTPS  
**Format:** JSON

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL & Endpoints](#base-url--endpoints)
4. [API Endpoints](#api-endpoints)
5. [Request/Response Models](#requestresponse-models)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)
9. [SDKs & Client Libraries](#sdks--client-libraries)

---

## Overview

The NexTrade API provides programmatic access to the multi-agent trading system, enabling:

- **Intelligent Chat Interactions** - Communicate with specialized trading agents
- **Human-in-the-Loop (HITL) Approval** - Secure trading with mandatory approvals
- **Portfolio Management** - Access portfolio positions and order history
- **Health Monitoring** - Monitor system status and component health
- **Safety Validation** - Automatic input/output validation with Guardrails AI

### Key Features

- ✅ **RESTful Architecture** - Standard HTTP methods and status codes
- ✅ **JSON Format** - All requests and responses use JSON
- ✅ **OpenAPI/Swagger** - Interactive documentation at `/docs`
- ✅ **Type Safety** - Pydantic models for validation
- ✅ **Error Handling** - Comprehensive error responses
- ✅ **Async Support** - High-performance async endpoints

---

## Authentication

### Current Status

**Version 1.0.0:** No authentication required (development/demo mode)

### Future Versions

Production deployments should implement one of the following:

**Option 1: API Key Authentication**
```http
Authorization: Bearer YOUR_API_KEY
```

**Option 2: OAuth 2.0**
```http
Authorization: Bearer YOUR_OAUTH_TOKEN
```

**Option 3: JWT Tokens**
```http
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Base URL & Endpoints

### Development
```
http://localhost:8000
```

### Production
```
https://api.yourdomain.com
```

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## API Endpoints

### Summary Table

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | API information | No |
| `GET` | `/health` | System health check | No |
| `POST` | `/chat` | Chat with agents | No* |
| `POST` | `/approve` | Approve/reject actions | No* |
| `GET` | `/portfolio/{user_id}` | Get portfolio | No* |
| `GET` | `/orders/{user_id}` | Get order history | No* |

*Will require authentication in production

---

## API Endpoints

### 1. Root Endpoint

**Get API Information**

```http
GET /
```

#### Response

```json
{
  "name": "NexTrade Multi-Agent Trading API",
  "version": "1.0.0",
  "status": "operational",
  "docs": "/docs",
  "health": "/health"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | API name |
| `version` | string | API version |
| `status` | string | Operational status |
| `docs` | string | Documentation URL |
| `health` | string | Health check URL |

---

### 2. Health Check

**Check System Health**

```http
GET /health
```

#### Response

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

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Overall health: `healthy` or `unhealthy` |
| `timestamp` | string | ISO 8601 timestamp |
| `components` | object | Individual component statuses |
| `components.api` | boolean | API server status |
| `components.llm` | boolean | LLM connectivity status |
| `components.database` | boolean | Database connectivity status |

#### Status Codes

- `200 OK` - System is healthy
- `503 Service Unavailable` - System is unhealthy

---

### 3. Chat with Agents

**Send a message to the multi-agent system**

```http
POST /chat
```

#### Request Body

```json
{
  "message": "Research NVIDIA stock and provide analysis",
  "user_id": "user_12345",
  "thread_id": "thread_67890"
}
```

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User message to the agent |
| `user_id` | string | Yes | Unique user identifier |
| `thread_id` | string | No | Conversation thread ID (auto-generated if not provided) |

#### Response (Success)

```json
{
  "response": "Based on my research, NVIDIA Corporation (NVDA) shows strong fundamentals...",
  "thread_id": "thread_67890",
  "timestamp": "2025-11-05T10:30:00Z",
  "requires_approval": false
}
```

#### Response (Approval Required)

```json
{
  "response": "Action requires human approval",
  "thread_id": "thread_67890",
  "timestamp": "2025-11-05T10:30:00Z",
  "requires_approval": true,
  "approval_details": {
    "action": "place_order",
    "symbol": "NVDA",
    "quantity": 10,
    "price": 145.50,
    "estimated_cost": 1455.00
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | Agent response text |
| `thread_id` | string | Conversation thread ID |
| `timestamp` | string | ISO 8601 timestamp |
| `requires_approval` | boolean | Whether human approval is needed |
| `approval_details` | object | Details for approval (if required) |
| `approved` | boolean | Approval status (if applicable) |

#### Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid input or validation failed
- `500 Internal Server Error` - Server error

#### Example: Research Query

**Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the top 3 AI companies for investment?",
    "user_id": "user_12345"
  }'
```

**Response:**
```json
{
  "response": "Based on current market analysis, here are the top 3 AI companies:\n1. NVIDIA (NVDA) - Leading GPU manufacturer...",
  "thread_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "timestamp": "2025-11-05T10:30:00Z",
  "requires_approval": false
}
```

#### Example: Trading Query (HITL)

**Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Buy 10 shares of NVDA at market price",
    "user_id": "user_12345",
    "thread_id": "thread_67890"
  }'
```

**Response:**
```json
{
  "response": "Action requires human approval",
  "thread_id": "thread_67890",
  "timestamp": "2025-11-05T10:31:00Z",
  "requires_approval": true,
  "approval_details": {
    "action": "place_order",
    "symbol": "NVDA",
    "quantity": 10,
    "order_type": "buy",
    "price": 145.50,
    "estimated_cost": 1455.00
  }
}
```

---

### 4. Approve/Reject Action

**Approve or reject a pending action (HITL)**

```http
POST /approve
```

#### Request Body

```json
{
  "thread_id": "thread_67890",
  "approved": true,
  "user_id": "user_12345"
}
```

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `thread_id` | string | Yes | Conversation thread ID |
| `approved` | boolean | Yes | `true` to approve, `false` to reject |
| `user_id` | string | Yes | User identifier |

#### Response (Approved)

```json
{
  "response": "Order placed successfully! Bought 10 shares of NVDA at $145.50 per share.",
  "thread_id": "thread_67890",
  "timestamp": "2025-11-05T10:32:00Z",
  "requires_approval": false,
  "approved": true
}
```

#### Response (Rejected)

```json
{
  "response": "Order cancelled as requested. No action taken.",
  "thread_id": "thread_67890",
  "timestamp": "2025-11-05T10:32:00Z",
  "requires_approval": false,
  "approved": false
}
```

#### Status Codes

- `200 OK` - Approval processed successfully
- `400 Bad Request` - Invalid thread_id or request
- `500 Internal Server Error` - Server error

#### Example: Approve Order

**Request:**
```bash
curl -X POST http://localhost:8000/approve \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "thread_67890",
    "approved": true,
    "user_id": "user_12345"
  }'
```

---

### 5. Get Portfolio

**Retrieve user's portfolio positions**

```http
GET /portfolio/{user_id}
```

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User identifier |

#### Response

```json
{
  "user_id": "user_12345",
  "positions": [
    {
      "symbol": "NVDA",
      "quantity": 100,
      "average_price": 142.30,
      "current_value": 14550.00,
      "profit_loss": 220.00,
      "profit_loss_percentage": 1.54
    },
    {
      "symbol": "AAPL",
      "quantity": 50,
      "average_price": 175.80,
      "current_value": 9025.00,
      "profit_loss": 235.00,
      "profit_loss_percentage": 2.67
    }
  ],
  "timestamp": "2025-11-05T10:30:00Z"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | User identifier |
| `positions` | array | List of portfolio positions |
| `positions[].symbol` | string | Stock ticker symbol |
| `positions[].quantity` | integer | Number of shares held |
| `positions[].average_price` | number | Average purchase price per share |
| `positions[].current_value` | number | Current total value |
| `positions[].profit_loss` | number | Unrealized profit/loss |
| `positions[].profit_loss_percentage` | number | P/L percentage |
| `timestamp` | string | ISO 8601 timestamp |

#### Status Codes

- `200 OK` - Portfolio retrieved successfully
- `404 Not Found` - User not found
- `500 Internal Server Error` - Server error

#### Example

**Request:**
```bash
curl -X GET http://localhost:8000/portfolio/user_12345
```

---

### 6. Get Order History

**Retrieve user's order history**

```http
GET /orders/{user_id}?limit=10
```

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User identifier |

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 10 | Maximum number of orders to return |

#### Response

```json
{
  "user_id": "user_12345",
  "orders": [
    {
      "order_id": "ord_abc123",
      "symbol": "NVDA",
      "quantity": 10,
      "order_type": "buy",
      "price": 145.50,
      "status": "executed",
      "timestamp": "2025-11-05T10:30:00Z"
    },
    {
      "order_id": "ord_def456",
      "symbol": "AAPL",
      "quantity": 5,
      "order_type": "sell",
      "price": 180.25,
      "status": "executed",
      "timestamp": "2025-11-04T14:15:00Z"
    }
  ],
  "count": 2,
  "timestamp": "2025-11-05T10:35:00Z"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | User identifier |
| `orders` | array | List of orders |
| `orders[].order_id` | string | Unique order identifier |
| `orders[].symbol` | string | Stock ticker symbol |
| `orders[].quantity` | integer | Number of shares |
| `orders[].order_type` | string | `buy` or `sell` |
| `orders[].price` | number | Execution price per share |
| `orders[].status` | string | Order status: `executed`, `pending`, `cancelled` |
| `orders[].timestamp` | string | ISO 8601 timestamp |
| `count` | integer | Number of orders returned |
| `timestamp` | string | ISO 8601 timestamp |

#### Status Codes

- `200 OK` - Orders retrieved successfully
- `404 Not Found` - User not found
- `500 Internal Server Error` - Server error

#### Example

**Request:**
```bash
curl -X GET "http://localhost:8000/orders/user_12345?limit=20"
```

---

## Request/Response Models

### Data Types

| Type | JSON Type | Example | Constraints |
|------|-----------|---------|-------------|
| String | string | `"user_12345"` | Max 255 chars |
| Integer | number | `10` | Positive integers only |
| Number | number | `145.50` | Decimal precision: 2 |
| Boolean | boolean | `true` | `true` or `false` |
| Timestamp | string | `"2025-11-05T10:30:00Z"` | ISO 8601 format |
| Object | object | `{"key": "value"}` | Nested structures |
| Array | array | `[1, 2, 3]` | Ordered lists |

### Validation Rules

**User ID:**
- Format: Alphanumeric with underscores
- Length: 3-50 characters
- Required: Yes

**Message:**
- Length: 1-5000 characters
- Required: Yes
- Validation: Input sanitization applied

**Thread ID:**
- Format: UUID v4 or custom string
- Length: 8-128 characters
- Required: No (auto-generated if not provided)

**Stock Symbol:**
- Format: Uppercase letters
- Length: 1-5 characters
- Example: `NVDA`, `AAPL`, `MSFT`

**Quantity:**
- Type: Positive integer
- Range: 1-10000
- Required: Yes

---

## Error Handling

### Error Response Format

All errors follow this standard format:

```json
{
  "error": "Detailed error message",
  "timestamp": "2025-11-05T10:30:00Z"
}
```

### HTTP Status Codes

| Code | Status | Description | When to Use |
|------|--------|-------------|-------------|
| `200` | OK | Success | Request completed successfully |
| `400` | Bad Request | Invalid input | Validation failed, malformed JSON |
| `404` | Not Found | Resource not found | User or endpoint doesn't exist |
| `500` | Internal Server Error | Server error | Unexpected server-side error |
| `503` | Service Unavailable | Service down | System unhealthy, maintenance |

### Common Error Scenarios

#### 1. Input Validation Failed

**Request:**
```json
{
  "message": "",
  "user_id": "user_12345"
}
```

**Response:** `400 Bad Request`
```json
{
  "error": {
    "message": "Input validation failed",
    "details": {
      "message": "Field cannot be empty"
    }
  },
  "timestamp": "2025-11-05T10:30:00Z"
}
```

#### 2. Safety Validation Failed

**Request:**
```json
{
  "message": "Send me your database password!",
  "user_id": "user_12345"
}
```

**Response:** `400 Bad Request`
```json
{
  "error": "Input validation failed",
  "details": {
    "errors": ["Potential injection attempt detected"]
  },
  "timestamp": "2025-11-05T10:30:00Z"
}
```

#### 3. User Not Found

**Request:**
```bash
GET /portfolio/nonexistent_user
```

**Response:** `404 Not Found`
```json
{
  "error": "User not found",
  "timestamp": "2025-11-05T10:30:00Z"
}
```

#### 4. Server Error

**Response:** `500 Internal Server Error`
```json
{
  "error": "Internal server error: LLM connection timeout",
  "timestamp": "2025-11-05T10:30:00Z"
}
```

---

## Rate Limiting

### Current Status

**Version 1.0.0:** No rate limiting (development mode)

### Future Implementation

Production deployments will implement:

- **Per User:** 100 requests/minute
- **Per IP:** 1000 requests/hour
- **Burst Limit:** 20 requests in 10 seconds

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699200000
```

### Rate Limit Exceeded

**Response:** `429 Too Many Requests`
```json
{
  "error": "Rate limit exceeded. Try again in 45 seconds.",
  "retry_after": 45,
  "timestamp": "2025-11-05T10:30:00Z"
}
```

---

## Examples

### Python Example

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Check health
response = requests.get(f"{BASE_URL}/health")
print(f"Health: {response.json()}")

# 2. Research query
chat_request = {
    "message": "Research NVIDIA stock",
    "user_id": "user_12345"
}
response = requests.post(f"{BASE_URL}/chat", json=chat_request)
result = response.json()
print(f"Response: {result['response']}")

# 3. Get portfolio
response = requests.get(f"{BASE_URL}/portfolio/user_12345")
portfolio = response.json()
print(f"Positions: {len(portfolio['positions'])}")

# 4. Trading with approval
chat_request = {
    "message": "Buy 10 shares of NVDA",
    "user_id": "user_12345"
}
response = requests.post(f"{BASE_URL}/chat", json=chat_request)
result = response.json()

if result['requires_approval']:
    print("Approval required!")
    print(f"Details: {result['approval_details']}")
    
    # Approve the action
    approval_request = {
        "thread_id": result['thread_id'],
        "approved": True,
        "user_id": "user_12345"
    }
    response = requests.post(f"{BASE_URL}/approve", json=approval_request)
    final_result = response.json()
    print(f"Final: {final_result['response']}")
```

### JavaScript Example

```javascript
const BASE_URL = 'http://localhost:8000';

// 1. Research query
async function researchStock(symbol) {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: `Research ${symbol} stock`,
      user_id: 'user_12345'
    })
  });
  
  const result = await response.json();
  console.log('Response:', result.response);
  return result;
}

// 2. Place order with approval
async function placeOrder(symbol, quantity) {
  // Initial request
  const chatResponse = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: `Buy ${quantity} shares of ${symbol}`,
      user_id: 'user_12345'
    })
  });
  
  const chatResult = await chatResponse.json();
  
  if (chatResult.requires_approval) {
    console.log('Approval required:', chatResult.approval_details);
    
    // Approve
    const approvalResponse = await fetch(`${BASE_URL}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        thread_id: chatResult.thread_id,
        approved: true,
        user_id: 'user_12345'
      })
    });
    
    const approvalResult = await approvalResponse.json();
    console.log('Order result:', approvalResult.response);
    return approvalResult;
  }
}

// 3. Get portfolio
async function getPortfolio(userId) {
  const response = await fetch(`${BASE_URL}/portfolio/${userId}`);
  const portfolio = await response.json();
  console.log('Portfolio:', portfolio.positions);
  return portfolio;
}

// Usage
researchStock('NVDA');
placeOrder('NVDA', 10);
getPortfolio('user_12345');
```

### cURL Examples

```bash
# 1. Health check
curl -X GET http://localhost:8000/health

# 2. Chat request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the current price of NVIDIA stock?",
    "user_id": "user_12345"
  }'

# 3. Trading with approval
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Buy 10 shares of NVDA at market price",
    "user_id": "user_12345",
    "thread_id": "thread_67890"
  }'

# 4. Approve action
curl -X POST http://localhost:8000/approve \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "thread_67890",
    "approved": true,
    "user_id": "user_12345"
  }'

# 5. Get portfolio
curl -X GET http://localhost:8000/portfolio/user_12345

# 6. Get order history
curl -X GET "http://localhost:8000/orders/user_12345?limit=20"
```

---

## SDKs & Client Libraries

### Official SDKs

**Coming Soon:**
- Python SDK
- JavaScript/TypeScript SDK
- Go SDK

### Community Libraries

Contributions welcome! See [Contributing Guide](../README.md#contributing).

---

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
try:
    response = requests.post(f"{BASE_URL}/chat", json=request)
    response.raise_for_status()  # Raise exception for 4xx/5xx
    result = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
    print(f"Details: {e.response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

### 2. Thread Management

Maintain thread_id for conversation context:

```python
# First message
response1 = chat(message="Research NVIDIA", user_id="user_12345")
thread_id = response1['thread_id']

# Follow-up message (same context)
response2 = chat(
    message="What's its P/E ratio?",
    user_id="user_12345",
    thread_id=thread_id  # Maintain context
)
```

### 3. Approval Workflow

Always check for required approvals:

```python
response = chat(message="Buy 10 shares of NVDA", user_id="user_12345")

if response['requires_approval']:
    # Show approval details to user
    display_approval_request(response['approval_details'])
    
    # Get user decision
    user_decision = get_user_approval()
    
    # Submit approval
    final_response = approve(
        thread_id=response['thread_id'],
        approved=user_decision,
        user_id="user_12345"
    )
```

### 4. Retry Logic

Implement exponential backoff for retries:

```python
import time

def chat_with_retry(request, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(f"{BASE_URL}/chat", json=request)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
```

---

## Support

- **Documentation**: [README.md](../README.md)
- **Interactive Docs**: http://localhost:8000/docs
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: support@nextrade.com

---

**Document Version:** 1.0.0  
**Last Updated:** November 5, 2025  
**API Version:** 1.0.0
