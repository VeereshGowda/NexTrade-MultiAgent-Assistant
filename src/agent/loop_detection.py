"""
Loop detection and prevention middleware for the multi-agent system.

This module provides utilities to detect and prevent infinite loops
in agent routing and execution.
"""

import logging
import time
from typing import Any, Dict, Optional
from functools import wraps

from .state import LoopDetector

logger = logging.getLogger(__name__)

# Global loop detector instance
_loop_detector = LoopDetector(max_iterations=50, pattern_window=10)


def check_loop_conditions(state: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Check all loop detection conditions.
    
    Args:
        state: Current supervisor state
        
    Returns:
        Tuple of (should_stop, stop_message)
    """
    iteration_count = state.get("iteration_count", 0)
    agent_call_history = state.get("agent_call_history", [])
    
    # Check iteration limit
    is_exceeded, message = _loop_detector.check_iteration_limit(iteration_count)
    if is_exceeded:
        logger.error(f"Loop detected - Iteration limit: {message}")
        return True, message
    
    # Check repeated patterns
    is_loop, message = _loop_detector.check_repeated_pattern(agent_call_history)
    if is_loop:
        logger.error(f"Loop detected - Repeated pattern: {message}")
        return True, message
    
    # Check stuck agent
    is_stuck, message = _loop_detector.check_stuck_agent(agent_call_history)
    if is_stuck:
        logger.error(f"Loop detected - Stuck agent: {message}")
        return True, message
    
    return False, None


def update_loop_tracking(state: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
    """
    Update state with loop tracking information.
    
    Args:
        state: Current supervisor state
        agent_name: Name of the agent being called
        
    Returns:
        Updated state
    """
    # Initialize tracking fields if not present
    if "iteration_count" not in state:
        state["iteration_count"] = 0
    if "agent_call_history" not in state:
        state["agent_call_history"] = []
    if "start_timestamp" not in state:
        state["start_timestamp"] = time.time()
    
    # Update iteration count
    state["iteration_count"] += 1
    
    # Update agent call history
    state["agent_call_history"].append(agent_name)
    
    # Keep only last 20 calls to prevent memory bloat
    if len(state["agent_call_history"]) > 20:
        state["agent_call_history"] = state["agent_call_history"][-20:]
    
    # Update last agent
    state["last_agent"] = agent_name
    
    # Update execution time
    if state["start_timestamp"]:
        state["execution_time"] = time.time() - state["start_timestamp"]
    
    # Log progress
    logger.info(
        f"Agent routing: {agent_name} | "
        f"Iteration: {state['iteration_count']} | "
        f"Time: {state['execution_time']:.2f}s"
    )
    
    # Warn if approaching limits
    if state["iteration_count"] >= 40:
        logger.warning(
            f"Approaching iteration limit: {state['iteration_count']}/50. "
            f"Recent agents: {' -> '.join(state['agent_call_history'][-5:])}"
        )
    
    return state


def with_loop_detection(func):
    """
    Decorator to add loop detection to supervisor functions.
    
    Args:
        func: Function to wrap (typically supervisor.invoke)
        
    Returns:
        Wrapped function with loop detection
    """
    @wraps(func)
    def wrapper(input_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None):
        """
        Wrapper that checks for loops before and during execution.
        
        Args:
            input_data: Input to the supervisor
            config: Configuration including thread_id and user_id
            
        Returns:
            Supervisor response
        """
        # Initialize state tracking if this is a new invocation
        if "iteration_count" not in input_data:
            input_data["iteration_count"] = 0
            input_data["agent_call_history"] = []
            input_data["start_timestamp"] = time.time()
            input_data["loop_detected"] = False
        
        try:
            # Execute the original function
            result = func(input_data, config)
            
            # Check for loop conditions in the result state
            if isinstance(result, dict) and "iteration_count" in result:
                should_stop, stop_message = check_loop_conditions(result)
                
                if should_stop:
                    result["loop_detected"] = True
                    
                    # Add stop message to messages
                    from langchain_core.messages import AIMessage
                    if "messages" in result:
                        result["messages"].append(
                            AIMessage(
                                content=f"⚠️ **Execution Stopped - Loop Detected**\n\n{stop_message}\n\n"
                                        f"**Statistics:**\n"
                                        f"- Total iterations: {result['iteration_count']}\n"
                                        f"- Execution time: {result.get('execution_time', 0):.2f}s\n"
                                        f"- Agent call sequence: {' -> '.join(result.get('agent_call_history', []))}\n\n"
                                        f"💡 **Recommendation:** Try rephrasing your request or breaking it into smaller, "
                                        f"more specific tasks."
                            )
                        )
                    
                    logger.error(
                        f"Loop detected after {result['iteration_count']} iterations. "
                        f"Agent sequence: {' -> '.join(result.get('agent_call_history', []))}"
                    )
            
            return result
            
        except RecursionError as e:
            logger.error(f"RecursionError caught: {e}. This indicates an infinite loop in agent routing.")
            
            # Create error response
            from langchain_core.messages import AIMessage
            error_response = {
                "messages": input_data.get("messages", []) + [
                    AIMessage(
                        content="⚠️ **Execution Stopped - Recursion Limit Reached**\n\n"
                                "The system detected a potential infinite loop in agent routing and stopped execution.\n\n"
                                "**Possible Causes:**\n"
                                "- Circular dependencies between agents\n"
                                "- Agents repeatedly calling each other without making progress\n"
                                "- Task too complex for current agent configuration\n\n"
                                "💡 **Recommendation:** Try simplifying your request or breaking it into smaller tasks."
                    )
                ],
                "loop_detected": True,
                "error": "RecursionError",
                "iteration_count": input_data.get("iteration_count", 0),
            }
            
            return error_response
        
        except Exception as e:
            logger.error(f"Error in loop detection wrapper: {e}")
            raise
    
    return wrapper


def get_loop_statistics(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get loop detection statistics from state.
    
    Args:
        state: Supervisor state
        
    Returns:
        Statistics dictionary
    """
    return {
        "iteration_count": state.get("iteration_count", 0),
        "max_iterations": state.get("max_iterations", 50),
        "agent_call_history": state.get("agent_call_history", []),
        "last_agent": state.get("last_agent", None),
        "loop_detected": state.get("loop_detected", False),
        "execution_time": state.get("execution_time", 0.0),
        "iterations_remaining": state.get("max_iterations", 50) - state.get("iteration_count", 0),
    }


def reset_loop_tracking(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reset loop tracking in state (useful for testing).
    
    Args:
        state: Supervisor state
        
    Returns:
        State with reset tracking
    """
    state["iteration_count"] = 0
    state["agent_call_history"] = []
    state["last_agent"] = None
    state["loop_detected"] = False
    state["start_timestamp"] = time.time()
    state["execution_time"] = 0.0
    
    logger.info("Loop tracking reset")
    
    return state
