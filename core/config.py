"""
Central settings, read from environment variables / a local .env file.
Never commit a real .env — use .env.example as the template.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "VITERA Camp API"

    # --- TiDB connection ---
    DB_HOST: str = "localhost"
    DB_PORT: int = 4000
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "vitera"
    DB_SSL: bool = True  # TiDB Cloud requires TLS

    # --- Auth ---
    JWT_SECRET_KEY: str = "CHANGE_ME"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 12  # 12h shift-length session

    @property
    def database_url(self) -> str:
        # pymysql driver, sync. TLS itself is configured via connect_args
        # in config/database/db_session.py (pymysql doesn't take ssl as a
        # URL query param the way asyncmy does).
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )


settings = Settings()