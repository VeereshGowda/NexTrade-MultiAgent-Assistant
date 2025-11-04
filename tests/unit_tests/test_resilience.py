"""
Unit tests for resilience utilities.

Tests retry logic, circuit breakers, timeouts, and error handling.
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from agent.resilience import (
    RetryConfig,
    calculate_backoff_delay,
    retry_with_backoff,
    CircuitBreaker,
    CircuitBreakerState,
    FallbackChain,
    RateLimiter,
    HealthCheck
)


# ==================== Retry Logic Tests ====================

@pytest.mark.unit
class TestRetryLogic:
    """Test retry functionality with exponential backoff."""
    
    def test_retry_config_defaults(self):
        """Test default retry configuration."""
        config = RetryConfig()
        
        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
    
    def test_calculate_backoff_delay(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            jitter=False
        )
        
        # Test exponential growth
        assert calculate_backoff_delay(0, config) == 1.0
        assert calculate_backoff_delay(1, config) == 2.0
        assert calculate_backoff_delay(2, config) == 4.0
        assert calculate_backoff_delay(3, config) == 8.0
    
    def test_backoff_respects_max_delay(self):
        """Test that backoff doesn't exceed max delay."""
        config = RetryConfig(
            initial_delay=1.0,
            max_delay=5.0,
            exponential_base=2.0,
            jitter=False
        )
        
        # Should cap at max_delay
        assert calculate_backoff_delay(10, config) == 5.0
    
    def test_retry_success_on_first_attempt(self):
        """Test successful execution on first try."""
        mock_func = Mock(return_value="success")
        
        @retry_with_backoff(retry_config=RetryConfig(max_retries=3))
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_success_after_failures(self):
        """Test successful execution after retries."""
        mock_func = Mock(side_effect=[
            ConnectionError("Failed"),
            ConnectionError("Failed"),
            "success"
        ])
        
        @retry_with_backoff(
            retry_config=RetryConfig(max_retries=3, initial_delay=0.01),
            retryable_exceptions=(ConnectionError,)
        )
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_retry_exhausted_raises_exception(self):
        """Test that exception is raised after max retries."""
        mock_func = Mock(side_effect=ConnectionError("Always fails"))
        
        @retry_with_backoff(
            retry_config=RetryConfig(max_retries=2, initial_delay=0.01),
            retryable_exceptions=(ConnectionError,)
        )
        def test_func():
            return mock_func()
        
        with pytest.raises(ConnectionError):
            test_func()
        
        assert mock_func.call_count == 3  # Initial + 2 retries
    
    def test_retry_only_on_specified_exceptions(self):
        """Test that only specified exceptions trigger retry."""
        mock_func = Mock(side_effect=ValueError("Wrong exception"))
        
        @retry_with_backoff(
            retry_config=RetryConfig(max_retries=3),
            retryable_exceptions=(ConnectionError,)
        )
        def test_func():
            return mock_func()
        
        with pytest.raises(ValueError):
            test_func()
        
        # Should fail immediately, no retries
        assert mock_func.call_count == 1
    
    def test_retry_callback_invoked(self):
        """Test that on_retry callback is called."""
        callback_mock = Mock()
        mock_func = Mock(side_effect=[
            ConnectionError("Failed"),
            "success"
        ])
        
        @retry_with_backoff(
            retry_config=RetryConfig(max_retries=2, initial_delay=0.01),
            retryable_exceptions=(ConnectionError,),
            on_retry=callback_mock
        )
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert callback_mock.call_count == 1  # Called on first retry


# ==================== Circuit Breaker Tests ====================

@pytest.mark.unit
class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    def test_circuit_breaker_initial_state(self):
        """Test circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker(failure_threshold=3)
        
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
    
    def test_circuit_breaker_normal_operation(self):
        """Test normal operation in CLOSED state."""
        cb = CircuitBreaker(failure_threshold=3)
        mock_func = Mock(return_value="success")
        
        result = cb.call(mock_func, "arg1", key="value")
        
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
    
    def test_circuit_breaker_opens_after_threshold(self):
        """Test circuit breaker opens after failure threshold."""
        cb = CircuitBreaker(failure_threshold=3, expected_exception=ValueError)
        mock_func = Mock(side_effect=ValueError("Error"))
        
        # Trigger failures up to threshold
        for i in range(3):
            with pytest.raises(ValueError):
                cb.call(mock_func)
        
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 3
    
    def test_circuit_breaker_blocks_when_open(self):
        """Test that circuit breaker blocks calls when OPEN."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=10.0,
            expected_exception=ValueError
        )
        mock_func = Mock(side_effect=ValueError("Error"))
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(mock_func)
        
        assert cb.state == CircuitBreakerState.OPEN
        
        # Next call should be blocked
        with pytest.raises(Exception, match="Circuit breaker.*is OPEN"):
            cb.call(mock_func)
    
    def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker transitions to HALF_OPEN for recovery."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1,  # Short timeout for testing
            expected_exception=ValueError
        )
        
        # Open the circuit
        mock_func = Mock(side_effect=ValueError("Error"))
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(mock_func)
        
        assert cb.state == CircuitBreakerState.OPEN
        
        # Wait for recovery timeout
        time.sleep(0.2)
        
        # Next call should attempt HALF_OPEN
        mock_func = Mock(return_value="success")
        result = cb.call(mock_func)
        
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED
    
    def test_circuit_breaker_manual_reset(self):
        """Test manual reset of circuit breaker."""
        cb = CircuitBreaker(failure_threshold=2, expected_exception=ValueError)
        mock_func = Mock(side_effect=ValueError("Error"))
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(mock_func)
        
        assert cb.state == CircuitBreakerState.OPEN
        
        # Manual reset
        cb.reset()
        
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0


# ==================== Fallback Chain Tests ====================

@pytest.mark.unit
class TestFallbackChain:
    """Test fallback chain functionality."""
    
    def test_fallback_chain_primary_success(self):
        """Test primary function executes successfully."""
        primary = Mock(return_value="primary_result")
        fallback1 = Mock(return_value="fallback1_result")
        
        chain = FallbackChain(primary, fallback1)
        result = chain.execute()
        
        assert result == "primary_result"
        assert primary.call_count == 1
        assert fallback1.call_count == 0
    
    def test_fallback_chain_uses_fallback(self):
        """Test fallback is used when primary fails."""
        primary = Mock(side_effect=ConnectionError("Primary failed"))
        fallback1 = Mock(return_value="fallback1_result")
        
        chain = FallbackChain(primary, fallback1)
        result = chain.execute()
        
        assert result == "fallback1_result"
        assert primary.call_count == 1
        assert fallback1.call_count == 1
    
    def test_fallback_chain_multiple_fallbacks(self):
        """Test multiple fallbacks in sequence."""
        primary = Mock(side_effect=ConnectionError("Primary failed"))
        fallback1 = Mock(side_effect=ConnectionError("Fallback1 failed"))
        fallback2 = Mock(return_value="fallback2_result")
        
        chain = FallbackChain(primary, fallback1, fallback2)
        result = chain.execute()
        
        assert result == "fallback2_result"
        assert primary.call_count == 1
        assert fallback1.call_count == 1
        assert fallback2.call_count == 1
    
    def test_fallback_chain_all_fail(self):
        """Test exception raised when all fallbacks fail."""
        primary = Mock(side_effect=ConnectionError("Primary failed"))
        fallback1 = Mock(side_effect=ConnectionError("Fallback1 failed"))
        
        chain = FallbackChain(primary, fallback1)
        
        with pytest.raises(ConnectionError):
            chain.execute()


# ==================== Rate Limiter Tests ====================

@pytest.mark.unit
class TestRateLimiter:
    """Test rate limiter functionality."""
    
    def test_rate_limiter_allows_within_limit(self):
        """Test calls are allowed within rate limit."""
        limiter = RateLimiter(max_calls=5, time_window=1.0)
        
        # Should allow 5 calls
        for i in range(5):
            assert limiter.is_allowed() is True
    
    def test_rate_limiter_blocks_excess_calls(self):
        """Test calls are blocked when limit exceeded."""
        limiter = RateLimiter(max_calls=3, time_window=1.0)
        
        # Allow 3 calls
        for i in range(3):
            assert limiter.is_allowed() is True
        
        # Block 4th call
        assert limiter.is_allowed() is False
    
    def test_rate_limiter_resets_after_window(self):
        """Test rate limiter resets after time window."""
        limiter = RateLimiter(max_calls=2, time_window=0.1)
        
        # Use up limit
        assert limiter.is_allowed() is True
        assert limiter.is_allowed() is True
        assert limiter.is_allowed() is False
        
        # Wait for window to pass
        time.sleep(0.15)
        
        # Should allow again
        assert limiter.is_allowed() is True


# ==================== Health Check Tests ====================

@pytest.mark.unit
class TestHealthCheck:
    """Test health check functionality."""
    
    def test_health_check_register_and_run(self):
        """Test registering and running health checks."""
        health = HealthCheck()
        
        check1 = Mock(return_value=True)
        check2 = Mock(return_value=True)
        
        health.register("component1", check1)
        health.register("component2", check2)
        
        results = health.run_all()
        
        assert results == {"component1": True, "component2": True}
        assert check1.call_count == 1
        assert check2.call_count == 1
    
    def test_health_check_handles_failures(self):
        """Test health check handles component failures."""
        health = HealthCheck()
        
        check1 = Mock(return_value=True)
        check2 = Mock(side_effect=Exception("Component failed"))
        
        health.register("component1", check1)
        health.register("component2", check2)
        
        results = health.run_all()
        
        assert results["component1"] is True
        assert results["component2"] is False
    
    def test_is_healthy_all_pass(self):
        """Test is_healthy when all checks pass."""
        health = HealthCheck()
        
        health.register("component1", Mock(return_value=True))
        health.register("component2", Mock(return_value=True))
        
        assert health.is_healthy() is True
    
    def test_is_healthy_with_failures(self):
        """Test is_healthy when some checks fail."""
        health = HealthCheck()
        
        health.register("component1", Mock(return_value=True))
        health.register("component2", Mock(return_value=False))
        
        assert health.is_healthy() is False
