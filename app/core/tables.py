from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class MenuTable(Base):
    __tablename__ = "menus"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    products: Mapped[list["ProductTable"]] = relationship(
        back_populates="menu",
        cascade="all, delete-orphan",
    )


class ProductTable(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.id"), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    menu: Mapped[MenuTable] = relationship(back_populates="products")


class ClientTable(Base):
    __tablename__ = "clients"

    client_id: Mapped[str] = mapped_column(String, primary_key=True)
    client_secret: Mapped[str] = mapped_column(String, nullable=False)
    grant_type: Mapped[str] = mapped_column(String, nullable=False)
    scope: Mapped[str] = mapped_column(String, nullable=False)
