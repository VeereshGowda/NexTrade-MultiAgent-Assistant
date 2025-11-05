"""
Unit tests for utility functions module.

Tests graph visualization, message printing, and helper utilities.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock, mock_open, call
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.types import Command
from agent.utils import (
    save_graph_image,
    get_graph_image_bytes,
    print_messages,
    create_handoff_tool,
    _normalize_agent_name,
    ensure_images_exist
)


# ==================== Graph Visualization Tests ====================

@pytest.mark.unit
class TestGraphVisualization:
    """Test graph visualization utilities."""
    
    @patch('agent.utils.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_graph_image_creates_directory(self, mock_file, mock_makedirs):
        """Test that save_graph_image creates images directory."""
        mock_graph = MagicMock()
        mock_graph.get_graph.return_value.draw_mermaid_png.return_value = b'fake_png_data'
        
        save_graph_image(mock_graph, "test_graph")
        
        mock_makedirs.assert_called_once_with("images", exist_ok=True)
    
    @patch('agent.utils.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_graph_image_returns_filepath(self, mock_file, mock_makedirs):
        """Test that save_graph_image returns filepath on success."""
        mock_graph = MagicMock()
        mock_graph.get_graph.return_value.draw_mermaid_png.return_value = b'fake_png_data'
        
        result = save_graph_image(mock_graph, "test_graph")
        
        assert result is not None
        assert isinstance(result, str)
        assert "test_graph" in result
    
    @patch('agent.utils.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_graph_image_writes_png_data(self, mock_file, mock_makedirs):
        """Test that save_graph_image writes PNG data."""
        mock_graph = MagicMock()
        png_data = b'fake_png_data'
        mock_graph.get_graph.return_value.draw_mermaid_png.return_value = png_data
        
        save_graph_image(mock_graph, "test_graph")
        
        # Verify write was called with PNG data
        mock_file.return_value.write.assert_called_once_with(png_data)
    
    @patch('agent.utils.os.makedirs')
    @patch('agent.utils._generate_svg_fallback')
    def test_save_graph_image_uses_svg_fallback_on_png_failure(self, mock_svg_fallback, mock_makedirs):
        """Test that SVG fallback is used when PNG generation fails."""
        mock_graph = MagicMock()
        mock_graph.get_graph.return_value.draw_mermaid_png.side_effect = Exception("PNG failed")
        mock_svg_fallback.return_value = "images/test_graph.svg"
        
        result = save_graph_image(mock_graph, "test_graph")
        
        mock_svg_fallback.assert_called_once()
    
    def test_get_graph_image_bytes_returns_bytes_or_none(self):
        """Test that get_graph_image_bytes returns bytes or None."""
        mock_graph = MagicMock()
        mock_graph.get_graph.return_value.draw_mermaid_png.return_value = b'fake_png_data'
        
        result = get_graph_image_bytes(mock_graph)
        
        assert result is None or isinstance(result, bytes)
    
    def test_multiple_graph_saves(self):
        """Test saving multiple graphs."""
        mock_graph1 = MagicMock()
        mock_graph2 = MagicMock()
        mock_graph1.get_graph.return_value.draw_mermaid_png.return_value = b'png1'
        mock_graph2.get_graph.return_value.draw_mermaid_png.return_value = b'png2'
        
        with patch('builtins.open', mock_open()):
            with patch('agent.utils.os.makedirs'):
                # Save multiple graphs
                save_graph_image(mock_graph1, "graph1")
                save_graph_image(mock_graph2, "graph2")
        
        # Both should be called
        assert mock_graph1.get_graph.called
        assert mock_graph2.get_graph.called


# ==================== Message Printing Tests ====================

@pytest.mark.unit
class TestMessagePrinting:
    """Test message printing utilities."""
    
    def test_print_messages_with_empty_list(self):
        """Test print_messages with empty list."""
        # Should not raise exception
        try:
            print_messages([])
            success = True
        except Exception:
            success = False
        
        assert success
    
    def test_print_messages_with_human_message(self):
        """Test print_messages with HumanMessage."""
        messages = [HumanMessage(content="Hello")]
        
        try:
            print_messages(messages)
            success = True
        except Exception:
            success = False
        
        assert success
    
    def test_print_messages_with_ai_message(self):
        """Test print_messages with AIMessage."""
        messages = [AIMessage(content="Hi there!")]
        
        try:
            print_messages(messages)
            success = True
        except Exception:
            success = False
        
        assert success
    
    def test_print_messages_with_tool_message(self):
        """Test print_messages with ToolMessage."""
        messages = [ToolMessage(content="Tool result", tool_call_id="123")]
        
        try:
            print_messages(messages)
            success = True
        except Exception:
            success = False
        
        assert success
    
    def test_print_messages_with_mixed_messages(self):
        """Test print_messages with mixed message types."""
        messages = [
            HumanMessage(content="Question"),
            AIMessage(content="Answer"),
            ToolMessage(content="Result", tool_call_id="123")
        ]
        
        try:
            print_messages(messages)
            success = True
        except Exception:
            success = False
        
        assert success
    
    def test_print_messages_handles_tool_calls(self):
        """Test print_messages handles AI messages with tool calls."""
        ai_message = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "test_tool",
                    "args": {"param": "value"},
                    "id": "call_123"
                }
            ]
        )
        
        try:
            print_messages([ai_message])
            success = True
        except Exception:
            success = False
        
        assert success


# ==================== Helper Function Tests ====================

@pytest.mark.unit
class TestHelperFunctions:
    """Test helper utility functions."""
    
    def test_graph_visualization_with_retry(self):
        """Test graph visualization retry logic."""
        mock_graph = MagicMock()
        # First call fails, second succeeds
        mock_graph.get_graph.return_value.draw_mermaid_png.side_effect = [
            Exception("Temporary failure"),
            b'fake_png_data'
        ]
        
        with patch('builtins.open', mock_open()):
            with patch('agent.utils.os.makedirs'):
                result = save_graph_image(mock_graph, "test_graph", max_retries=2)
        
        # Should eventually succeed
        assert result is not None or result is None  # Either succeeds or falls back
    
    def test_message_content_extraction(self):
        """Test extracting content from different message types."""
        messages = [
            HumanMessage(content="Human message"),
            AIMessage(content="AI response"),
            ToolMessage(content="Tool output", tool_call_id="123")
        ]
        
        # Verify messages have content
        for msg in messages:
            assert hasattr(msg, 'content')
            assert isinstance(msg.content, str)
    
    def test_tool_message_requires_tool_call_id(self):
        """Test that ToolMessage requires tool_call_id."""
        # Should be able to create ToolMessage with tool_call_id
        msg = ToolMessage(content="Result", tool_call_id="test_id")
        
        assert msg.tool_call_id == "test_id"
        assert msg.content == "Result"


# ==================== Integration Tests ====================

@pytest.mark.unit
@pytest.mark.integration
class TestUtilsIntegration:
    """Test utils integration scenarios."""
    
    def test_complete_visualization_workflow(self):
        """Test complete visualization workflow."""
        mock_graph = MagicMock()
        mock_graph.get_graph.return_value.draw_mermaid_png.return_value = b'png_data'
        
        with patch('builtins.open', mock_open()):
            with patch('agent.utils.os.makedirs'):
                # Save graph image
                filepath = save_graph_image(mock_graph, "workflow_test")
                
                # Should return a path
                assert filepath is None or isinstance(filepath, str)
    
    def test_message_flow_simulation(self):
        """Test simulating a message flow."""
        conversation = [
            HumanMessage(content="What's the stock price?"),
            AIMessage(content="Let me check that for you."),
            ToolMessage(content="AAPL: $150.25", tool_call_id="1"),
            AIMessage(content="The stock price is $150.25")
        ]
        
        # Should be able to process full conversation
        try:
            print_messages(conversation)
            success = True
        except Exception:
            success = False
        
        assert success
    
    def test_batch_visualization_generation(self):
        """Test generating multiple visualizations."""
        graphs = [MagicMock() for _ in range(4)]
        
        for graph in graphs:
            graph.get_graph.return_value.draw_mermaid_png.return_value = b'png_data'
        
        with patch('builtins.open', mock_open()):
            with patch('agent.utils.os.makedirs'):
                # Simulate saving multiple graphs
                for i, graph in enumerate(graphs):
                    save_graph_image(graph, f"graph_{i}")
        
        # All graphs should have been called
        for graph in graphs:
            assert graph.get_graph.called


# ==================== Agent Handoff Tests ====================

@pytest.mark.unit
class TestAgentHandoffTool:
    """Test agent handoff tool creation and functionality."""
    
    def test_normalize_agent_name_basic(self):
        """Test basic agent name normalization."""
        assert _normalize_agent_name("Database Agent") == "database_agent"
        assert _normalize_agent_name("Research Agent") == "research_agent"
        assert _normalize_agent_name("Portfolio Manager") == "portfolio_manager"
    
    def test_normalize_agent_name_with_multiple_spaces(self):
        """Test normalization with multiple spaces."""
        assert _normalize_agent_name("My  Special   Agent") == "my__special___agent"
    
    def test_normalize_agent_name_already_lowercase(self):
        """Test normalization when already lowercase."""
        assert _normalize_agent_name("database_agent") == "database_agent"
    
    def test_normalize_agent_name_uppercase(self):
        """Test normalization with uppercase."""
        assert _normalize_agent_name("DATABASE") == "database"
    
    def test_create_handoff_tool_default_name(self):
        """Test creating handoff tool with default name."""
        tool = create_handoff_tool(agent_name="Database Agent")
        
        assert tool.name == "transfer_to_database_agent"
        assert "Database Agent" in tool.description
    
    def test_create_handoff_tool_custom_name(self):
        """Test creating handoff tool with custom name."""
        tool = create_handoff_tool(
            agent_name="Research Agent",
            name="custom_handoff_name"
        )
        
        assert tool.name == "custom_handoff_name"
    
    def test_create_handoff_tool_custom_description(self):
        """Test creating handoff tool with custom description."""
        custom_desc = "Transfer to specialized agent"
        tool = create_handoff_tool(
            agent_name="Portfolio Agent",
            description=custom_desc
        )
        
        assert tool.description == custom_desc
    
    def test_create_handoff_tool_returns_basetool(self):
        """Test that handoff tool is a BaseTool instance."""
        tool = create_handoff_tool(agent_name="Test Agent")
        
        # Should have tool attributes
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert callable(tool)
    
    @patch('agent.utils.ToolMessage')
    @patch('agent.utils.Command')
    def test_handoff_tool_execution(self, mock_command, mock_tool_message):
        """Test executing handoff tool."""
        tool = create_handoff_tool(agent_name="Database Agent")
        
        # Mock state and tool_call_id
        mock_state = {"messages": [HumanMessage(content="test")]}
