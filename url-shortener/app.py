"""URL Shortener: a small Flask + SQLite REST service."""

import os
import secrets
import sqlite3
import string
from urllib.parse import urlparse

from flask import Flask, g, jsonify, redirect, request

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def create_app(db_path: str = None) -> Flask:
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or os.environ.get("DB_PATH", "urls.db")

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    with app.app_context():
        get_db().execute(
            "CREATE TABLE IF NOT EXISTS urls ("
            "code TEXT PRIMARY KEY, url TEXT NOT NULL, clicks INTEGER NOT NULL DEFAULT 0)"
        )
        get_db().commit()

    def new_code() -> str:
        db = get_db()
        while True:
            code = "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
            if db.execute("SELECT 1 FROM urls WHERE code = ?", (code,)).fetchone() is None:
                return code

    @app.post("/shorten")
    def shorten():
        data = request.get_json(silent=True) or {}
        url = data.get("url", "")
        if not is_valid_url(url):
            return jsonify(error="A valid http(s) URL is required"), 400
        db = get_db()
        code = new_code()
        db.execute("INSERT INTO urls (code, url) VALUES (?, ?)", (code, url))
        db.commit()
        return jsonify(code=code, short_url=request.host_url + code), 201

    @app.get("/<code>")
    def follow(code):
        db = get_db()
        row = db.execute("SELECT url FROM urls WHERE code = ?", (code,)).fetchone()
        if row is None:
            return jsonify(error="Unknown short code"), 404
        db.execute("UPDATE urls SET clicks = clicks + 1 WHERE code = ?", (code,))
        db.commit()
        return redirect(row["url"], code=302)

    @app.get("/stats/<code>")
    def stats(code):
        row = get_db().execute("SELECT url, clicks FROM urls WHERE code = ?", (code,)).fetchone()
        if row is None:
            return jsonify(error="Unknown short code"), 404
        return jsonify(code=code, url=row["url"], clicks=row["clicks"])

    return app


if __name__ == "__main__":
    # Debug mode lets anyone who can reach the server run code on it, so it is OFF by default.
    # Enable it only on your own machine with: FLASK_DEBUG=1 python app.py
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    create_app().run(host="127.0.0.1", debug=debug)
