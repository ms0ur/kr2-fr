"""Доступ к данным только через sqlite3, без Django ORM."""
import sqlite3
from contextlib import closing
from datetime import datetime
from functools import wraps
import logging

from django.conf import settings
from django.shortcuts import render

logger = logging.getLogger(__name__)

SORT_OPTIONS = {
    "date": ("s.start_date ASC, s.id ASC", "Сначала ранние"),
    "date_desc": ("s.start_date DESC, s.id ASC", "Сначала поздние"),
    "skaters_desc": ("s.skaters DESC, s.id ASC", "Больше посетителей"),
    "skaters": ("s.skaters ASC, s.id ASC", "Меньше посетителей"),
}
SESSION_SELECT = """
SELECT s.*, r.name AS rink_name, r.capacity, r.rink_kind
FROM skating AS s
JOIN rinks AS r ON r.id = s.rink_id
"""


def query(sql, parameters=()):
    # mode=rw не позволяет случайно создать пустую БД при неверном пути.
    uri = settings.SKATING_DB.resolve().as_uri() + "?mode=rw"
    with closing(sqlite3.connect(uri, uri=True, timeout=5)) as connection:
        connection.row_factory = sqlite3.Row
        rows = [dict(row) for row in connection.execute(sql, parameters).fetchall()]
    # Фильтру date в Django нужен datetime, а SQLite хранит дату как текст.
    for row in rows:
        if "start_date" in row:
            row["start_date"] = datetime.fromisoformat(row["start_date"])
    return rows


def get_sessions(min_skaters=0, sort="date", limit=1000):
    order = SORT_OPTIONS[sort][0]  # Только заранее определённый SQL.
    return query(SESSION_SELECT + " WHERE s.skaters >= ? ORDER BY " + order + " LIMIT ?",
                 (min_skaters, limit))


def get_session(slug):
    rows = query(SESSION_SELECT + " WHERE s.slug = ?", (slug,))
    return rows[0] if rows else None


def get_rinks():
    return query("SELECT id, name, capacity, rink_kind FROM rinks ORDER BY name")


def get_count():
    return query("SELECT COUNT(*) AS total FROM skating")[0]["total"]


def get_statistics(min_count=2):
    return query("""
        SELECT session_kind, COUNT(*) AS total
        FROM skating
        GROUP BY session_kind
        HAVING COUNT(*) >= ?
        ORDER BY total DESC, session_kind
    """, (min_count,))


def database_errors(view):
    """Единая обработка ошибки БД для всех страниц."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except sqlite3.Error:
            logger.exception("Не удалось прочитать базу катков")
            return render(request, "error.html", {
                "message": "Данные временно недоступны. Попробуйте обновить страницу позже."
            }, status=503)
    return wrapped
