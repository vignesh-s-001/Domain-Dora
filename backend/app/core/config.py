from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    REDIS_URL: str | None = None
    
    RDAP_TIMEOUT: int = 10
    DNS_TIMEOUT: int = 5
    SSL_TIMEOUT: int = 5
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
