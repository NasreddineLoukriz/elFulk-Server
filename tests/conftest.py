"""تهيئة pytest: قاعدة SQLite مؤقتة + عميل اختبار."""

import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="elfulk-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only-1234567890"
os.environ["SEED_EMAIL"] = "parent@elfulk.app"
os.environ["SEED_PASSWORD"] = "Seed123!"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def auth_headers(client, email="parent@elfulk.app", password="Seed123!"):
    """تسجيل دخول مستخدم البذر وإرجاع ترويسة التفويض."""
    response = client.post(
        "/app/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200, response.text
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
