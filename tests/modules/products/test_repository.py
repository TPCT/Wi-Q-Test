from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import seed_from_response_files
from app.core.tables import Base, MenuTable
from app.modules.products.models import Product
from app.modules.products.repository import SqlAlchemyProductRepository


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


async def test_lists_products_seeded_from_menu_products_json() -> None:
    session = create_seeded_session()
    repository = SqlAlchemyProductRepository(session=session)

    products = await repository.list_products_for_menu(menu_id=3)

    assert products == [
        Product(id=1, menu_id=3, name="Large Pizza"),
        Product(id=2, menu_id=3, name="Medium Pizza"),
        Product(id=3, menu_id=3, name="Burger"),
        Product(id=4, menu_id=3, name="Chips"),
        Product(id=5, menu_id=3, name="Soup"),
        Product(id=6, menu_id=3, name="Salad"),
    ]


async def test_seeds_products_under_takeaway_menu_relationship() -> None:
    session = create_seeded_session()

    takeaway = session.scalar(select(MenuTable).where(MenuTable.name == "Takeaway"))

    assert takeaway is not None
    assert [product.name for product in takeaway.products] == [
        "Large Pizza",
        "Medium Pizza",
        "Burger",
        "Chips",
        "Soup",
        "Salad",
    ]


async def test_upserts_product_in_database() -> None:
    session = create_seeded_session()
    repository = SqlAlchemyProductRepository(session=session)

    product = await repository.rename_product(menu_id=7, product_id=84, new_name="Chips")
    products = await repository.list_products_for_menu(menu_id=7)

    assert product == Product(id=84, menu_id=7, name="Chips")
    assert products == [Product(id=84, menu_id=7, name="Chips")]
