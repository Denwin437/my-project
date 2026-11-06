# URL Shortener


A tiny REST API built with Flask and SQLite. Send it a long URL, get back a 6-character short code, and track how many times it has been used.

## Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | `/shorten` | Body `{"url": "https://..."}`, returns `{"code", "short_url"}` |
| GET | `/<code>` | Redirects (302) to the original URL and counts the click |
| GET | `/stats/<code>` | Returns the URL and its click count |

## Run it
```bash
pip install -r requirements.txt
python app.py
```

Try it:
```bash
curl -X POST http://127.0.0.1:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Run the tests
```bash
pytest
```

## What I practiced
REST API design, the Flask application-factory pattern, SQLite with parameterized queries, URL validation, and API testing with Flask's test client.
