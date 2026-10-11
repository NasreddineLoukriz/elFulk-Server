"""اختبارات عقد API مقابل ما يتوقعه تطبيق Flutter."""

import re

from .conftest import auth_headers

DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")


def test_register_then_login(client):
    response = client.post(
        "/app/auth/register",
        json={
            "user_name": "أمينة",
            "email": "amina@elfulk.app",
            "password": "Secret123",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert set(body) == {"token", "userName", "email"}
    assert body["userName"] == "أمينة"

    login = client.post(
        "/app/auth/login",
        json={"email": "amina@elfulk.app", "password": "Secret123"},
    )
    assert login.status_code == 200
    assert login.json()["email"] == "amina@elfulk.app"


def test_register_duplicate_email_conflicts(client):
    response = client.post(
        "/app/auth/register",
        json={"email": "parent@elfulk.app", "password": "Secret123"},
    )
    assert response.status_code == 409
    assert "detail" in response.json()


def test_login_wrong_password_is_unauthorized(client):
    response = client.post(
        "/app/auth/login",
        json={"email": "parent@elfulk.app", "password": "wrong"},
    )
    assert response.status_code == 401


def test_protected_routes_require_token(client):
    for path in ("/parent/home", "/parent/requests", "/child/home"):
        assert client.get(path).status_code == 401


def test_overviews_match_flutter_contract(client):
    headers = auth_headers(client)

    app_home = client.get("/app/home").json()
    assert set(app_home) >= {
        "headline",
        "summary",
        "base_url",
        "endpoint",
        "principles",
        "modules",
        "next_milestones",
    }

    parent_home = client.get("/parent/home", headers=headers).json()
    assert set(parent_home) >= {
        "title",
        "summary",
        "base_url",
        "endpoint",
        "highlights",
        "next_actions",
    }

    child_home = client.get("/child/home", headers=headers).json()
    assert set(child_home) >= {
        "title",
        "summary",
        "base_url",
        "endpoint",
        "tasks",
        "tips",
    }


def test_requests_crud_flow(client):
    headers = auth_headers(client)

    listing = client.get("/parent/requests", headers=headers).json()
    assert {r["id"] for r in listing["requests"]} >= {
        "req_001",
        "req_002",
        "req_003",
    }
    first = listing["requests"][0]
    assert set(first) == {
        "id",
        "child_name",
        "request_type",
        "status",
        "requested_at",
        "note",
    }
    assert DATETIME_RE.match(first["requested_at"])

    created = client.post(
        "/parent/requests",
        headers=headers,
        json={
            "child_name": "ليان",
            "request_type": "وقت إضافي للقراءة",
            "note": "تريد إنهاء قصة قبل النوم.",
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["status"] == "pending"
    assert DATETIME_RE.match(created.json()["requested_at"])
    new_id = created.json()["id"]

    bad = client.post(
        "/parent/requests",
        headers=headers,
        json={"child_name": "ليان", "request_type": "", "note": "x"},
    )
    assert bad.status_code == 400

    patched = client.patch(
        f"/parent/requests/{new_id}",
        headers=headers,
        json={"status": "approved", "review_note": "تمت الموافقة."},
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "approved"
    assert patched.json()["note"] == "تمت الموافقة."

    missing = client.patch(
        "/parent/requests/req_999",
        headers=headers,
        json={"status": "approved", "review_note": ""},
    )
    assert missing.status_code == 404

    empty_status = client.patch(
        f"/parent/requests/{new_id}",
        headers=headers,
        json={"status": "  ", "review_note": ""},
    )
    assert empty_status.status_code == 400
