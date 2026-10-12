"""Небольшой CRUD-сервис заметок поверх PostgreSQL."""

import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel, Field


def build_conninfo() -> str:
    return (
        f"host={os.environ.get('DB_HOST', 'db')} "
        f"port={os.environ.get('DB_PORT', '5432')} "
        f"dbname={os.environ['POSTGRES_DB']} "
        f"user={os.environ['POSTGRES_USER']} "
        f"password={os.environ['POSTGRES_PASSWORD']}"
    )


pool: ConnectionPool | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global pool
    pool = ConnectionPool(
        build_conninfo(),
        min_size=1,
        max_size=5,
        kwargs={"row_factory": dict_row},
        # проверять соединение перед выдачей: переживаем перезапуск БД
        check=ConnectionPool.check_connection,
        open=False,
    )
    pool.open(wait=True, timeout=30)
    yield
    pool.close()


app = FastAPI(title="Notes service", lifespan=lifespan)


class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = ""


class NoteOut(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime


@app.get("/health")
def health():
    try:
        with pool.connection() as conn:
            conn.execute("SELECT 1")
    except Exception:  # noqa: BLE001
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "database unavailable")
    return {"status": "ok", "db": "ok"}


@app.post("/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteIn):
    with pool.connection() as conn:
        return conn.execute(
            "INSERT INTO notes (title, body) VALUES (%s, %s) "
            "RETURNING id, title, body, created_at",
            (note.title, note.body),
        ).fetchone()


@app.get("/notes", response_model=list[NoteOut])
def list_notes():
    with pool.connection() as conn:
        return conn.execute(
            "SELECT id, title, body, created_at FROM notes ORDER BY id"
        ).fetchall()


@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int):
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT id, title, body, created_at FROM notes WHERE id = %s",
            (note_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "note not found")
    return row


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    with pool.connection() as conn:
        deleted = conn.execute("DELETE FROM notes WHERE id = %s", (note_id,)).rowcount
    if deleted == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "note not found")
