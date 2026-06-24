from pathlib import Path

import jwt
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.core.database import seed_from_response_files
from app.core.tables import Base
from app.modules.auth.repository import SqlAlchemyClientRepository
from app.modules.auth.service import AuthService, InvalidClientCredentialsError


def create_seeded_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = session_factory()
    seed_from_response_files(
        session=session,
        response_fixtures_path=Path("responses"),
    )
    return session


def create_settings() -> Settings:
    return Settings(
        database_path=":memory:",
        response_fixtures_path="responses",
        jwt_secret="test-secret-with-at-least-thirty-two-bytes",
        jwt_algorithm="HS256",
        access_token_expires_seconds=3600,
    )


async def test_creates_one_hour_jwt_for_valid_client_credentials() -> None:
    settings = create_settings()
    service = AuthService(
        client_repository=SqlAlchemyClientRepository(session=create_seeded_session()),
        settings=settings,
    )

    access_token = await service.create_access_token(
        client_id="1337",
        client_secret="4j3g4gj304gj3",
        grant_type="client_credentials",
    )

    claims = jwt.decode(
        access_token.access_token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
    assert access_token.expires_in == 3600
    assert access_token.token_type == "Bearer"
    assert claims["client_id"] == "1337"
    assert claims["sub"] == "1337"
    assert claims["grant_type"] == "client_credentials"
    assert claims["scope"] == "catalogue"
    assert claims["exp"] - claims["iat"] == 3600


async def test_rejects_invalid_client_secret() -> None:
    service = AuthService(
        client_repository=SqlAlchemyClientRepository(session=create_seeded_session()),
        settings=create_settings(),
    )

    with pytest.raises(InvalidClientCredentialsError):
        await service.create_access_token(
            client_id="1337",
            client_secret="wrong",
            grant_type="client_credentials",
        )
