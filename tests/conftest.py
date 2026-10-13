import pytest
from fastapi.testclient import TestClient

from changeshield.api import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(str(tmp_path / "test.sqlite3"))) as c:
        yield c


@pytest.fixture
def tokens():
    return {
        role: {"Authorization": f"Bearer local-{role}-token"}
        for role in ("viewer", "analyst", "admin")
    }
