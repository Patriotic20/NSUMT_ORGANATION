from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


load_dotenv()







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


class JwtConfig(BaseModel):
    access_secret_key: str
    refresh_secret_key: str
    access_secret_minutes: int
    refresh_secret_day: int
    algorithm: str
    
    
class HemisConfig(BaseModel):
    base_url: str

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )

    hemis: HemisConfig = HemisConfig(base_url="https://student.ndki.uz/rest/v1")
    db: DatabaseConfig
    jwt: JwtConfig

settings = AppSettings()
