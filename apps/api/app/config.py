from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_database_url(url: str) -> str:
    """Ensure the URL uses the psycopg (v3) driver.

    Render injects ``postgresql://…`` which SQLAlchemy maps to psycopg2.
    Replace the scheme so the correct driver is used everywhere.
    """
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


class Settings(BaseSettings):
    app_name: str = "SMB Cash Flow Risk API"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/smb_cashflow_risk"
    allowed_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def get_database_url(self) -> str:
        return _normalize_database_url(self.database_url)


settings = Settings()
