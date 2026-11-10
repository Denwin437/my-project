# Student Management API

A REST API for managing student records, built with FastAPI and SQLite. Supports full CRUD, search, filtering, pagination and summary statistics, with strict input validation.

## Features
- Create, read, update and delete students
- Search by name or email (wildcard characters are matched literally)
- Filter by course and minimum GPA, with `limit` / `offset` pagination
- Summary statistics: total, average GPA and students per course
- Emails are normalised to lowercase and must be unique (`409` on duplicates)
- Validation: year 1-8, GPA 0-4, non-blank name and course, valid email shape (`422` otherwise)
- Parameterized SQL everywhere; the server binds to `127.0.0.1` by default
- Interactive API docs at `/docs`

## Setup and run
```bash
pip install -r requirements.txt
python app.py            # http://127.0.0.1:8000  (docs at /docs)
```
The database file defaults to `students.db` in the current folder. Set `STUDENTS_DB=/path/to/file.db` to change it.

## Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/students` | Create a student |
| GET | `/students` | List (`q`, `course`, `min_gpa`, `limit`, `offset`) |
| GET | `/students/stats` | Totals and averages |
| GET | `/students/{id}` | Get one student |
| PUT | `/students/{id}` | Replace a student |
| DELETE | `/students/{id}` | Delete a student |

```bash
curl -X POST http://127.0.0.1:8000/students -H 'content-type: application/json' \
  -d '{"name":"Asha Rao","email":"asha@example.com","course":"CS","year":2,"gpa":3.5}'
curl "http://127.0.0.1:8000/students?course=CS&min_gpa=3"
```

## Run the tests
```bash
pip install -r requirements.txt pytest
pytest
```
18 tests cover CRUD, validation, duplicates, search and filters, wildcard handling, an SQL-injection attempt and statistics. Each test uses its own temporary database.

## Known limitations
- No authentication: it is meant to run locally or behind your own access control.
- `PUT` replaces the whole record; there is no partial `PATCH`.
- SQLite is single-file storage and not suited to heavy concurrent writes.
