import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    PROJECT_NAME: str = "PaperFox"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    SECRET_KEY: str = "paperfox_super_secret_access_key_change_in_production_32chars"
    REFRESH_SECRET_KEY: str = "paperfox_super_secret_refresh_key_change_in_production_32chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECURE_COOKIES: bool = False
    
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "paperfox"
    
    ALLOWED_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Document Engine Configuration
    # Name or PATH-resolvable command for the LaTeX compiler (pdflatex, xelatex)
    LATEX_COMPILER: str = "pdflatex"
    # Optional: explicit full path to the compiler binary.
    # Use when the compiler is installed but NOT on the backend process PATH.
    # Example: C:\Users\you\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe
    # Example: /usr/bin/pdflatex
    LATEX_COMPILER_PATH: str = ""


    # Rate Limiting Configuration
    RATE_LIMITING_ENABLED: bool = True
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    RATE_LIMIT_AI_PER_MINUTE: int = 30

    # AI Providers Configuration
    GOOGLE_API_KEY: str = ""
    GOOGLE_MODEL: str = "gemini-2.5-flash"

    NVIDIA_API_KEY: str = ""
    NVIDIA_MODEL: str = "meta/llama-3.1-70b-instruct"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "nvidia/nemotron-3.5-lightning:free"
    OPENROUTER_FALLBACK_MODEL: str = "liquid/lfm-2.5-2.6b:free"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-20b"

    AI_TIMEOUT_SECONDS: int = 30
    AI_MAX_RETRIES: int = 2

    JD_ANALYSIS_PRIMARY_PROVIDER: str = "gemini"
    JD_ANALYSIS_FALLBACK_PROVIDERS: Union[List[str], str] = ["groq", "openrouter"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("JD_ANALYSIS_FALLBACK_PROVIDERS", mode="before")
    def parse_fallback_providers(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [provider.strip().lower() for provider in v.split(",") if provider.strip()]
        return v


settings = Settings()
