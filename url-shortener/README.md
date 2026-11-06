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
python app.py          # listens on 127.0.0.1 only, debug mode off
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

## Security notes
- The server binds to `127.0.0.1` and debug mode is off unless you set `FLASK_DEBUG=1`.
- Only `http` and `https` URLs are accepted, and all SQL uses parameterized queries.
- There is no authentication or rate limiting yet, so put it behind a proper web server and limiter before exposing it publicly.
