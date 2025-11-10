from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hora
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 14  # 14 días
    
    POKEAPI_BASE_URL: str = "https://pokeapi.co/api/v2"
    POKEAPI_TIMEOUT_SECONDS: float = 5.0
    POKEAPI_RETRIES: int = 2
    
    CACHE_TTL_SECONDS: int = 60 * 60 * 12  # 12h
    
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"

settings = Settings()
