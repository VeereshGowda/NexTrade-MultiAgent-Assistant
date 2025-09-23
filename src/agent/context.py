"""
Context management for the multi-agent supervisor system.
"""

import uuid
from typing import Dict, Any


class UserContext:
    """Manages user-specific context for the multi-agent system."""
    
    def __init__(self, user_id: str = None):
        self.user_id = user_id or str(uuid.uuid4())
        self.thread_id = str(uuid.uuid4())
    
    def get_config(self) -> Dict[str, Any]:
        """Get LangGraph configuration with user context."""
        return {
            "configurable": {
                "thread_id": self.thread_id,
                "user_id": self.user_id
            }
        }
    
    def new_thread(self) -> str:
        """Start a new conversation thread."""
        self.thread_id = str(uuid.uuid4())
        return self.thread_id


def create_user_context(user_id: str = None) -> UserContext:
    """Create a new user context."""
    return UserContext(user_id=user_id)


def get_default_config() -> Dict[str, Any]:
    """Get default configuration for testing."""
    return {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "default_user"
        }
    }