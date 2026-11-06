import pytest

from app import create_app, is_valid_url


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    return app.test_client()


def test_is_valid_url():
    assert is_valid_url("https://example.com/path")
    assert not is_valid_url("ftp://example.com")
    assert not is_valid_url("not a url")


def test_shorten_and_redirect(client):
    res = client.post("/shorten", json={"url": "https://example.com"})
    assert res.status_code == 201
    code = res.get_json()["code"]
    assert len(code) == 6

    redirect_res = client.get(f"/{code}")
    assert redirect_res.status_code == 302
    assert redirect_res.headers["Location"] == "https://example.com"


def test_stats_count_clicks(client):
    code = client.post("/shorten", json={"url": "https://example.com"}).get_json()["code"]
    client.get(f"/{code}")
    client.get(f"/{code}")
    data = client.get(f"/stats/{code}").get_json()
    assert data["clicks"] == 2
    assert data["url"] == "https://example.com"


def test_invalid_url_rejected(client):
    assert client.post("/shorten", json={"url": "nope"}).status_code == 400
    assert client.post("/shorten", data="garbage").status_code == 400


def test_unknown_code(client):
    assert client.get("/doesnotexist").status_code == 404
    assert client.get("/stats/doesnotexist").status_code == 404
