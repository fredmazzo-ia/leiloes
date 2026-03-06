from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://leiloes:leiloes@localhost:5432/leiloes"

    class Config:
        env_file = ".env"


settings = Settings()
