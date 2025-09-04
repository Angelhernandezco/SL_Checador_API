from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DB_URL: str
    PAYROLL_DB_URL: str
    PRODUCTION: bool
    PROGRAMA: str

    class Config:
        env_file = ".env"

settings = Settings()
