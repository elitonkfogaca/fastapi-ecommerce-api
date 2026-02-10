from pydantic_settings import BaseSettings
from pydantic import Field



class Settings(BaseSettings):
    # App
    APP_NAME: str = 'FastAPI E-commerce API'
    DEBUG: bool = True

    # Database
    POSTGRES_HOST: str = Field(default='localhost')
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # JWT
    SECRET_KEY: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
