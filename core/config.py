import os

from pydantic import BaseSettings


class Config(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    WRITER_DB_URL: str = f"mysql+aiomysql://fastapi:fastapi@localhost:3306/fastapi"
    READER_DB_URL: str = f"mysql+aiomysql://fastapi:fastapi@localhost:3306/fastapi"
    JWT_SECRET_KEY: str = (
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    )
    JWT_ALGORITHM: str = "HS256"
    SUPPORTED_ROLES = ["buyer", "seller"]
    SUPPORTED_COINS = [100, 50, 20, 10, 5]
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    JWT_EXPIRATION: int = 3600


class TestConfig(Config):
    WRITER_DB_URL: str = f"mysql+aiomysql://root:fastapi@localhost:3306/fastapi"
    READER_DB_URL: str = f"mysql+aiomysql://root:fastapi@localhost:3306/fastapi"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379


class DevelopmentConfig(Config):
    WRITER_DB_URL: str = f"mysql+aiomysql://root:fastapi@db:3306/fastapi"
    READER_DB_URL: str = f"mysql+aiomysql://root:fastapi@db:3306/fastapi"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379


class ProductionConfig(Config):
    DEBUG: str = False
    WRITER_DB_URL: str = f"mysql+aiomysql://fastapi:fastapi@localhost:3306/prod"
    READER_DB_URL: str = f"mysql+aiomysql://fastapi:fastapi@localhost:3306/prod"


def get_config():
    env = os.getenv("ENV", "dev")
    config_type = {
        "dev": DevelopmentConfig(),
        "test": TestConfig(),
        "prod": ProductionConfig(),
    }
    return config_type[env]


config: Config = get_config()
