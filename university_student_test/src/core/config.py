from pydantic_settings import BaseSettings , SettingsConfigDict
from pydantic import PostgresDsn , BaseModel
from dotenv import load_dotenv
from typing import Literal

load_dotenv()

LOG_DEFAULT_FORMAT = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"

class GunicornConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8010
    workers: int = 2
    timeout: int = 60
    
class LoggingConfig(BaseModel):
    log_level: Literal[
        'debug',
        'info',
        'warning',
        'error',
        'critical',
    ] = 'info'
    log_format: str = LOG_DEFAULT_FORMAT

class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8010
    is_reload: bool = True
    

class JwtConfig(BaseModel):
    access_secret_key: str 
    algorithm: str
    
class FileUrl(BaseModel):
    http: str
    upload_dir: str

class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class OrganizationUrls(BaseModel):
    permissions: str
    

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template" , ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    
    gunicorn: GunicornConfig = GunicornConfig()
    logging: LoggingConfig = LoggingConfig()
    server: ServerConfig = ServerConfig()
    db: DatabaseConfig
    jwt: JwtConfig
    file_url: FileUrl
    organization_urls: OrganizationUrls 
    
    
    
    
settings = AppSettings()
    
