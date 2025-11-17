"""
Custom exceptions for the NexTrade Multi-Agent Trading System.

This module defines a hierarchy of custom exceptions to provide better
error handling, debugging, and user feedback throughout the application.
"""

from typing import Optional, Dict, Any


class NexTradeException(Exception):
    """Base exception for all NexTrade-specific errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            details: Additional context information about the error
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/API responses."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


# Configuration Errors
class ConfigurationError(NexTradeException):
    """Raised when there's a configuration issue (missing API keys, invalid settings)."""
    pass


class MissingAPIKeyError(ConfigurationError):
    """Raised when a required API key is not found."""
    
    def __init__(self, api_name: str):
        super().__init__(
            f"Missing API key: {api_name}",
            details={"api_name": api_name}
        )


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration values are invalid."""
    
    def __init__(self, config_name: str, reason: str):
        super().__init__(
            f"Invalid configuration for '{config_name}': {reason}",
            details={"config_name": config_name, "reason": reason}
        )


# LLM and API Errors
class LLMError(NexTradeException):
    """Base class for LLM-related errors."""
    pass


class LLMConnectionError(LLMError):
    """Raised when unable to connect to LLM service."""
    
    def __init__(self, provider: str, reason: str):
        super().__init__(
            f"Failed to connect to {provider}: {reason}",
            details={"provider": provider, "reason": reason}
        )


class LLMRateLimitError(LLMError):
    """Raised when LLM rate limit is exceeded."""
    
    def __init__(self, provider: str, retry_after: Optional[int] = None):
        message = f"Rate limit exceeded for {provider}"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(
            message,
            details={"provider": provider, "retry_after": retry_after}
        )


class LLMResponseError(LLMError):
    """Raised when LLM response is invalid or cannot be parsed."""
    
    def __init__(self, reason: str, response: Optional[str] = None):
        super().__init__(
            f"Invalid LLM response: {reason}",
            details={"reason": reason, "response": response}
        )


# Database Errors
class DatabaseError(NexTradeException):
    """Base class for database-related errors."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when unable to connect to database."""
    
    def __init__(self, db_path: str, reason: str):
        super().__init__(
            f"Failed to connect to database at {db_path}: {reason}",
            details={"db_path": db_path, "reason": reason}
        )


class DatabaseQueryError(DatabaseError):
    """Raised when a database query fails."""
    
    def __init__(self, query: str, reason: str):
        super().__init__(
            f"Database query failed: {reason}",
            details={"query": query[:100], "reason": reason}  # Truncate query for logging
        )


class RecordNotFoundError(DatabaseError):
    """Raised when a requested record is not found."""
    
    def __init__(self, entity_type: str, identifier: str):
        super().__init__(
            f"{entity_type} not found: {identifier}",
            details={"entity_type": entity_type, "identifier": identifier}
        )


# Trading Errors
class TradingError(NexTradeException):
    """Base class for trading-related errors."""
    pass


class InvalidOrderError(TradingError):
    """Raised when an order is invalid."""
    
    def __init__(self, reason: str, order_details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Invalid order: {reason}",
            details={"reason": reason, "order_details": order_details}
        )


class OrderExecutionError(TradingError):
    """Raised when order execution fails."""
    
    def __init__(self, order_id: str, reason: str):
        super().__init__(
            f"Order execution failed for {order_id}: {reason}",
            details={"order_id": order_id, "reason": reason}
        )


class InsufficientFundsError(TradingError):
    """Raised when user has insufficient funds for an order."""
    
    def __init__(self, required: float, available: float):
        super().__init__(
            f"Insufficient funds: Required ${required:.2f}, Available ${available:.2f}",
            details={"required": required, "available": available}
        )


class MarketDataError(TradingError):
    """Raised when market data cannot be retrieved."""
    
    def __init__(self, symbol: str, reason: str):
        super().__init__(
            f"Failed to retrieve market data for {symbol}: {reason}",
            details={"symbol": symbol, "reason": reason}
        )


# Agent Errors
class AgentError(NexTradeException):
    """Base class for agent-related errors."""
    pass


class AgentTimeoutError(AgentError):
    """Raised when an agent operation times out."""
    
    def __init__(self, agent_name: str, timeout_seconds: int):
        super().__init__(
            f"Agent '{agent_name}' timed out after {timeout_seconds} seconds",
            details={"agent_name": agent_name, "timeout_seconds": timeout_seconds}
        )


class AgentLoopError(AgentError):
    """Raised when an agent enters an infinite loop."""
    
    def __init__(self, agent_name: str, iteration_count: int):
        super().__init__(
            f"Agent '{agent_name}' detected in infinite loop after {iteration_count} iterations",
            details={"agent_name": agent_name, "iteration_count": iteration_count}
        )


class InvalidAgentStateError(AgentError):
    """Raised when agent state is invalid or corrupted."""
    
    def __init__(self, agent_name: str, reason: str):
        super().__init__(
            f"Invalid state for agent '{agent_name}': {reason}",
            details={"agent_name": agent_name, "reason": reason}
        )


# Safety and Compliance Errors
class SafetyError(NexTradeException):
    """Base class for safety-related errors."""
    pass


class GuardrailViolationError(SafetyError):
    """Raised when input/output fails guardrail validation."""
    
    def __init__(self, violation_type: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Guardrail violation: {violation_type}",
            details={"violation_type": violation_type, **(details or {})}
        )


class RiskyOperationError(SafetyError):
    """Raised when a risky operation is attempted without approval."""
    
    def __init__(self, operation: str, reason: str):
        super().__init__(
            f"Risky operation blocked: {operation} - {reason}",
            details={"operation": operation, "reason": reason}
        )


class HumanApprovalRequiredError(SafetyError):
    """Raised when human approval is required but not provided."""
    
    def __init__(self, operation: str):
        super().__init__(
            f"Human approval required for: {operation}",
            details={"operation": operation}
        )


class HumanApprovalRejectedError(SafetyError):
    """Raised when human rejects an approval request."""
    
    def __init__(self, operation: str, reason: Optional[str] = None):
        message = f"Human rejected: {operation}"
        if reason:
            message += f" - Reason: {reason}"
        super().__init__(
            message,
            details={"operation": operation, "rejection_reason": reason}
        )


# External Service Errors
class ExternalServiceError(NexTradeException):
    """Base class for external service errors."""
    pass


class APIError(ExternalServiceError):
    """Raised when an external API call fails."""
    
    def __init__(self, service_name: str, status_code: Optional[int] = None, reason: str = ""):
        message = f"API error from {service_name}"
        if status_code:
            message += f" (HTTP {status_code})"
        if reason:
            message += f": {reason}"
        super().__init__(
            message,
            details={"service_name": service_name, "status_code": status_code, "reason": reason}
        )


class NetworkError(ExternalServiceError):
    """Raised when a network error occurs."""
    
    def __init__(self, reason: str):
        super().__init__(
            f"Network error: {reason}",
            details={"reason": reason}
        )


class ServiceUnavailableError(ExternalServiceError):
    """Raised when an external service is unavailable."""
    
    def __init__(self, service_name: str, reason: str = ""):
        super().__init__(
            f"Service unavailable: {service_name}" + (f" - {reason}" if reason else ""),
            details={"service_name": service_name, "reason": reason}
        )


# Validation Errors
class ValidationError(NexTradeException):
    """Base class for validation errors."""
    pass


class InputValidationError(ValidationError):
    """Raised when input validation fails."""
    
    def __init__(self, field_name: str, reason: str, value: Any = None):
        super().__init__(
            f"Invalid input for '{field_name}': {reason}",
            details={"field_name": field_name, "reason": reason, "value": str(value)}
        )


class OutputValidationError(ValidationError):
    """Raised when output validation fails."""
    
    def __init__(self, reason: str, output: Any = None):
        super().__init__(
            f"Invalid output: {reason}",
            details={"reason": reason, "output": str(output)[:200]}  # Truncate output
        )


# Workflow Errors
class WorkflowError(NexTradeException):
    """Base class for workflow-related errors."""
    pass


class WorkflowStateError(WorkflowError):
    """Raised when workflow is in an invalid state."""
    
    def __init__(self, current_state: str, expected_state: str):
        super().__init__(
            f"Invalid workflow state: Expected '{expected_state}', got '{current_state}'",
            details={"current_state": current_state, "expected_state": expected_state}
        )


class WorkflowInterruptedError(WorkflowError):
    """Raised when workflow is interrupted."""
    
    def __init__(self, reason: str):
        super().__init__(
            f"Workflow interrupted: {reason}",
            details={"reason": reason}
        )


class MaxRetriesExceededError(WorkflowError):
    """Raised when maximum retry attempts are exceeded."""
    
    def __init__(self, operation: str, max_retries: int):
        super().__init__(
            f"Maximum retries exceeded for '{operation}' ({max_retries} attempts)",
            details={"operation": operation, "max_retries": max_retries}
        )
