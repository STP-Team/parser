from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OKC_USERNAME: str
    OKC_PASSWORD: str
    OKC_BASE_URL: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str

    DB_STP_NAME: str
    DB_STATS_NAME: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
