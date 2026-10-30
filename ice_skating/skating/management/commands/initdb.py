import sqlite3
from contextlib import closing
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Создать SQLite и добавить 4 катка и 8 сеансов (только если БД ещё нет)."

    def handle(self, *args, **options):
        path = settings.SKATING_DB
        if path.exists():
            raise CommandError("База уже существует. Существующие данные сохранены.")
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with closing(sqlite3.connect(path)) as connection:
                connection.execute("PRAGMA foreign_keys = ON")
                for filename in ("schema.sql", "seed.sql"):
                    connection.executescript((settings.BASE_DIR / "sql" / filename).read_text())
                connection.commit()
        except sqlite3.Error as error:
            path.unlink(missing_ok=True)
            raise CommandError(str(error)) from error
        self.stdout.write("Создана база: 4 катка, 8 сеансов.")
