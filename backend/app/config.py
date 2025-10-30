import os
from functools import lru_cache


class Settings:
    # Supabase/Postgres
    
    database_url: str = "postgresql://postgres.ystxeblrfwqmrjlaoygl:AfterQuery2025@aws-1-us-east-2.pooler.supabase.com:6543/postgres"
    
    

    # App
    app_base_url: str = os.getenv("APP_BASE_URL", "http://localhost:3000")
    api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


