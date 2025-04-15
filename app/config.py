from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    astra_db_api_endpoint: str
    astra_db_application_token: str
    astra_db_application_token2: str
    astra_db_keyspace: str
    mistral_api_key: str

    class Config:
        env_file = '.env'

settings = Settings()