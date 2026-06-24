import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    database_path: str
    response_fixtures_path: str
    jwt_secret: str
    jwt_algorithm: str
    access_token_expires_seconds: int


def get_settings() -> Settings:
    return Settings(
        database_path=_require_env("DATABASE_PATH"),
        response_fixtures_path=_require_env("RESPONSE_FIXTURES_PATH"),
        jwt_secret=_require_env("JWT_SECRET"),
        jwt_algorithm=_require_env("JWT_ALGORITHM"),
        access_token_expires_seconds=int(_require_env("ACCESS_TOKEN_EXPIRES_SECONDS")),
    )


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value
