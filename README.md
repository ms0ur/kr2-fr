# Контрольная работа № 2

Django-приложение: 4 катка, 8 сеансов, фильтрация, сортировка,
страницы сеансов и статистика. Данные читаются через стандартный `sqlite3`.
Django ORM не используется. Дополнительные библиотеки, кроме Django, не нужны.

Ответы на 30 теоретических вопросов находятся в
[docs/theory_answers.md](docs/theory_answers.md). Документ и все примеры
сохранены без изменений относительно исходного файла. Раздел об ORM нужен
для теории; в самом приложении работа с данными реализована через sqlite3.

Настройки в `pyproject.toml` указывают анализаторам Python корень импортов
`ice_skating` (папку с `manage.py`) и окружение `.venv`. Поэтому импорт
`from skating import db` обращается к соседнему Django-приложению.
Для Pyright выбран режим `basic`: он проверяет ошибки импортов и типов,
но не требует обязательных аннотаций у каждой функции учебного проекта.
Настройки соответствуют документации [Pyright](https://github.com/microsoft/pyright/blob/main/docs/configuration.md)
и [ty](https://docs.astral.sh/ty/reference/configuration/#root).
Заменять его на `from .skating import db` нельзя: внутри `homepage` нет `skating`.
Файлы `__init__.py` могут быть пустыми: они обозначают пакеты Python.
Файлы `models.py` и `admin.py` удалены: ORM по заданию не используется,
админка не требуется. Django работает без этих файлов.
Проверки всех приложений собраны в `skating/tests.py`.

## Запуск

Команды выполняются из корня репозитория:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cd ice_skating
python manage.py check
python manage.py runserver --insecure
```

Открыть <http://127.0.0.1:8000/>. Остановить сервер: Ctrl+C.
Если окружение `.venv` уже настроено, достаточно его активировать.

База `ice_skating/data/skating.db` уже включена в проект. Если её нет,
перед запуском выполните `python manage.py initdb` из папки `ice_skating`.
Команда создаёт таблицы из `sql/schema.sql` и данные из `sql/seed.sql`.
Существующую БД она не перезаписывает. Выполнять `migrate` не требуется.

## Где смотреть реализацию

| Требование | Файл внутри ice_skating |
| --- | --- |
| Настройки, общие маршруты | `ice_skating/settings.py`, `ice_skating/urls.py` |
| Соединение, execute, параметры, закрытие соединения | `skating/db.py` |
| SQL, структура и тестовые данные | `sql/queries.sql`, `sql/schema.sql`, `sql/seed.sql` |
| Главная и актуальное количество | `homepage/views.py`, `homepage/templates/homepage/home.html` |
| Катки | `rinks/views.py`, `rinks/templates/rinks/rink_list.html` |
| GET, сортировка, лимит, сеанс, статистика | `skating/views.py` |
| Именованные маршруты и slug | `skating/urls.py` |
| Общий интерфейс, подключение статики | `templates/base.html` |
| Цикл и include | `skating/templates/skating/skate_list.html` |
| Карточка и условия статуса | `skating/templates/skating/includes/` |
| Статистика | `skating/templates/skating/statistics.html` |
| Ошибки 404 и БД | `templates/404.html`, `templates/error.html`, декоратор `database_errors` |
| Оформление и интерактивность | `static/css/style.css`, `static/js/main.js`, `static/img/logo.png` |

Полный путь данных: view вызывает функцию из `skating/db.py` → SQL выполняется
через `sqlite3.Connection.execute(sql, parameters)` → строки преобразуются в
словари → view передаёт их в context → шаблон выводит значения. Даты из SQLite
преобразуются в `datetime`, чтобы работал фильтр `date`.

`queries.sql` хранит запросы для просмотра; рабочие запросы выполняются в `db.py`.
Пользовательские числа и slug передаются через `?`. SQL для сортировки выбирается
из словаря `SORT_OPTIONS`. Новое соединение для каждого запроса обеспечивает
актуальность данных, `closing` гарантирует его закрытие.

Используются фильтры `date`, `default`, `length`, `upper`, `truncatechars`,
`capfirst`. JavaScript показывает и скрывает сведения о катке в карточках;
без JavaScript эти сведения остаются видимыми.

## Проверка

Из папки `ice_skating`:

```bash
python manage.py check
python manage.py test skating -v 2
```

13 тестов используют отдельную временную SQLite и проверяют страницы, JOIN,
фильтрацию, сортировку, LIMIT, неверные параметры, slug, 404, пустую БД,
ошибки БД, обновление катка и изменение COUNT/GROUP BY/HAVING после добавления
сеансов. Рабочая база при тестировании не изменяется.

## Демонстрация в браузере

1. Главная: название, описание, «Всего сеансов: 8», ссылки.
2. «Катки»: четыре катка с вместимостью и типом.
3. «Сеансы»: восемь карточек, связанные катки, три разных статуса,
   дата в формате `15.10.2026`, типы в верхнем регистре.
4. Фильтр `skaters=50`: четыре результата; `skaters=100`: два;
   `skaters=999`: сообщение об отсутствии результатов.
5. `http://127.0.0.1:8000/skating/?sort=skaters_desc&limit=2`:
   «Неоновая ночь» (160) и «Субботнее катание» (120).
   Выберите другой порядок и лимит через форму.
6. Перейдите по ссылке «Субботнее катание»:
   `/skating/saturday-skate/`, затем вернитесь к списку.
7. Откройте `/skating/missing/`: понятная страница 404.
   `/skating/?skaters=abc`: понятная ошибка параметра, HTTP 400.
8. `/skating/statistics/`: массовое катание — 4, тренировка — 3.
   Дискотека пока не отображается: один сеанс не проходит `HAVING COUNT(*) >= 2`.
9. В карточке нажмите «Подробнее о катке», затем «Скрыть сведения».

### SQL и изменение данных без перезапуска

Оставьте сервер работающим. Во втором терминале из папки `ice_skating`
запустите `python`, затем выполните следующие команды. Используется Python
sqlite3; отдельная утилита sqlite3 не требуется.

```python
import sqlite3
db = sqlite3.connect("data/skating.db")
db.execute("PRAGMA foreign_keys = ON")

# Результат (4, 8).
print(db.execute("SELECT (SELECT COUNT(*) FROM rinks), COUNT(*) FROM skating").fetchone())

# Сравнить с /skating/?skaters=50&limit=3 : 55, 95, 120 посетителей.
print(db.execute("""
    SELECT s.title, s.skaters, r.name
    FROM skating s JOIN rinks r ON r.id = s.rink_id
    WHERE s.skaters >= ? ORDER BY s.start_date, s.id LIMIT ?
""", (50, 3)).fetchall())

# Сравнить с /skating/saturday-skate/.
print(db.execute("""
    SELECT s.*, r.name, r.capacity, r.rink_kind
    FROM skating s JOIN rinks r ON r.id = s.rink_id WHERE s.slug = ?
""", ("saturday-skate",)).fetchone())

# Сравнить с /rinks/ и /skating/statistics/.
print(db.execute("SELECT id, name, capacity, rink_kind FROM rinks ORDER BY name").fetchall())
print(db.execute("""
    SELECT session_kind, COUNT(*) FROM skating
    GROUP BY session_kind HAVING COUNT(*) >= ?
    ORDER BY COUNT(*) DESC, session_kind
""", (2,)).fetchall())

# Изменение катка: обновите /rinks/, список и страницу сеанса.
db.execute("UPDATE rinks SET name = ? WHERE id = ?", ("Большой каток — обновлён", 1))
db.commit()

# Добавить два сеанса: обновите главную и статистику.
for n in (1, 2):
    db.execute("""
        INSERT INTO skating
            (title, slug, session_kind, start_date, duration, skaters, status, rink_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (f"Демо-дискотека {n}", f"demo-disco-{n}", "дискотека на льду",
          "2026-10-26 20:00:00", 60, 50, "запланирован", 4))

db.commit()
# На главной теперь 10, в статистике появилась дискотека — 3.
print(db.execute("""
    SELECT session_kind, COUNT(*) FROM skating
    GROUP BY session_kind HAVING COUNT(*) >= ?
    ORDER BY COUNT(*) DESC, session_kind
""", (2,)).fetchall())

# После демонстрации вернуть исходные данные.
db.execute("UPDATE rinks SET name = ? WHERE id = ?", ("Большой каток", 1))
db.execute("DELETE FROM skating WHERE slug IN (?, ?)", ("demo-disco-1", "demo-disco-2"))
db.commit()
db.close()
```

### Демонстрация ошибки БД

Во втором терминале из папки `ice_skating` временно переименуйте файл:

```bash
mv data/skating.db data/skating.db.backup
```

Обновите любую страницу: HTTP 503 и сообщение «Данные временно недоступны».
В браузере нет traceback и технических подробностей; исключение записывается
только в журнал сервера. Верните базу и обновите страницу:

```bash
mv data/skating.db.backup data/skating.db
```
