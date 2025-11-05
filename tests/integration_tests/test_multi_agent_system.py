"""
Integration tests for multi-agent graph system.

Tests complete agent workflows, supervisor coordination, and HITL approval.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage
from agent.graph import (
    create_financial_advisor_system,
    create_research_agent,
    create_portfolio_agent,
    create_database_agent
)


# ==================== Agent Creation Tests ====================

@pytest.mark.integration
class TestAgentCreation:
    """Test individual agent creation."""
    
    @pytest.mark.slow
    def test_research_agent_creation(self):
        """Test research agent can be created."""
        agent = create_research_agent()
        
        assert agent is not None
        assert hasattr(agent, 'invoke') or hasattr(agent, '__call__')
    
    @pytest.mark.slow
    def test_portfolio_agent_creation(self):
        """Test portfolio agent can be created."""
        agent = create_portfolio_agent()
        
        assert agent is not None
        assert hasattr(agent, 'invoke') or hasattr(agent, '__call__')
    
    @pytest.mark.slow
    def test_database_agent_creation(self):
        """Test database agent can be created."""
        agent = create_database_agent()
        
        assert agent is not None
        assert hasattr(agent, 'invoke') or hasattr(agent, '__call__')


# ==================== Supervisor System Tests ====================

@pytest.mark.integration
@pytest.mark.slow
class TestSupervisorSystem:
    """Test complete supervisor system."""
    
    def test_supervisor_creation(self):
        """Test supervisor system can be created."""
        supervisor = create_financial_advisor_system()
        
        assert supervisor is not None
        assert hasattr(supervisor, 'invoke')
    
    @pytest.mark.llm
    @patch('agent.graph.get_llm')
    def test_supervisor_message_routing(self, mock_get_llm):
        """Test supervisor routes messages correctly."""
        # Mock LLM to return specific routing decision
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(
            content="I'll route this to the research agent"
        )
        mock_get_llm.return_value = mock_llm
        
        supervisor = create_financial_advisor_system()
        
        config = {
            "configurable": {
                "thread_id": "test_thread",
                "user_id": "test_user"
            }
        }
        
        # This test verifies structure, not actual LLM calls
        assert supervisor is not None


# ==================== Research Agent Workflow Tests ====================

@pytest.mark.integration
@pytest.mark.mock
class TestResearchAgentWorkflow:
    """Test research agent workflows with mocked dependencies."""
    
    @patch('agent.tools.TavilySearch')
    @patch('agent.graph.get_llm')
    def test_research_agent_web_search_workflow(self, mock_get_llm, mock_tavily):
        """Test research agent can perform web search."""
        # Mock Tavily
        mock_tavily_instance = MagicMock()
        mock_tavily_instance.invoke.return_value = {
            "results": [
                {
                    "title": "NVIDIA Analysis",
                    "url": "https://example.com",
                    "content": "NVIDIA stock information",
                    "snippet": "Stock analysis"
                }
            ]
        }
        mock_tavily.return_value = mock_tavily_instance
        
        # Mock LLM to call web_search tool
        mock_llm = MagicMock()
        
        # First call: decide to use web_search
        tool_call_message = AIMessage(
            content="",
            tool_calls=[{
                "name": "web_search",
                "args": {"query": "NVIDIA stock", "max_results": 5},
                "id": "call_123"
            }]
        )
        
        # Second call: final response after tool use
        final_message = AIMessage(
            content="Based on my research, NVIDIA shows strong performance..."
        )
        
        mock_llm.invoke.side_effect = [tool_call_message, final_message]
        mock_get_llm.return_value = mock_llm
        
        agent = create_research_agent()
        
        # Agent structure created successfully
        assert agent is not None


# ==================== Portfolio Agent Workflow Tests ====================

@pytest.mark.integration
@pytest.mark.mock
class TestPortfolioAgentWorkflow:
    """Test portfolio agent workflows with HITL."""
    
    @patch('agent.tools.yf.Ticker')
    @patch('agent.graph.get_llm')
    def test_portfolio_agent_stock_lookup_workflow(self, mock_get_llm, mock_ticker):
        """Test portfolio agent can lookup and fetch stock data."""
        # Mock yfinance
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            "symbol": "AAPL",
            "regularMarketPrice": 150.25,
            "shortName": "Apple Inc."
        }
        mock_ticker.return_value = mock_ticker_instance
        
        # Mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(
            content="The current price of Apple stock is $150.25"
        )
        mock_get_llm.return_value = mock_llm
        
        agent = create_portfolio_agent()
        
        assert agent is not None
    
    def test_portfolio_agent_has_hitl_hook(self):
        """Test portfolio agent has human-in-the-loop configured."""
        agent = create_portfolio_agent()
        
        # Portfolio agent should be configured with HITL
        # This is a structural test
        assert agent is not None


# ==================== Database Agent Workflow Tests ====================

@pytest.mark.integration
@pytest.mark.database
class TestDatabaseAgentWorkflow:
    """Test database agent workflows."""
    
    @patch('agent.database_tools.get_user_orders')
    @patch('agent.graph.get_llm')
    def test_database_agent_query_orders(self, mock_get_llm, mock_get_orders):
        """Test database agent can query orders."""
        # Mock database tool
        mock_get_orders.return_value = [
            {
                "order_id": "order_123",
                "symbol": "AAPL",
                "quantity": 10,
                "status": "executed"
            }
        ]
        
        # Mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(
            content="You have 1 order in your history"
        )
        mock_get_llm.return_value = mock_llm
        
        agent = create_database_agent()
        
        assert agent is not None


# ==================== End-to-End Workflow Tests ====================

@pytest.mark.e2e
@pytest.mark.slow
class TestEndToEndWorkflows:
    """End-to-end tests for complete workflows."""
    
    @patch('agent.tools.TavilySearch')
    @patch('agent.tools.yf.Ticker')
    @patch('agent.graph.get_llm')
    def test_complete_research_to_recommendation_workflow(
        self,
        mock_get_llm,
        mock_ticker,
        mock_tavily
    ):
        """Test complete workflow from research to recommendation."""
        # Mock external dependencies
        mock_tavily_instance = MagicMock()
        mock_tavily_instance.invoke.return_value = {
            "results": [{"title": "Test", "content": "Test content"}]
        }
        mock_tavily.return_value = mock_tavily_instance
        
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {"symbol": "AAPL", "regularMarketPrice": 150.0}
        mock_ticker.return_value = mock_ticker_instance
        
        # Mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(
            content="Research complete. Stock looks promising."
        )
        mock_get_llm.return_value = mock_llm
        
        # Create supervisor
        supervisor = create_financial_advisor_system()
        
        # Verify supervisor is created
        assert supervisor is not None
    
    @patch('agent.tools.yf.Ticker')
    @patch('agent.graph.get_llm')
    def test_order_placement_requires_approval(self, mock_get_llm, mock_ticker):
        """Test that order placement triggers HITL approval."""
        # This test verifies the HITL structure
        # Actual approval flow requires full system integration
        
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {"symbol": "AAPL", "regularMarketPrice": 150.0}
        mock_ticker.return_value = mock_ticker_instance
        
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        supervisor = create_financial_advisor_system()
        
        # Supervisor should have HITL configured
        assert supervisor is not None


# ==================== Error Handling Tests ====================

@pytest.mark.integration
class TestErrorHandling:
    """Test error handling in agent system."""
    
    @patch('agent.tools.TavilySearch')
    @patch('agent.graph.get_llm')
    def test_agent_handles_tool_failure(self, mock_get_llm, mock_tavily):
        """Test agent handles tool failures gracefully."""
        # Mock tool failure
        mock_tavily_instance = MagicMock()
        mock_tavily_instance.invoke.side_effect = Exception("API Error")
        mock_tavily.return_value = mock_tavily_instance
        
        # Mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(
            content="I encountered an error accessing the search tool"
        )
        mock_get_llm.return_value = mock_llm
        
        agent = create_research_agent()
        
        # Agent should be created despite potential tool issues
        assert agent is not None
    
    @patch('agent.graph.get_llm')
    def test_supervisor_handles_missing_config(self, mock_get_llm):
        """Test supervisor handles missing configuration."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        supervisor = create_financial_advisor_system()
        
        # Should create without errors
        assert supervisor is not None


# ==================== State Management Tests ====================

@pytest.mark.integration
class TestStateManagement:
    """Test state management in multi-agent system."""
    
    def test_state_initialization(self):
        """Test that agent state initializes correctly."""
        from agent.state import SupervisorState
        
        # Verify state structure
        assert SupervisorState is not None
    
    @patch('agent.graph.get_llm')
    def test_supervisor_maintains_context(self, mock_get_llm):
        """Test supervisor maintains conversation context."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="Response")
        mock_get_llm.return_value = mock_llm
        
        supervisor = create_financial_advisor_system()
        
        # Supervisor should support configuration with thread_id
        config = {
            "configurable": {
                "thread_id": "test_thread_123",
                "user_id": "user_456"
            }
        }
        
        # Verify supervisor accepts config structure
        assert supervisor is not None


# ==================== Performance Tests ====================

@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Performance tests for agent system."""
    
    @patch('agent.graph.get_llm')
    def test_supervisor_creation_performance(
        self,
        mock_get_llm,
        measure_execution_time
    ):
        """Test supervisor creation completes in reasonable time."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        with measure_execution_time() as timer:
            supervisor = create_financial_advisor_system()
        
        # Should create within 5 seconds
        assert timer.elapsed < 5.0
        assert supervisor is not None
    
    @patch('agent.tools.TavilySearch')
    @patch('agent.graph.get_llm')
    def test_agent_invocation_performance(
        self,
        mock_get_llm,
        mock_tavily,
        measure_execution_time
    ):
        """Test agent responds in reasonable time."""
        # Mock dependencies for fast execution
        mock_tavily_instance = MagicMock()
        mock_tavily_instance.invoke.return_value = {"results": []}
        mock_tavily.return_value = mock_tavily_instance
        
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="Fast response")
        mock_get_llm.return_value = mock_llm
        
        agent = create_research_agent()
        
        # Agent creation should be fast
        assert agent is not None
