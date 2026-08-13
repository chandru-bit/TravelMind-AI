import time
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger("resilience")

def retry_with_backoff(max_retries: int = 3, initial_delay: float = 0.5, backoff_factor: float = 2.0):
    """
    Decorator for retrying transient operations with exponential backoff.
    Does not retry client errors (400, 401, 403, 404).
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    # Do not retry HTTP 4xx validation or client error exceptions
                    status_code = getattr(exc, "status_code", None)
                    if status_code and 400 <= status_code < 500:
                        raise exc
                    
                    logger.warning(
                        "Attempt %d/%d for %s failed (%s). Retrying in %.2f seconds...",
                        attempt, max_retries, func.__name__, str(exc), delay
                    )
                    if attempt == max_retries:
                        break
                    time.sleep(delay)
                    delay *= backoff_factor
            raise last_exception
        return wrapper
    return decorator


class CircuitBreakerOpenException(Exception):
    """Raised when circuit breaker is in OPEN state."""
    pass


class CircuitBreaker:
    """
    Circuit Breaker pattern to protect system against cascading failures.
    States: CLOSED -> OPEN -> HALF-OPEN -> CLOSED
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 10.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.last_state_change = time.time()

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            now = time.time()
            
            if self.state == "OPEN":
                if now - self.last_state_change > self.recovery_timeout:
                    self.state = "HALF-OPEN"
                    self.last_state_change = now
                    logger.info("CircuitBreaker transitioned to HALF-OPEN for %s", func.__name__)
                else:
                    logger.warning("CircuitBreaker OPEN for %s. Request short-circuited.", func.__name__)
                    raise CircuitBreakerOpenException("Circuit breaker is OPEN. External dependency unavailable.")

            try:
                result = func(*args, **kwargs)
                if self.state == "HALF-OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                    self.last_state_change = now
                    logger.info("CircuitBreaker recovered to CLOSED for %s", func.__name__)
                return result
            except Exception as exc:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    self.last_state_change = now
                    logger.error("Failure threshold reached. CircuitBreaker switched to OPEN for %s", func.__name__)
                raise exc
        return wrapper
