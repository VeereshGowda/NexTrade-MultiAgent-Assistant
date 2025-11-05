"""
Pytest configuration and shared fixtures for NexTrade testing suite.
"""

import pytest
import os
import sys
from typing import Dict, Any
from unittest.mock import Mock, MagicMock
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.store.memory import InMemoryStore


# ==================== Environment Setup ====================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ["TESTING"] = "true"
    # Ensure we have test API keys (can be dummy for mocked tests)
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        os.environ["AZURE_OPENAI_API_KEY"] = "test-key-12345"
    if not os.getenv("AZURE_OPENAI_ENDPOINT"):
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com"
    if not os.getenv("TAVILY_API_KEY"):
        os.environ["TAVILY_API_KEY"] = "test-tavily-key"
    yield
    # Cleanup
    os.environ.pop("TESTING", None)


# ==================== Mock LLM Fixtures ====================

@pytest.fixture
def mock_llm():
    """Provide a mocked LLM that returns deterministic responses."""
    mock = MagicMock()
    mock.invoke.return_value = AIMessage(
        content="This is a mocked response from the LLM."
    )
    return mock


@pytest.fixture
def mock_llm_with_tool_call():
    """Provide a mocked LLM that returns a tool call."""
    mock = MagicMock()
    tool_call = {
        "name": "web_search",
        "args": {"query": "test query", "max_results": 5},
        "id": "call_123"
    }
    mock.invoke.return_value = AIMessage(
        content="",
        tool_calls=[tool_call]
    )
    return mock


@pytest.fixture
def mock_structured_output():
    """Provide a mocked structured output response."""
    return {
        "status": "success",
        "data": {"symbol": "AAPL", "price": 150.25},
        "timestamp": datetime.now().isoformat()
    }


# ==================== Test Data Fixtures ====================

@pytest.fixture
def sample_user_message():
    """Sample user message for testing."""
    return HumanMessage(content="Research NVIDIA stock and provide analysis")


@pytest.fixture
def sample_thread_id():
    """Sample thread ID for testing."""
    return "test-thread-12345"


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return "test-user-67890"


@pytest.fixture
def sample_config(sample_thread_id, sample_user_id):
    """Sample configuration for agent testing."""
    return {
        "configurable": {
            "thread_id": sample_thread_id,
            "user_id": sample_user_id
        }
    }


@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing."""
    return {
        "symbol": "AAPL",
        "current_price": 150.25,
        "change": 2.50,
        "change_percent": 1.69,
        "volume": 50000000,
        "market_cap": 2500000000000
    }


@pytest.fixture
def sample_order_data():
    """Sample order data for testing."""
    return {
        "user_id": "test-user-67890",
        "symbol": "AAPL",
        "quantity": 10,
        "order_type": "buy",
        "price": 150.25,
        "status": "pending"
    }


# ==================== Database Fixtures ====================

@pytest.fixture
def in_memory_store():
    """Provide an in-memory store for testing."""
    return InMemoryStore()


@pytest.fixture
def test_database_path(tmp_path):
    """Provide a temporary database path for testing."""
    db_path = tmp_path / "test_trading_orders.db"
    return str(db_path)


# ==================== Mock Tool Fixtures ====================

@pytest.fixture
def mock_web_search_results():
    """Mock web search results."""
    return {
        "results": [
            {
                "title": "NVIDIA Stock Analysis",
                "url": "https://example.com/nvidia-analysis",
                "snippet": "NVIDIA shows strong growth in AI chip market..."
            },
            {
                "title": "Tech Stock Insights",
                "url": "https://example.com/tech-insights",
                "snippet": "Analysis of major tech stocks including NVIDIA..."
            }
        ]
    }


@pytest.fixture
def mock_stock_lookup_result():
    """Mock stock symbol lookup result."""
    return {
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "exchange": "NASDAQ"
    }


# ==================== Agent Fixtures ====================

@pytest.fixture
def mock_research_agent():
    """Provide a mocked research agent."""
    agent = MagicMock()
    agent.invoke.return_value = {
        "messages": [
            AIMessage(content="Research completed: NVIDIA is a leading AI chip manufacturer...")
        ]
    }
    return agent


@pytest.fixture
def mock_portfolio_agent():
    """Provide a mocked portfolio agent."""
    agent = MagicMock()
    agent.invoke.return_value = {
        "messages": [
            AIMessage(content="Order placed successfully for 10 shares of AAPL at $150.25")
        ]
    }
    return agent


@pytest.fixture
def mock_database_agent():
    """Provide a mocked database agent."""
    agent = MagicMock()
    agent.invoke.return_value = {
        "messages": [
            AIMessage(content="Retrieved 5 orders from the database")
        ]
    }
    return agent


# ==================== Pytest Markers ====================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )


# ==================== Test Helpers ====================

@pytest.fixture
def assert_message_contains():
    """Helper to assert message content."""
    def _assert(messages, expected_text):
        """Check if any message contains the expected text."""
        message_texts = [
            msg.content for msg in messages 
            if hasattr(msg, 'content')
        ]
        assert any(
            expected_text.lower() in text.lower() 
            for text in message_texts
        ), f"Expected '{expected_text}' not found in messages: {message_texts}"
    return _assert


@pytest.fixture
def measure_execution_time():
    """Measure execution time of a code block."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.elapsed = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, *args):
            self.end_time = time.time()
            self.elapsed = self.end_time - self.start_time
    
    return Timer
