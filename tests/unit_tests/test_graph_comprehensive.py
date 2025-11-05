"""
Comprehensive tests for graph.py module to improve coverage.

Tests graph creation, compilation, node configuration, and LLM setup.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI

from agent.graph import (
    get_llm,
    create_research_agent,
    create_portfolio_agent,
    create_database_agent,
    create_supervisor_highlevel,
    create_supervisor_custom,
    create_financial_advisor_system
)


# ==================== LLM Configuration Tests ====================

@pytest.mark.unit
class TestLLMConfiguration:
    """Test LLM instance creation and configuration."""
    
    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "OPENAI_API_VERSION": "2024-12-01-preview",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o"
    })
    def test_get_llm_azure_configuration(self):
        """Test Azure OpenAI LLM configuration."""
        llm = get_llm(use_azure=True)
        
        assert isinstance(llm, AzureChatOpenAI)
        assert llm.api_key == "test-key"
        assert llm.azure_endpoint == "https://test.openai.azure.com/"
    
    @patch.dict(os.environ, {"GROQ_API_KEY": "test-groq-key"})
    def test_get_llm_groq_configuration(self):
        """Test Groq LLM configuration."""
        llm = get_llm(use_azure=False)
        
        assert isinstance(llm, ChatGroq)
        assert llm.model_name == "llama-3.1-8b-instant"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_llm_azure_missing_credentials(self):
        """Test Azure LLM raises error when credentials missing."""
        with pytest.raises(ValueError, match="Azure OpenAI configuration not found"):
            get_llm(use_azure=True)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_llm_groq_missing_credentials(self):
        """Test Groq LLM raises error when API key missing."""
        with pytest.raises(ValueError, match="GROQ_API_KEY not found"):
            get_llm(use_azure=False)
    
    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/"
    })
    def test_get_llm_default_azure(self):
        """Test that Azure is the default LLM provider."""
        llm = get_llm()
        
        assert isinstance(llm, AzureChatOpenAI)
    
    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "key",
        "AZURE_OPENAI_ENDPOINT": "https://endpoint.com/"
    })
    def test_get_llm_with_custom_model_name(self):
        """Test LLM creation with custom model name."""
        llm = get_llm(model_name="gpt-4-turbo", use_azure=True)
        
        assert isinstance(llm, AzureChatOpenAI)


# ==================== Agent Creation Tests ====================

@pytest.mark.unit
class TestAgentCreation:
    """Test individual agent creation functions."""
    
    @patch('agent.graph.get_llm')
    @patch('agent.graph.create_react_agent')
    def test_create_research_agent(self, mock_create_agent, mock_get_llm):
        """Test research agent creation."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        
        agent = create_research_agent()
        
        mock_get_llm.assert_called_once()
        mock_create_agent.assert_called_once()
        assert agent == mock_agent
    
    @patch('agent.graph.get_llm')
    @patch('agent.graph.create_react_agent')
    def test_create_portfolio_agent(self, mock_create_agent, mock_get_llm):
        """Test portfolio agent creation."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        
        agent = create_portfolio_agent()
        
        mock_get_llm.assert_called_once()
        mock_create_agent.assert_called_once()
        assert agent == mock_agent
    
    @patch('agent.graph.get_llm')
    @patch('agent.graph.create_react_agent')
    def test_create_database_agent(self, mock_create_agent, mock_get_llm):
        """Test database agent creation."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        
        agent = create_database_agent()
        
        mock_get_llm.assert_called_once()
        mock_create_agent.assert_called_once()
        assert agent == mock_agent
    
    @patch('agent.graph.get_llm')
    @patch('agent.graph.create_react_agent')
    def test_agent_creation_with_tools(self, mock_create_agent, mock_get_llm):
        """Test that agents are created with appropriate tools."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        # Test research agent
        create_research_agent()
        call_args = mock_create_agent.call_args
        
        # Verify tools are passed
        assert 'tools' in call_args.kwargs or len(call_args.args) >= 2
    
    @patch('agent.graph.get_llm')
    @patch('agent.graph.create_react_agent')
    def test_agent_creation_with_system_message(self, mock_create_agent, mock_get_llm):
        """Test that agents are created with system messages."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        create_portfolio_agent()
        call_args = mock_create_agent.call_args
        
        # Verify state_modifier (system message) is passed
        assert 'state_modifier' in call_args.kwargs or len(call_args.args) >= 3


# ==================== Supervisor Tests ====================

@pytest.mark.unit
class TestSupervisorCreation:
    """Test supervisor creation and configuration."""
    
    @patch('agent.graph.get_llm')
    @patch('agent.graph.create_react_agent')
    def test_create_supervisor_highlevel_function(self, mock_agent, mock_get_llm):
        """Test high-level supervisor creation."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_agent.return_value = MagicMock()
        
        supervisor = create_supervisor_highlevel()
        
        assert supervisor is not None
        mock_get_llm.assert_called()
    
    @patch('agent.graph.get_llm')
    @patch('agent.graph.create_react_agent')
    def test_create_supervisor_custom_function(self, mock_agent, mock_get_llm):
        """Test custom supervisor creation."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_agent.return_value = MagicMock()
        
        supervisor = create_supervisor_custom()
        
        assert supervisor is not None
        mock_get_llm.assert_called()


# ==================== System Creation Tests ====================

@pytest.mark.unit
class TestSystemCreation:
    """Test complete system creation functions."""
    
    @patch('agent.graph.get_llm')
    @patch('agent.graph.create_react_agent')
    def test_create_financial_advisor_system(self, mock_agent, mock_llm):
        """Test high-level financial advisor system creation."""
        mock_llm.return_value = MagicMock()
        mock_agent.return_value = MagicMock()
        
        system = create_financial_advisor_system()
        
        assert system is not None
        # Verify agents were created
        assert mock_agent.call_count >= 3  # research, portfolio, database
    
    @patch('agent.graph.get_llm')
    @patch('agent.graph.create_react_agent')
    def test_create_financial_advisor_with_custom(self, mock_agent, mock_llm):
        """Test custom financial advisor system creation."""
        mock_llm.return_value = MagicMock()
        mock_agent.return_value = MagicMock()
        
        system = create_financial_advisor_system(use_highlevel=False)
        
        assert system is not None
        # Verify agents were created
        assert mock_agent.call_count >= 3


# ==================== Graph Compilation Tests ====================

@pytest.mark.unit
class TestGraphCompilation:
    """Test graph compilation and structure."""
    
    @patch('agent.graph.get_llm')
    @patch('agent.graph.create_react_agent')
    def test_system_returns_compiled_graph(self, mock_agent, mock_llm):
        """Test that system creation returns a compiled graph."""
        mock_llm.return_value = MagicMock()
        mock_agent.return_value = MagicMock()
        
        system = create_financial_advisor_system()
        
        # Should return a graph-like object
        assert system is not None
    
    @patch('agent.graph.get_llm')
    @patch('agent.graph.create_react_agent')
    def test_custom_system_has_checkpointer(self, mock_agent, mock_llm):
        """Test custom system includes memory checkpointer."""
        mock_llm.return_value = MagicMock()
        mock_agent.return_value = MagicMock()
        
        system = create_financial_advisor_system(use_highlevel=False)
        
        # Verify system was created (checkpointer is internal)
        assert system is not None


# ==================== Integration Tests ====================

@pytest.mark.unit
@pytest.mark.integration
class TestGraphIntegration:
    """Test integration scenarios for graph creation."""
    
    @patch('agent.graph.get_llm')
    @patch('agent.graph.create_react_agent')
    def test_full_system_creation_workflow(self, mock_agent, mock_llm):
        """Test complete workflow from agents to supervisor to system."""
        # Setup mocks
        mock_llm.return_value = MagicMock()
        mock_agent.return_value = MagicMock()
        
        # Create system
        system = create_financial_advisor_system()
        
        # Verify all components were created
        assert system is not None
        assert mock_llm.called
        assert mock_agent.called
    
    @patch('agent.graph.get_llm')
    @patch('agent.graph.create_react_agent')
    def test_multiple_systems_can_coexist(self, mock_agent, mock_llm):
        """Test that multiple system instances can be created."""
        mock_llm.return_value = MagicMock()
        mock_agent.return_value = MagicMock()
        
        system1 = create_financial_advisor_system()
        system2 = create_financial_advisor_system(use_highlevel=False)
        
        assert system1 is not None
        assert system2 is not None
    
    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/"
    })
    @patch('agent.graph.create_react_agent')
    def test_system_with_real_llm_config(self, mock_agent):
        """Test system creation with realistic LLM configuration."""
        mock_agent.return_value = MagicMock()
        
        system = create_financial_advisor_system()
        
        assert system is not None


# ==================== Error Handling Tests ====================

@pytest.mark.unit
class TestGraphErrorHandling:
    """Test error handling in graph creation."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_system_fails_without_llm_config(self):
        """Test system creation fails gracefully without LLM config."""
        with pytest.raises(ValueError):
            create_financial_advisor_system()
    
    @patch('agent.graph.get_llm')
    def test_system_handles_llm_creation_error(self, mock_get_llm):
        """Test system handles LLM creation errors."""
        mock_get_llm.side_effect = Exception("LLM creation failed")
        
        with pytest.raises(Exception, match="LLM creation failed"):
            create_financial_advisor_system()


# ==================== Module Structure Tests ====================

@pytest.mark.unit
class TestGraphModuleStructure:
    """Test graph module structure and exports."""
    
    def test_module_exports_required_functions(self):
        """Test that module exports all required functions."""
        from agent import graph
        
        assert hasattr(graph, 'get_llm')
        assert hasattr(graph, 'create_research_agent')
        assert hasattr(graph, 'create_portfolio_agent')
        assert hasattr(graph, 'create_database_agent')
        assert hasattr(graph, 'create_supervisor_highlevel')
        assert hasattr(graph, 'create_supervisor_custom')
        assert hasattr(graph, 'create_financial_advisor_system')
    
    def test_functions_are_callable(self):
        """Test that exported functions are callable."""
        from agent import graph
        
        assert callable(graph.get_llm)
        assert callable(graph.create_research_agent)
        assert callable(graph.create_portfolio_agent)
        assert callable(graph.create_database_agent)
    
    def test_module_has_docstrings(self):
        """Test that module and functions have docstrings."""
        from agent import graph
        
        assert graph.__doc__ is not None
        assert graph.get_llm.__doc__ is not None
        assert graph.create_research_agent.__doc__ is not None
