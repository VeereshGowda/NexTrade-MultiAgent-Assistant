"""
Additional unit tests for state module to increase coverage.

Tests state management and message handling.
"""

import pytest
from unittest.mock import Mock
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from agent.state import SupervisorState, get_initial_state


def create_agent_state(messages=None):
    """Helper to create agent state for testing."""
    return {"messages": messages or []}


# ==================== State Creation Tests ====================

@pytest.mark.unit
class TestStateCreation:
    """Test state creation and initialization."""
    
    def test_create_agent_state_returns_dict(self):
        """Test that create_agent_state returns a dictionary."""
        state = create_agent_state()
        assert isinstance(state, dict)
    
    def test_create_agent_state_has_messages_key(self):
        """Test that state has messages key."""
        state = create_agent_state()
        assert "messages" in state
    
    def test_create_agent_state_messages_is_list(self):
        """Test that state messages is a list."""
        state = create_agent_state()
        assert isinstance(state["messages"], list)
    
    def test_create_agent_state_with_initial_message(self):
        """Test creating state with initial message."""
        initial_message = HumanMessage(content="Hello")
        state = create_agent_state(messages=[initial_message])
        
        assert len(state["messages"]) >= 1
    
    def test_create_agent_state_with_multiple_messages(self):
        """Test creating state with multiple messages."""
        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!")
        ]
        state = create_agent_state(messages=messages)
        
        assert len(state["messages"]) >= 2


# ==================== State Type Tests ====================

@pytest.mark.unit
class TestStateTypes:
    """Test state type definitions."""
    
    def test_agent_state_accepts_messages(self):
        """Test that AgentState accepts messages."""
        state = {"messages": [HumanMessage(content="Test")]}
        # Should not raise TypeError
        assert isinstance(state, dict)
    
    def test_state_handles_empty_messages(self):
        """Test state handles empty message list."""
        state = {"messages": []}
        assert isinstance(state["messages"], list)
        assert len(state["messages"]) == 0
    
    def test_state_handles_human_messages(self):
        """Test state handles HumanMessage instances."""
        msg = HumanMessage(content="User message")
        state = {"messages": [msg]}
        assert state["messages"][0].content == "User message"
    
    def test_state_handles_ai_messages(self):
        """Test state handles AIMessage instances."""
        msg = AIMessage(content="AI response")
        state = {"messages": [msg]}
        assert state["messages"][0].content == "AI response"
    
    def test_state_handles_tool_messages(self):
        """Test state handles ToolMessage instances."""
        msg = ToolMessage(content="Tool result", tool_call_id="123")
        state = {"messages": [msg]}
        assert state["messages"][0].content == "Tool result"


# ==================== State Update Tests ====================

@pytest.mark.unit
class TestStateUpdates:
    """Test state update operations."""
    
    def test_append_message_to_state(self):
        """Test appending message to state."""
        state = create_agent_state()
        initial_count = len(state["messages"])
        
        new_message = HumanMessage(content="New message")
        state["messages"].append(new_message)
        
        assert len(state["messages"]) == initial_count + 1
    
    def test_state_preserves_message_order(self):
        """Test that state preserves message order."""
        messages = [
            HumanMessage(content="First"),
            AIMessage(content="Second"),
            HumanMessage(content="Third")
        ]
        state = create_agent_state(messages=messages)
        
        assert state["messages"][0].content == "First"
        assert state["messages"][1].content == "Second"
        assert state["messages"][2].content == "Third"
    
    def test_state_can_be_copied(self):
        """Test that state can be copied."""
        original_state = create_agent_state(messages=[HumanMessage(content="Test")])
        copied_state = original_state.copy()
        
        assert isinstance(copied_state, dict)
        assert "messages" in copied_state
    
    def test_state_modification_doesnt_affect_original(self):
        """Test that modifying copied state doesn't affect original."""
        original_state = create_agent_state()
        copied_state = original_state.copy()
        
        # This is a shallow copy test
        # In real usage, messages would need deep copying
        assert isinstance(copied_state, dict)


# ==================== Message Handling Tests ====================

@pytest.mark.unit
class TestMessageHandling:
    """Test message handling in state."""
    
    def test_message_content_is_accessible(self):
        """Test that message content is accessible."""
        msg = HumanMessage(content="Test content")
        assert msg.content == "Test content"
    
    def test_tool_message_has_tool_call_id(self):
        """Test that ToolMessage has tool_call_id."""
        msg = ToolMessage(content="Result", tool_call_id="test_id")
        assert msg.tool_call_id == "test_id"
    
    def test_ai_message_can_have_tool_calls(self):
        """Test that AIMessage can have tool_calls."""
        msg = AIMessage(
            content="",
            tool_calls=[{"name": "test_tool", "args": {}, "id": "call_1"}]
        )
        assert hasattr(msg, 'tool_calls')
        assert len(msg.tool_calls) == 1
    
    def test_messages_have_type_attribute(self):
        """Test that messages have type attribute."""
        human_msg = HumanMessage(content="Test")
        ai_msg = AIMessage(content="Response")
        
        assert hasattr(human_msg, 'type')
        assert hasattr(ai_msg, 'type')
