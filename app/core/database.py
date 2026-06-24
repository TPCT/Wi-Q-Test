import json
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.core.tables import Base, ClientTable, MenuTable, ProductTable


def create_database_engine(database_path: str) -> Engine:
    return create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def initialize_database(settings: Settings) -> None:
    engine = create_database_engine(settings.database_path)
    Base.metadata.create_all(engine)

    session_factory = create_session_factory(engine)
    with session_factory() as session:
        seed_from_response_files(
            session=session,
            response_fixtures_path=Path(settings.response_fixtures_path),
        )


def seed_from_response_files(
    session: Session,
    response_fixtures_path: Path,
) -> None:
    menus_payload = _read_json(response_fixtures_path / "menus.json")
    clients_payload = _read_json(response_fixtures_path.parent / "seed" / "clients.json")
    menu_product_sources_payload = _read_json(
        response_fixtures_path.parent / "seed" / "menu-product-sources.json"
    )

    _upsert_clients(session, clients_payload["data"])
    _upsert_menus(session, menus_payload["data"])
    session.flush()
    _upsert_menu_products_from_sources(
        session=session,
        response_fixtures_path=response_fixtures_path,
        source_payloads=menu_product_sources_payload["data"],
    )
    session.commit()


def _upsert_menus(session: Session, menu_payloads: list[dict[str, object]]) -> None:
    for menu_payload in menu_payloads:
        menu = session.get(MenuTable, menu_payload["id"])
        if menu is None:
            session.add(MenuTable(**menu_payload))
            continue
        menu.name = str(menu_payload["name"])


def _upsert_clients(session: Session, client_payloads: list[dict[str, object]]) -> None:
    for client_payload in client_payloads:
        client = session.get(ClientTable, client_payload["client_id"])
        if client is None:
            session.add(ClientTable(**client_payload))
            continue
        client.client_secret = str(client_payload["client_secret"])
        client.grant_type = str(client_payload["grant_type"])
        client.scope = str(client_payload["scope"])


def _upsert_menu_products_from_sources(
    session: Session,
    response_fixtures_path: Path,
    source_payloads: list[dict[str, object]],
) -> None:
    for source_payload in source_payloads:
        menu_name = str(source_payload["menu_name"])
        response_file = str(source_payload["products_response_file"])
        menu = session.scalar(select(MenuTable).where(MenuTable.name == menu_name))
        if menu is None:
            raise RuntimeError(f"Cannot seed products for missing menu: {menu_name}")

        products_payload = _read_json(response_fixtures_path / response_file)
        _upsert_products(session, menu=menu, product_payloads=products_payload["data"])


def _upsert_products(
    session: Session,
    menu: MenuTable,
    product_payloads: list[dict[str, object]],
) -> None:
    for product_payload in product_payloads:
        product = session.get(ProductTable, (product_payload["id"], menu.id))
        if product is None:
            session.add(ProductTable(**product_payload, menu=menu))
            continue
        product.name = str(product_payload["name"])


def assert_database_seeded(session: Session) -> None:
    has_menus = session.scalar(select(MenuTable.id).limit(1)) is not None
    has_products = session.scalar(select(ProductTable.id).limit(1)) is not None
    has_clients = session.scalar(select(ClientTable.client_id).limit(1)) is not None
    if not has_menus or not has_products or not has_clients:
        raise RuntimeError("Database seed data is missing.")


def _read_json(file_path: Path) -> dict[str, list[dict[str, object]]]:
    return json.loads(file_path.read_text())
