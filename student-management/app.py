"""Student Management REST API (FastAPI + SQLite)."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field, field_validator

import db

app = FastAPI(title="Student Management API", version="1.0.0")


class StudentIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=254)
    course: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1, le=8)
    gpa: float = Field(ge=0, le=4)

    @field_validator("name", "course")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v

    @field_validator("email")
    @classmethod
    def _valid_email(cls, v: str) -> str:
        v = v.strip().lower()
        local, _, domain = v.partition("@")
        if not local or "." not in domain or " " in v or domain.startswith(".") or domain.endswith("."):
            raise ValueError("invalid email address")
        return v


class Student(StudentIn):
    id: int


def _conn():
    db.init_db()
    return db.connect()


def _row(row: sqlite3.Row) -> Student:
    return Student(**dict(row))


@app.post("/students", response_model=Student, status_code=201)
def create_student(s: StudentIn) -> Student:
    with closing(_conn()) as conn:
        try:
            cur = conn.execute(
                "INSERT INTO students (name, email, course, year, gpa) VALUES (?, ?, ?, ?, ?)",
                (s.name, s.email, s.course, s.year, s.gpa),
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=409, detail="email already registered") from exc
        return Student(id=cur.lastrowid, **s.model_dump())


@app.get("/students", response_model=list[Student])
def list_students(
    q: Annotated[str | None, Query(max_length=100, description="search name or email")] = None,
    course: str | None = None,
    min_gpa: Annotated[float | None, Query(ge=0, le=4)] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Student]:
    sql, args = "SELECT * FROM students WHERE 1=1", []
    if q:
        escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        like = f"%{escaped}%"
        sql += " AND (name LIKE ? ESCAPE '\\' OR email LIKE ? ESCAPE '\\')"
        args += [like, like]
    if course:
        sql += " AND course = ?"
        args.append(course)
    if min_gpa is not None:
        sql += " AND gpa >= ?"
        args.append(min_gpa)
    sql += " ORDER BY id LIMIT ? OFFSET ?"
    args += [limit, offset]
    with closing(_conn()) as conn:
        return [_row(r) for r in conn.execute(sql, args)]


@app.get("/students/stats")
def stats() -> dict:
    with closing(_conn()) as conn:
        total, avg = conn.execute("SELECT COUNT(*), AVG(gpa) FROM students").fetchone()
        rows = conn.execute("SELECT course, COUNT(*) AS n FROM students GROUP BY course ORDER BY course")
        by_course = {r["course"]: r["n"] for r in rows}
    return {"total": total, "average_gpa": round(avg, 2) if avg is not None else None, "by_course": by_course}


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int) -> Student:
    with closing(_conn()) as conn:
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="student not found")
    return _row(row)


@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, s: StudentIn) -> Student:
    with closing(_conn()) as conn:
        try:
            cur = conn.execute(
                "UPDATE students SET name=?, email=?, course=?, year=?, gpa=? WHERE id=?",
                (s.name, s.email, s.course, s.year, s.gpa, student_id),
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=409, detail="email already registered") from exc
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="student not found")
    return Student(id=student_id, **s.model_dump())


@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int) -> Response:
    with closing(_conn()) as conn:
        cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="student not found")
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
