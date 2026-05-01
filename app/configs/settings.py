from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List, Optional

class DatabaseSettings(BaseSettings):
    database_type: str = Field(default="postgresql", alias="DATABASE_TYPE")
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    
    postgres_driver: str = Field(default="postgresql+psycopg2", alias="POSTGRES_DRIVER")
    postgres_user: str = Field(default="ric_datbrdg", alias="POSTGRES_USER")
    postgres_password: str = Field(default="Ricago@312", alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="ric_databridge", alias="POSTGRES_DB")

    model_config = SettingsConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")

    def get_db_url(self) -> str:
        #print(f"##### PostgreSQL connection URL (self URL) in settings.py file: {self.database_url} #####")
        if self.database_url:
            return self.database_url
        
        # Default to PostgreSQL
        #print(f"##### PostgreSQL connection URL (new URL) in setting.py file: {self.postgres_driver}://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db} #####")
        return f"{self.postgres_driver}://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

class MailSettings(BaseSettings):
    mail_username: str = Field(alias="MAIL_USERNAME")
    mail_password: str = Field(alias="MAIL_PASSWORD")
    mail_from: str = Field(default="rica@ricago.com", alias="MAIL_FROM")
    mail_port: int = Field(default=587, alias="MAIL_PORT")
    mail_server: str = Field(default="smtp.gmail.com", alias="MAIL_SERVER")
    mail_starttls: bool = Field(default=False, alias="MAIL_STARTTLS")
    mail_ssl_tls: bool = Field(default=True, alias="MAIL_SSL_TLS")
    use_credentials: bool = Field(default=True, alias="USE_CREDENTIALS")
    validate_certs: bool = Field(default=True, alias="VALIDATE_CERTS")
    mail_to: str = Field(default="rica_admin@ricago.com", alias="MAIL_TO")
    support_email: str = Field(default="support@ricago.com", alias="SUPPORT_EMAIL")
    mail_provider: str = Field(default="gmail", alias="MAIL_PROVIDER")

    model_config = SettingsConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")

class ServerSettings(BaseSettings):
    cors_urls: List[str] = Field(default=["localhost"], alias="CORS_URLS")
    public_paths: List[str] = Field(default=["/"], alias="PUBLIC_PATHS")
    api_secret_key: str = Field(default="RICAGO", alias="API_SECRET_KEY")
    api_rate_limit: int = Field(default=1000, alias="API_RATE_LIMIT")
    token_secret_key: str = Field(default="RICAGO", alias="TOKEN_SECRET_KEY")
    token_expire_minutes: int = Field(default=60, alias="TOKEN_EXPIRE_MINUTES")
    token_issuer: str = Field(default="RICAGO", alias="TOKEN_ISSUER")
    token_algorithm: str = Field(default="HS256", alias="TOKEN_KEY_ALGORITHM")
    app_token_path:str = Field(default=["/ricauth/GetAppAuthToken"], alias="AUTH_TOKEN_PATH")
    api_name: str = Field(default="Ricago DataBridge API Server", alias="API_NAME")
    version: str = Field(default="0.1.1", alias="VERSION")
    
    model_config = SettingsConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")

class CMSSettings(BaseSettings):
    cms_api_url: str = Field(default="https://test.ricago.com/cmscontentconfig/configuration/ContentPush", alias="CMS_API_URL")
    cms_auth_token: str = Field(default="B4D1F1C67CE69F5BFDF2B63A6A0F1444D1C29DCD0034081BD5CF45C9FA88379B", alias="CMS_AUTH_TOKEN")
    cms_clients_endpoint: str = Field(default="GetRegulatorPortalCredentials", alias="CMS_CLIENTS_ENDPOINT")

    model_config = SettingsConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")

class AppSettings(BaseSettings):
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    mail: MailSettings = Field(default_factory=MailSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    cms: CMSSettings = Field(default_factory=CMSSettings)
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Singleton instance
settings = AppSettings()
