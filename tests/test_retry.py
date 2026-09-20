import pytest
from src.utils.exceptions import (
    FatalSchemaError,
    RateLimitError,
    ServiceUnavailableError,
    TransientIngestionError,
)
from src.utils.retry import fintech_retry, raise_error


@pytest.fixture(autouse=True)
def fast_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock time.sleep so backoff and jitter tests execute instantly without delays."""
    monkeypatch.setattr("time.sleep", lambda _: None)


def test_retry_recovers_after_transient_failures() -> None:
    """Assert function recovers after 2 transient failures and succeeds on 3rd attempt."""
    attempts = 0

    @fintech_retry
    def flaky_api() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ServiceUnavailableError("Service temporarily unavailable")
        return "SUCCESS"

    result = flaky_api()

    assert result == "SUCCESS"
    assert attempts == 3


def test_retry_exhaustion_reraises_original_exception() -> None:
    """Assert original TransientIngestionError is raised after max attempts are exhausted."""
    attempts = 0

    @fintech_retry
    def always_failing_api() -> None:
        nonlocal attempts
        attempts += 1
        raise RateLimitError("HTTP 429: Too Many Requests")

    with pytest.raises(RateLimitError) as exc_info:
        always_failing_api()

    assert "HTTP 429" in str(exc_info.value)
    assert attempts == 3


def test_fatal_schema_error_fails_immediately_without_retry() -> None:
    """Assert FatalSchemaError aborts immediately on attempt 1 with zero retries."""
    attempts = 0

    @fintech_retry
    def corrupted_payload_api() -> None:
        nonlocal attempts
        attempts += 1
        raise FatalSchemaError("Payload missing required account_id")

    with pytest.raises(FatalSchemaError) as exc_info:
        corrupted_payload_api()

    assert "Payload missing" in str(exc_info.value)
    assert attempts == 1  # Crucial: Must NOT retry fatal errors


def test_unexpected_exception_fails_immediately() -> None:
    """Assert generic unhandled exceptions (e.g. ValueError) fail on attempt 1."""
    attempts = 0

    @fintech_retry
    def bug_in_code() -> None:
        nonlocal attempts
        attempts += 1
        raise ValueError("Unexpected programming error")

    with pytest.raises(ValueError):
        bug_in_code()

    assert attempts == 1


def test_raise_error_helper() -> None:
    """Assert the pre-decorated raise_error helper function behaves as expected."""
    with pytest.raises(RateLimitError):
        raise_error(429)

    with pytest.raises(ServiceUnavailableError):
        raise_error(503)

    assert raise_error(200) == "error"
