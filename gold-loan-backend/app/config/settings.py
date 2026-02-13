from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_name: str = 'Gold Loan Backend'
    env: str = 'dev'
    api_prefix: str = '/api/v1'

    # Supabase Postgres DSN only
    supabase_db_url: str = Field(..., alias='SUPABASE_DB_URL')
    jwt_secret: str = Field('change-me', alias='JWT_SECRET')


settings = Settings()
