import pytest
from pydantic import ValidationError

from src.core.config import Settings


def test_default_settings_load_successfully() -> None:
    """Assert default settings instantiate with expected values."""
    settings = Settings()
    assert settings.app_name == "fintech-data-platform"
    assert settings.environment == "development"
    assert settings.postgres_port == 5432
    assert settings.minio_secure is False


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Assert environment variables override defaults."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.setenv("MINIO_SECURE", "true")

    settings = Settings()
    assert settings.environment == "production"
    assert settings.postgres_port == 5433
    assert settings.minio_secure is True


def test_invalid_environment_raises_validation_error() -> None:
    """Assert setting an invalid environment literal raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings(environment="invalid_env")  # type: ignore[arg-type]


def test_invalid_port_raises_validation_error() -> None:
    """Assert non-numeric port raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings(postgres_port="not_a_number")  # type: ignore[arg-type]
