from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Fleet Maintenance & Spares"
    secret_key: str = "change-me-in-prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "postgresql+psycopg://fleet:fleet@db:5432/fleetdb"
    scheduler_enabled: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
