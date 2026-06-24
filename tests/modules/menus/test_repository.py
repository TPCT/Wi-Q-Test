from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import seed_from_response_files
from app.core.tables import Base
from app.modules.menus.models import Menu
from app.modules.menus.repository import SqlAlchemyMenuRepository


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


async def test_lists_seeded_menus() -> None:
    session = create_seeded_session()
    repository = SqlAlchemyMenuRepository(session=session)

    menus = await repository.list_menus()

    assert Menu(id=3, name="Takeaway") in menus
    assert Menu(id=4, name="Delivery") in menus
    assert len(menus) == 5
