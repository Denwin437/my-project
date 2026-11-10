import importlib
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDENTS_DB", str(tmp_path / "t.db"))
    import db

    importlib.reload(db)
    import app as app_module

    importlib.reload(app_module)
    return TestClient(app_module.app)


def make(**over):
    base = {"name": "Asha Rao", "email": "asha@example.com", "course": "CS", "year": 2, "gpa": 3.5}
    base.update(over)
    return base


def test_create_and_get(client):
    r = client.post("/students", json=make())
    assert r.status_code == 201
    sid = r.json()["id"]
    assert client.get(f"/students/{sid}").json()["email"] == "asha@example.com"


def test_email_normalised_and_unique(client):
    client.post("/students", json=make(email="  ASHA@Example.com "))
    r = client.post("/students", json=make(email="asha@example.com", name="Other"))
    assert r.status_code == 409


@pytest.mark.parametrize(
    "bad",
    [
        {"name": "   "},
        {"email": "not-an-email"},
        {"email": "a@b"},
        {"year": 0},
        {"year": 9},
        {"gpa": 4.5},
        {"gpa": -1},
        {"course": ""},
    ],
)
def test_validation_rejects_bad_input(client, bad):
    assert client.post("/students", json=make(**bad)).status_code == 422


def test_get_missing_is_404(client):
    assert client.get("/students/999").status_code == 404


def test_update(client):
    sid = client.post("/students", json=make()).json()["id"]
    r = client.put(f"/students/{sid}", json=make(gpa=3.9, course="Math"))
    assert r.status_code == 200 and r.json()["gpa"] == 3.9
    assert client.get(f"/students/{sid}").json()["course"] == "Math"


def test_update_missing_and_conflict(client):
    assert client.put("/students/5", json=make()).status_code == 404
    client.post("/students", json=make())
    sid2 = client.post("/students", json=make(email="b@example.com")).json()["id"]
    assert client.put(f"/students/{sid2}", json=make(email="asha@example.com")).status_code == 409


def test_delete(client):
    sid = client.post("/students", json=make()).json()["id"]
    assert client.delete(f"/students/{sid}").status_code == 204
    assert client.delete(f"/students/{sid}").status_code == 404
    assert client.get(f"/students/{sid}").status_code == 404


def test_search_filter_paginate(client):
    client.post("/students", json=make())
    client.post("/students", json=make(name="Bo Lin", email="bo@example.com", course="Math", gpa=2.0))
    client.post("/students", json=make(name="Cy Dee", email="cy@example.com", course="CS", gpa=3.9))
    assert len(client.get("/students").json()) == 3
    assert [s["name"] for s in client.get("/students?q=bo").json()] == ["Bo Lin"]
    assert len(client.get("/students?course=CS").json()) == 2
    assert [s["name"] for s in client.get("/students?min_gpa=3.6").json()] == ["Cy Dee"]
    assert len(client.get("/students?limit=1&offset=1").json()) == 1
    assert client.get("/students?limit=0").status_code == 422


def test_search_treats_wildcards_literally(client):
    client.post("/students", json=make(name="Ann_B", email="ann@example.com"))
    client.post("/students", json=make(name="AnnXB", email="annx@example.com"))
    client.post("/students", json=make(name="100% Pass", email="p@example.com"))
    assert [s["name"] for s in client.get("/students", params={"q": "ann_b"}).json()] == ["Ann_B"]
    assert [s["name"] for s in client.get("/students", params={"q": "%"}).json()] == ["100% Pass"]


def test_sql_injection_attempt_is_harmless(client):
    client.post("/students", json=make())
    r = client.get("/students", params={"course": "x' OR '1'='1"})
    assert r.json() == []
    assert len(client.get("/students").json()) == 1


def test_stats(client):
    assert client.get("/students/stats").json() == {"total": 0, "average_gpa": None, "by_course": {}}
    client.post("/students", json=make(gpa=3.0))
    client.post("/students", json=make(email="b@example.com", gpa=4.0, course="Math"))
    s = client.get("/students/stats").json()
    assert s == {"total": 2, "average_gpa": 3.5, "by_course": {"CS": 1, "Math": 1}}
