"""Environment-backed application configuration."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings with safe local defaults."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    retailpulse_env: str = "local"
    retailpulse_db_path: Path = Path("data/retailpulse.db")
    retailpulse_data_dir: Path = Path("data")
    retailpulse_mock_agent: bool = True
    gcp_project_id: str | None = None
    gcp_bigquery_dataset: str = "retailpulse"
    gcp_pubsub_topic: str = "retail-events"
    gemini_api_key: str | None = None


settings = Settings()
