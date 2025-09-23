"""
State management for the multi-agent supervisor system.
"""

from langgraph.graph import MessagesState
from typing import Dict, Any


class SupervisorState(MessagesState):
    """
    State for the supervisor multi-agent system.
    
    Inherits from MessagesState to handle message history.
    Can be extended with additional state variables as needed.
    """
    pass


# For compatibility and future extensions
def get_initial_state() -> Dict[str, Any]:
    """Get initial state configuration."""
    return {
        "messages": [],
    }