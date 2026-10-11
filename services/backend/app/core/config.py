from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AegisCommerce Backend"
    ENVIRONMENT: str = "development"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "aegis_user"
    POSTGRES_PASSWORD: str = "aegis_password"
    POSTGRES_DB: str = "aegis_db"

    DATABASE_URL: str = ""

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = ""

    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    def model_post_init(self, __context):
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        if not self.REDIS_URL:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/2"

    @property
    def celery_broker_url(self) -> str:
        return self.CELERY_BROKER_URL

    @property
    def celery_result_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND

settings = Settings()
