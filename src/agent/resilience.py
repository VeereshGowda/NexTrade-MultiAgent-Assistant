"""
Resilience utilities for production-ready agentic systems.

This module provides retry logic, circuit breakers, timeouts, and error handling
to make the multi-agent system robust against real-world failures.
"""

import time
import logging
from functools import wraps
from typing import Callable, Any, Optional, Type, Tuple, Dict
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


# ==================== Retry Logic with Exponential Backoff ====================

class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def calculate_backoff_delay(
    attempt: int,
    config: RetryConfig
) -> float:
    """
    Calculate exponential backoff delay with optional jitter.
    
    Args:
        attempt: Current attempt number (0-indexed)
        config: Retry configuration
        
    Returns:
        Delay in seconds
    """
    delay = min(
        config.initial_delay * (config.exponential_base ** attempt),
        config.max_delay
    )
    
    if config.jitter:
        import random
        delay = delay * (0.5 + random.random() * 0.5)
    
    return delay


def retry_with_backoff(
    retry_config: Optional[RetryConfig] = None,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        retry_config: Retry configuration settings
        retryable_exceptions: Tuple of exception types to retry on
        on_retry: Optional callback function called on each retry
        
    Example:
        @retry_with_backoff(
            retry_config=RetryConfig(max_retries=3),
            retryable_exceptions=(ConnectionError, TimeoutError)
        )
        def call_external_api():
            # API call logic
            pass
    """
    if retry_config is None:
        retry_config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retry_config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == retry_config.max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after "
                            f"{retry_config.max_retries} retries: {e}"
                        )
                        raise
                    
                    delay = calculate_backoff_delay(attempt, retry_config)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{retry_config.max_retries + 1} "
                        f"failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    if on_retry:
                        on_retry(e, attempt)
                    
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator


# ==================== Circuit Breaker Pattern ====================

class CircuitBreakerState:
    """States for circuit breaker."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Blocking calls due to failures
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.
    
    Tracks failures and opens the circuit when threshold is exceeded,
    preventing further calls until recovery period passes.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
        name: str = "circuit_breaker"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitBreakerState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
            else:
                raise Exception(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service is unavailable."
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            logger.info(f"Circuit breaker '{self.name}' recovered. Closing circuit.")
        
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.error(
                f"Circuit breaker '{self.name}' OPENED after "
                f"{self.failure_count} failures"
            )
    
    def reset(self):
        """Manually reset circuit breaker."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time = None
        logger.info(f"Circuit breaker '{self.name}' manually reset")


# ==================== Timeout Handling ====================

class TimeoutError(Exception):
    """Raised when operation exceeds timeout."""
    pass


def with_timeout(timeout_seconds: float):
    """
    Decorator to add timeout to function execution.
    
    Args:
        timeout_seconds: Maximum execution time in seconds
        
    Example:
        @with_timeout(30.0)
        def slow_operation():
            # Long running operation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(
                    f"Function {func.__name__} exceeded timeout of {timeout_seconds}s"
                )
            
            # Set timeout alarm (Unix-like systems)
            if hasattr(signal, 'SIGALRM'):
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(timeout_seconds))
                
                try:
                    result = func(*args, **kwargs)
                finally:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
                
                return result
            else:
                # Fallback for Windows - just log warning
                logger.warning(
                    f"Timeout not supported on this platform. "
                    f"Running {func.__name__} without timeout."
                )
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


async def with_async_timeout(coro, timeout_seconds: float):
    """
    Run async coroutine with timeout.
    
    Args:
        coro: Coroutine to execute
        timeout_seconds: Maximum execution time
        
    Returns:
        Coroutine result
        
    Raises:
        asyncio.TimeoutError: If timeout exceeded
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.error(f"Async operation exceeded timeout of {timeout_seconds}s")
        raise


# ==================== Graceful Degradation ====================

class FallbackChain:
    """
    Chain of fallback functions to try in order.
    
    Executes primary function, and if it fails, tries fallbacks in sequence.
    """
    
    def __init__(self, primary: Callable, *fallbacks: Callable):
        self.primary = primary
        self.fallbacks = fallbacks
    
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute primary function with fallback chain.
        
        Args:
            *args, **kwargs: Arguments to pass to functions
            
        Returns:
            Result from first successful function
            
        Raises:
            Exception: If all functions fail
        """
        functions = [self.primary] + list(self.fallbacks)
        last_exception = None
        
        for i, func in enumerate(functions):
            try:
                func_name = getattr(func, '__name__', f'function_{i}')
                logger.info(
                    f"Attempting function {func_name} "
                    f"({'primary' if i == 0 else f'fallback {i}'})"
                )
                result = func(*args, **kwargs)
                
                if i > 0:
                    logger.warning(
                        f"Primary function failed, succeeded with fallback {i}"
                    )
                
                return result
                
            except Exception as e:
                last_exception = e
                func_name = getattr(func, '__name__', f'function_{i}')
                logger.warning(
                    f"Function {func_name} failed: {e}. "
                    f"Trying next fallback..."
                )
        
        logger.error("All functions in fallback chain failed")
        raise last_exception


# ==================== Rate Limiting ====================

class RateLimiter:
    """
    Simple rate limiter using token bucket algorithm.
    """
    
    def __init__(self, max_calls: int, time_window: float):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: list = []
    
    def is_allowed(self) -> bool:
        """Check if a new call is allowed."""
        now = time.time()
        
        # Remove old calls outside time window
        self.calls = [
            call_time for call_time in self.calls
            if now - call_time < self.time_window
        ]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        
        return False
    
    def wait_if_needed(self):
        """Wait if rate limit is exceeded."""
        while not self.is_allowed():
            time.sleep(0.1)


# ==================== Monitoring & Logging ====================

def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log function execution time.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function that logs execution time
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            logger.info(
                f"Function {func.__name__} completed in {elapsed:.2f}s"
            )
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Function {func.__name__} failed after {elapsed:.2f}s: {e}"
            )
            raise
    
    return wrapper


class HealthCheck:
    """
    Health check utility for monitoring system components.
    """
    
    def __init__(self):
        self.checks: Dict[str, Callable[[], bool]] = {}
    
    def register(self, name: str, check_func: Callable[[], bool]):
        """Register a health check function."""
        self.checks[name] = check_func
    
    def run_all(self) -> Dict[str, bool]:
        """Run all registered health checks."""
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                results[name] = check_func()
            except Exception as e:
                logger.error(f"Health check '{name}' failed: {e}")
                results[name] = False
        
        return results
    
    def is_healthy(self) -> bool:
        """Check if all components are healthy."""
        results = self.run_all()
        return all(results.values())
