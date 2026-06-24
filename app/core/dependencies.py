from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import create_database_engine, create_session_factory


def get_database_session(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Iterator[Session]:
    engine = create_database_engine(settings.database_path)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        yield session


DatabaseSessionDep = Annotated[Session, Depends(get_database_session)]
