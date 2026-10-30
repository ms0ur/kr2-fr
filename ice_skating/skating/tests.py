"""Проверки на отдельной временной SQLite: рабочие данные не изменяются."""
import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.http import HttpResponse
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from . import db


class SkatingTests(SimpleTestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "skating.db"
        override = override_settings(SKATING_DB=self.path, DEBUG=False)
        override.enable()
        self.addCleanup(override.disable)
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            for filename in ("schema.sql", "seed.sql"):
                connection.executescript((settings.BASE_DIR / "sql" / filename).read_text())
            connection.commit()

    def execute(self, sql, parameters=()):
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(sql, parameters)
            connection.commit()

    def test_home_and_navigation(self):
        response = self.client.get("/")
        self.assertContains(response, "Всего сеансов: 8.")
        for name in ("homepage:home", "rinks:list", "skating:list", "skating:statistics"):
            self.assertContains(response, f'href="{reverse(name)}"')

    def test_rinks(self):
        response = self.client.get("/rinks/")
        self.assertContains(response, '<article class="card">', count=4)
        self.assertContains(response, "Большой каток")
        self.assertContains(response, "150 человек")
        self.assertContains(response, "Тренировочный")

    def test_sessions_join_templates_and_formats(self):
        response = self.client.get("/skating/")
        self.assertContains(response, '<article class="card">', count=8)
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "skating/includes/skate_card.html")
        for text in ("15.10.2026", "МАССОВОЕ КАТАНИЕ", "Большой каток",
                     "Билеты в кассах", "Лёд открыт", "Сеанс завершён"):
            self.assertContains(response, text)

    def test_filters_produce_different_results(self):
        for minimum, expected in ((50, 4), (100, 2), (999, 0)):
            with self.subTest(minimum=minimum):
                response = self.client.get("/skating/", {"skaters": minimum})
                self.assertContains(response, f"Показано сеансов: {expected}.")
                self.assertContains(response, '<article class="card">', count=expected)
                for session in db.get_sessions(minimum):
                    self.assertContains(response, reverse("skating:detail", args=[session["slug"]]))
                if not expected:
                    self.assertContains(response, "Сеансы не найдены")

    def test_sorting_and_limit(self):
        for sort, expected in (("date", [25, 18]), ("date_desc", [30, 160]),
                               ("skaters", [12, 18]), ("skaters_desc", [160, 120])):
            with self.subTest(sort=sort):
                response = self.client.get("/skating/", {"sort": sort, "limit": 2})
                assert isinstance(response, HttpResponse)
                self.assertContains(response, '<article class="card">', count=2)
                body = response.content.decode()
                positions = [body.index(f'Посетителей: <strong>{number}</strong>')
                             for number in expected]
                self.assertLess(positions[0], positions[1])

    def test_invalid_parameters(self):
        for parameters in ({"skaters": "abc"}, {"skaters": -1}, {"limit": 0},
                           {"limit": 1001}, {"sort": "title; DROP TABLE skating"},
                           {"skaters": "0 OR 1=1"}):
            with self.subTest(parameters=parameters):
                self.assertContains(self.client.get("/skating/", parameters),
                                    "Проверьте параметры", status_code=400)
        self.assertEqual(db.get_count(), 8)

    def test_detail_and_missing_slug(self):
        url = reverse("skating:detail", args=["saturday-skate"])
        self.assertContains(self.client.get("/skating/"), f'href="{url}"')
        response = self.client.get(url)
        for text in ("Субботнее катание", "24.10.2026 11:00", "120 минут",
                     "120 человек", "Большой каток", "150 человек", "массовое катание"):
            self.assertContains(response, text)
        self.assertContains(self.client.get("/skating/missing/"),
                            "Страница не найдена", status_code=404)

    def test_slug_is_a_parameter(self):
        self.assertIsNone(db.get_session("' OR 1=1 --"))

    def test_statistics_and_having_react_to_inserts(self):
        response = self.client.get("/skating/statistics/")
        self.assertContains(response, '<tr><td>Массовое катание</td><td>4</td></tr>', html=True)
        self.assertContains(response, '<tr><td>Тренировка</td><td>3</td></tr>', html=True)
        self.assertNotContains(response, "дискотека на льду")
        for number in (1, 2):
            self.execute("""
                INSERT INTO skating
                    (title, slug, session_kind, start_date, duration, skaters, status, rink_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ("Дополнительная дискотека", f"extra-{number}", "дискотека на льду",
                  "2026-10-26 20:00:00", 60, 50, "запланирован", 4))
        response = self.client.get("/skating/statistics/")
        self.assertContains(response, "Дискотека на льду")
        self.assertContains(response, '<tr><td>Дискотека на льду</td><td>3</td></tr>', html=True)
        self.assertContains(self.client.get("/"), "Всего сеансов: 10.")

    def test_rink_update_is_visible_without_restart(self):
        self.execute("UPDATE rinks SET name = ?, capacity = ? WHERE id = ?",
                     ("Обновлённая арена", 170, 1))
        for url in ("/rinks/", "/skating/", "/skating/saturday-skate/"):
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), "Обновлённая арена")
                self.assertContains(self.client.get(url), "170 человек")

    def test_empty_database(self):
        self.execute("DELETE FROM skating")
        self.execute("DELETE FROM rinks")
        for url, text in (("/", "Всего сеансов: 0."), ("/rinks/", "Катки пока не добавлены"),
                          ("/skating/", "Сеансы не найдены"),
                          ("/skating/statistics/", "Нет типов с нужным количеством сеансов")):
            self.assertContains(self.client.get(url), text)

    def test_database_failure_is_handled_on_every_page(self):
        self.path.unlink()
        for url in ("/", "/rinks/", "/skating/", "/skating/statistics/",
                    "/skating/saturday-skate/"):
            with self.subTest(url=url), self.assertLogs("skating.db", level="ERROR"):
                response = self.client.get(url)
                self.assertContains(response, "Данные временно недоступны", status_code=503)
                self.assertNotContains(response, "Traceback", status_code=503)
                self.assertNotContains(response, str(self.path), status_code=503)
        self.assertFalse(self.path.exists())

    def test_database_constraints(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.execute("UPDATE skating SET rink_id = ? WHERE id = ?", (999, 1))
        with self.assertRaises(sqlite3.IntegrityError):
            self.execute("UPDATE skating SET slug = ? WHERE id = ?", ("saturday-skate", 1))
