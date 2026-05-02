from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./personal_trainer.db"
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    APP_NAME: str = "AurumSci"
    DEBUG: bool = True
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 5
    ANTHROPIC_API_KEY: str = ""

    # Stripe - chaves
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Stripe - Price IDs dos 4 planos PRO (criados em 01/05/2026)
    STRIPE_PRICE_BRONZE: str = ""
    STRIPE_PRICE_PRATA: str = ""
    STRIPE_PRICE_OURO: str = ""
    STRIPE_PRICE_DIAMANTE: str = ""
    # Stripe - Price ID do plano ALUNO (criado em 02/05/2026)
    STRIPE_PRICE_ALUNO: str = ""

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
