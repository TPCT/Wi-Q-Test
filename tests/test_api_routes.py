import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.main import create_app
from app.modules.auth.dependencies import get_auth_service
from app.modules.auth.models import AccessToken
from app.modules.menus.dependencies import get_menu_service
from app.modules.menus.models import Menu
from app.modules.products.dependencies import get_product_service
from app.modules.products.models import Product

RESPONSES_PATH = Path(__file__).resolve().parent.parent / "responses"


def create_test_token(grant_type: str = "client_credentials") -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": "1337",
            "client_id": "1337",
            "grant_type": grant_type,
            "scope": ["catalogue"],
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


AUTH_HEADER = {"Authorization": f"Bearer {create_test_token()}"}


def read_response_fixture(file_name: str) -> dict[str, object]:
    return json.loads((RESPONSES_PATH / file_name).read_text())


class MenuServiceStub:
    async def list_menus(self) -> list[Menu]:
        menus_payload = read_response_fixture("menus.json")
        return [Menu.model_validate(menu) for menu in menus_payload["data"]]


class ProductServiceStub:
    async def list_for_menu(self, menu_id: int) -> list[Product]:
        assert menu_id == 3
        products_payload = read_response_fixture("menu-products.json")
        return [
            Product.model_validate({**product, "menu_id": 3})
            for product in products_payload["data"]
        ]

    async def rename_product(self, menu_id: int, product_id: int, new_name: str) -> Product:
        assert menu_id == 7
        assert product_id == 84
        assert new_name == "Chips"
        return Product(id=84, menu_id=7, name="Chips")


class AuthServiceStub:
    async def create_access_token(
        self,
        client_id: str,
        client_secret: str,
        grant_type: str,
    ) -> AccessToken:
        return AccessToken(
            access_token=create_test_token(grant_type=grant_type),
            expires_in=3600,
            token_type="Bearer",
            scope=["catalogue"],
        )


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    app = create_app()
    app.dependency_overrides[get_auth_service] = AuthServiceStub
    app.dependency_overrides[get_menu_service] = MenuServiceStub
    app.dependency_overrides[get_product_service] = ProductServiceStub
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client


async def test_list_menus_route(client: AsyncClient) -> None:
    response = await client.get("/menus", headers=AUTH_HEADER)
    menus_payload = read_response_fixture("menus.json")

    assert response.status_code == 200
    assert response.json() == menus_payload


async def test_create_auth_token_route(client: AsyncClient) -> None:
    response = await client.post(
        "/auth_token",
        data={
            "client_secret": "4j3g4gj304gj3",
            "client_id": "1337",
            "grant_type": "client_credentials",
        },
    )

    assert response.status_code == 200
    token_payload = read_response_fixture("token.json")
    assert set(response.json()) == set(token_payload)
    assert response.json() == {
        "access_token": response.json()["access_token"],
        "expires_in": 3600,
        "token_type": "Bearer",
        "scope": ["catalogue"],
    }
    claims = jwt.decode(
        response.json()["access_token"],
        get_settings().jwt_secret,
        algorithms=[get_settings().jwt_algorithm],
    )
    assert claims["grant_type"] == "client_credentials"
    assert claims["client_id"] == "1337"
    assert claims["scope"] == ["catalogue"]


async def test_protected_routes_require_authorization(client: AsyncClient) -> None:
    response = await client.get("/menus")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


async def test_protected_routes_reject_wrong_grant_type(client: AsyncClient) -> None:
    response = await client.get(
        "/menus",
        headers={"Authorization": f"Bearer {create_test_token(grant_type='password')}"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Unsupported token grant type"}


async def test_list_products_for_menu_route(client: AsyncClient) -> None:
    response = await client.get("/menu/3/products", headers=AUTH_HEADER)
    products_payload = read_response_fixture("menu-products.json")

    assert response.status_code == 200
    assert response.json() == products_payload


async def test_rename_product_route(client: AsyncClient) -> None:
    response = await client.put(
        "/menu/7/product/84",
        json={"name": "Chips"},
        headers=AUTH_HEADER,
    )

    assert response.status_code == 200
    assert response.json() == {"data": {"id": 84, "name": "Chips"}}
