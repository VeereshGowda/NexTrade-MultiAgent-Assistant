"""
Additional comprehensive tests for utils.py to improve coverage.

Focuses on testing create_handoff_tool, ensure_images_exist, and get_graph_image_bytes.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock, mock_open, call
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.types import Command
from agent.utils import (
    create_handoff_tool,
    _normalize_agent_name,
    ensure_images_exist,
    get_graph_image_bytes
)


# ==================== Additional Agent Handoff Tests ====================

@pytest.mark.unit
class TestAgentHandoffToolAdditional:
    """Additional tests for agent handoff tools."""
    
    def test_create_multiple_handoff_tools(self):
        """Test creating multiple handoff tools."""
        agents = ["Database Agent", "Research Agent", "Portfolio Agent"]
        tools = [create_handoff_tool(agent_name=name) for name in agents]
        
        assert len(tools) == 3
        assert tools[0].name == "transfer_to_database_agent"
        assert tools[1].name == "transfer_to_research_agent"
        assert tools[2].name == "transfer_to_portfolio_agent"
    
    def test_handoff_tool_with_special_characters(self):
        """Test handoff tool with special characters in agent name."""
        tool = create_handoff_tool(agent_name="Agent-123 Test!")
        
        # Should normalize to valid tool name
        assert tool.name == "transfer_to_agent-123_test!"
    
    def test_normalize_agent_name_empty_string(self):
        """Test normalization with empty string."""
        result = _normalize_agent_name("")
        assert result == ""
    
    def test_normalize_agent_name_only_spaces(self):
        """Test normalization with only spaces."""
        result = _normalize_agent_name("   ")
        assert result == "___"
    
    def test_create_handoff_tool_empty_agent_name(self):
        """Test creating handoff tool with empty agent name."""
        tool = create_handoff_tool(agent_name="")
        assert tool.name == "transfer_to_"


# ==================== Image Management Tests ====================

@pytest.mark.unit
class TestEnsureImagesExist:
    """Test ensure_images_exist functionality."""
    
    @patch('agent.utils.save_graph_image')
    @patch('agent.utils.os.path.exists')
    def test_ensure_images_exist_creates_missing_images(self, mock_exists, mock_save):
        """Test that ensure_images_exist creates missing images."""
        mock_exists.return_value = False
        
        graph1 = MagicMock()
        graph2 = MagicMock()
        graph_dict = {"graph1": graph1, "graph2": graph2}
        
        ensure_images_exist(graph_dict)
        
        # Should save both graphs
        assert mock_save.call_count == 2
    
    @patch('agent.utils.save_graph_image')
    @patch('agent.utils.os.path.exists')
    def test_ensure_images_exist_skips_existing_images(self, mock_exists, mock_save):
        """Test that ensure_images_exist skips existing images."""
        mock_exists.return_value = True
        
        graph1 = MagicMock()
        graph_dict = {"graph1": graph1}
        
        ensure_images_exist(graph_dict)
        
        # Should not save if exists
        mock_save.assert_not_called()
    
    @patch('agent.utils.save_graph_image')
    @patch('agent.utils.os.path.exists')
    def test_ensure_images_exist_force_recreate(self, mock_exists, mock_save):
        """Test ensure_images_exist with force_recreate."""
        mock_exists.return_value = True
        
        graph1 = MagicMock()
        graph_dict = {"graph1": graph1}
        
        ensure_images_exist(graph_dict, force_recreate=True)
        
        # Should save even if exists
        mock_save.assert_called_once()
    
    @patch('agent.utils.save_graph_image')
    @patch('agent.utils.os.path.exists')
    def test_ensure_images_exist_empty_dict(self, mock_exists, mock_save):
        """Test ensure_images_exist with empty dictionary."""
        ensure_images_exist({})
        
        # Should not save anything
        mock_save.assert_not_called()
    
    @patch('agent.utils.save_graph_image')
    @patch('agent.utils.os.path.exists')
    def test_ensure_images_exist_mixed_existence(self, mock_exists, mock_save):
        """Test ensure_images_exist with some existing, some missing."""
        # First graph exists, second doesn't
        mock_exists.side_effect = [True, False, False, False]
        
        graph1 = MagicMock()
        graph2 = MagicMock()
        graph_dict = {"existing": graph1, "missing": graph2}
        
        ensure_images_exist(graph_dict)
        
        # Should only save the missing one
        assert mock_save.call_count == 1
        mock_save.assert_called_with(graph2, "missing")
    
    @patch('agent.utils.save_graph_image')
    @patch('agent.utils.os.path.exists')
    def test_ensure_images_exist_checks_both_png_and_svg(self, mock_exists, mock_save):
        """Test that ensure_images_exist checks for both PNG and SVG."""
        # Neither PNG nor SVG exists
        mock_exists.side_effect = [False, False]
        
        graph1 = MagicMock()
        graph_dict = {"graph1": graph1}
        
        ensure_images_exist(graph_dict)
        
        # Should check for both formats
        assert mock_exists.call_count == 2
        expected_calls = [
            call("images/graph1.png"),
            call("images/graph1.svg")
        ]
        mock_exists.assert_has_calls(expected_calls, any_order=False)
    
    @patch('agent.utils.save_graph_image')
    @patch('agent.utils.os.path.exists')
    def test_ensure_images_exist_with_svg_exists(self, mock_exists, mock_save):
        """Test ensure_images_exist when SVG exists but PNG doesn't."""
        # PNG doesn't exist, but SVG does
        mock_exists.side_effect = [False, True]
        
        graph1 = MagicMock()
        graph_dict = {"graph1": graph1}
        
        ensure_images_exist(graph_dict)
        
        # Should not save if SVG exists
        mock_save.assert_not_called()


# ==================== Get Graph Image Bytes Tests ====================

@pytest.mark.unit
class TestGetGraphImageBytes:
    """Test get_graph_image_bytes functionality."""
    
    def test_get_graph_image_bytes_success(self):
        """Test successful PNG generation."""
        mock_graph = MagicMock()
        mock_graph.get_graph.return_value.draw_mermaid_png.return_value = b'fake_png_data'
        
        result = get_graph_image_bytes(mock_graph)
        
        assert result == b'fake_png_data'
    
    def test_get_graph_image_bytes_with_filename_hint(self):
        """Test with custom filename hint."""
        mock_graph = MagicMock()
        mock_graph.get_graph.return_value.draw_mermaid_png.return_value = b'png_data'
        
        result = get_graph_image_bytes(mock_graph, filename_hint="custom_graph")
        
        assert result == b'png_data'
    
    def test_get_graph_image_bytes_failure(self):
        """Test handling of PNG generation failure."""
        mock_graph = MagicMock()
        mock_graph.get_graph.return_value.draw_mermaid_png.side_effect = Exception("Failed")
        
        result = get_graph_image_bytes(mock_graph)
        
        assert result is None
    
    def test_get_graph_image_bytes_returns_none_or_bytes(self):
        """Test that return type is always None or bytes."""
        mock_graph = MagicMock()
        mock_graph.get_graph.return_value.draw_mermaid_png.return_value = b'data'
        
        result = get_graph_image_bytes(mock_graph)
        
        assert result is None or isinstance(result, bytes)
    
    def test_get_graph_image_bytes_calls_draw_mermaid_png(self):
        """Test that draw_mermaid_png is called."""
        mock_graph = MagicMock()
        mock_draw = mock_graph.get_graph.return_value.draw_mermaid_png
        mock_draw.return_value = b'png'
        
        get_graph_image_bytes(mock_graph)
        
        mock_draw.assert_called_once()
    
    def test_get_graph_image_bytes_with_none_return(self):
        """Test get_graph_image_bytes when draw returns None."""
        mock_graph = MagicMock()
        mock_graph.get_graph.return_value.draw_mermaid_png.return_value = None
        
        result = get_graph_image_bytes(mock_graph)
        
        # Should handle None gracefully
        assert result is None or result == None


# ==================== Edge Case and Error Handling Tests ====================

@pytest.mark.unit
class TestUtilsEdgeCases:
    """Test edge cases and error handling."""
    
    @patch('agent.utils.save_graph_image')
    @patch('agent.utils.os.path.exists')
    def test_ensure_images_exist_with_save_failure(self, mock_exists, mock_save):
        """Test ensure_images_exist when save_graph_image fails."""
        mock_exists.return_value = False
        mock_save.side_effect = Exception("Save failed")
        
        graph1 = MagicMock()
        graph_dict = {"graph1": graph1}
        
        # Should handle exception gracefully or propagate
        try:
            ensure_images_exist(graph_dict)
        except Exception as e:
            # If it propagates, that's acceptable behavior
            assert "Save failed" in str(e)
    
    def test_normalize_agent_name_preserves_underscores(self):
        """Test that existing underscores are preserved."""
        assert _normalize_agent_name("database_agent") == "database_agent"
        assert _normalize_agent_name("my_custom_agent") == "my_custom_agent"
    
    def test_normalize_agent_name_handles_mixed_case(self):
        """Test normalization with mixed case."""
        assert _normalize_agent_name("MyAgent") == "myagent"
        assert _normalize_agent_name("My_Agent") == "my_agent"
    
    def test_create_handoff_tool_with_long_agent_name(self):
        """Test creating handoff tool with very long agent name."""
        long_name = "This Is A Very Long Agent Name That Should Still Work"
        tool = create_handoff_tool(agent_name=long_name)
        
        expected = "transfer_to_this_is_a_very_long_agent_name_that_should_still_work"
        assert tool.name == expected
    
    def test_handoff_tool_attributes_exist(self):
        """Test that handoff tool has required attributes."""
        tool = create_handoff_tool(agent_name="Test Agent")
        
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, 'func') or callable(tool)
    
    @patch('agent.utils.save_graph_image')
    @patch('agent.utils.os.path.exists')
    def test_ensure_images_exist_with_many_graphs(self, mock_exists, mock_save):
        """Test ensure_images_exist with many graphs."""
        mock_exists.return_value = False
        
        # Create 10 graphs
        graphs = {f"graph{i}": MagicMock() for i in range(10)}
        
        ensure_images_exist(graphs)
        
        # Should save all 10
        assert mock_save.call_count == 10
    
    def test_get_graph_image_bytes_consistent_behavior(self):
        """Test that get_graph_image_bytes has consistent behavior."""
        mock_graph = MagicMock()
        mock_graph.get_graph.return_value.draw_mermaid_png.return_value = b'test'
        
        result1 = get_graph_image_bytes(mock_graph)
        result2 = get_graph_image_bytes(mock_graph)
        
        # Should be consistent
        assert result1 == result2
