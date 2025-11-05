"""
State management for the multi-agent supervisor system.
"""

from langgraph.graph import MessagesState
from typing import Dict, Any, Optional
from typing_extensions import TypedDict


class SupervisorState(MessagesState):
    """
    State for the supervisor multi-agent system.
    
    Inherits from MessagesState to handle message history.
    Extended with loop detection and iteration limits for safety.
    """
    # Loop detection and limits
    iteration_count: int = 0
    max_iterations: int = 50
    agent_call_history: list[str] = []
    last_agent: Optional[str] = None
    loop_detected: bool = False
    
    # Performance tracking
    start_timestamp: Optional[float] = None
    execution_time: float = 0.0


class LoopDetector:
    """
    Detects potential infinite loops in agent routing.
    
    Strategies:
    1. Maximum iteration count
    2. Repeated agent call patterns
    3. No progress detection
    """
    
    def __init__(self, max_iterations: int = 50, pattern_window: int = 10):
        """
        Initialize loop detector.
        
        Args:
            max_iterations: Maximum allowed iterations before stopping
            pattern_window: Number of recent calls to check for patterns
        """
        self.max_iterations = max_iterations
        self.pattern_window = pattern_window
    
    def check_iteration_limit(self, iteration_count: int) -> tuple[bool, str]:
        """
        Check if iteration limit exceeded.
        
        Args:
            iteration_count: Current iteration count
            
        Returns:
            Tuple of (is_exceeded, message)
        """
        if iteration_count >= self.max_iterations:
            return True, (
                f"Maximum iteration limit ({self.max_iterations}) reached. "
                f"Stopping to prevent infinite loop. "
                f"This may indicate a routing issue or circular dependencies between agents."
            )
        return False, ""
    
    def check_repeated_pattern(self, agent_call_history: list[str]) -> tuple[bool, str]:
        """
        Check for repeated agent call patterns indicating a loop.
        
        Args:
            agent_call_history: List of recent agent calls
            
        Returns:
            Tuple of (is_loop, message)
        """
        if len(agent_call_history) < self.pattern_window:
            return False, ""
        
        # Check last N calls
        recent_calls = agent_call_history[-self.pattern_window:]
        
        # Detect simple loops (A->B->A->B->A->B)
        if len(set(recent_calls)) <= 2:
            unique_agents = set(recent_calls)
            return True, (
                f"Detected potential routing loop between agents: {', '.join(unique_agents)}. "
                f"Last {self.pattern_window} calls: {' -> '.join(recent_calls)}. "
                f"Stopping to prevent infinite loop."
            )
        
        # Detect repeated sequences (A->B->C->A->B->C)
        sequence_length = 3
        if len(recent_calls) >= sequence_length * 2:
            first_sequence = recent_calls[:sequence_length]
            second_sequence = recent_calls[sequence_length:sequence_length*2]
            if first_sequence == second_sequence:
                return True, (
                    f"Detected repeated agent call sequence: {' -> '.join(first_sequence)}. "
                    f"Stopping to prevent infinite loop."
                )
        
        return False, ""
    
    def check_stuck_agent(self, agent_call_history: list[str]) -> tuple[bool, str]:
        """
        Check if same agent is being called repeatedly without progress.
        
        Args:
            agent_call_history: List of recent agent calls
            
        Returns:
            Tuple of (is_stuck, message)
        """
        if len(agent_call_history) < 5:
            return False, ""
        
        # Check if last 5 calls are to the same agent
        recent_calls = agent_call_history[-5:]
        if len(set(recent_calls)) == 1:
            stuck_agent = recent_calls[0]
            return True, (
                f"Agent '{stuck_agent}' has been called 5 times consecutively without progress. "
                f"This may indicate the agent is unable to complete its task. "
                f"Stopping to prevent infinite loop."
            )
        
        return False, ""


# For compatibility and future extensions
def get_initial_state() -> Dict[str, Any]:
    """Get initial state configuration."""
    import time
    return {
        "messages": [],
        "iteration_count": 0,
        "max_iterations": 50,
        "agent_call_history": [],
        "last_agent": None,
        "loop_detected": False,
        "start_timestamp": time.time(),
        "execution_time": 0.0,
    }