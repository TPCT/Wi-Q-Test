import json
import os
from collections.abc import Iterator
from pathlib import Path

import pytest

os.environ["DATABASE_PATH"] = ":memory:"
os.environ["RESPONSE_FIXTURES_PATH"] = "responses"
os.environ["JWT_SECRET"] = "test-secret-with-at-least-thirty-two-bytes"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRES_SECONDS"] = "3600"


@pytest.fixture
def response_payloads() -> Iterator[dict[str, dict]]:
    responses_path = Path(__file__).resolve().parent.parent / "responses"
    yield {
        "token": json.loads((responses_path / "token.json").read_text()),
        "menus": json.loads((responses_path / "menus.json").read_text()),
        "products": json.loads((responses_path / "menu-products.json").read_text()),
    }
