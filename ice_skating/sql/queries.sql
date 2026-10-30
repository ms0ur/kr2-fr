-- Запросы приложения: те же SELECT выполняются функциями skating/db.py.
-- Параметры ? передаются отдельно в connection.execute(sql, parameters).

-- Список сеансов, JOIN, фильтрация, сортировка и ограничение.
-- Пример параметров: (50, 3).
SELECT s.*, r.name AS rink_name, r.capacity, r.rink_kind
FROM skating AS s
JOIN rinks AS r ON r.id = s.rink_id
WHERE s.skaters >= ?
ORDER BY s.start_date ASC, s.id ASC
LIMIT ?;

-- Другой порядок, допустимый в SORT_OPTIONS: сначала больше посетителей.
SELECT s.*, r.name AS rink_name, r.capacity, r.rink_kind
FROM skating AS s
JOIN rinks AS r ON r.id = s.rink_id
WHERE s.skaters >= ?
ORDER BY s.skaters DESC, s.id ASC
LIMIT ?;

-- Один сеанс по slug. Пример параметров: ('saturday-skate',).
SELECT s.*, r.name AS rink_name, r.capacity, r.rink_kind
FROM skating AS s
JOIN rinks AS r ON r.id = s.rink_id
WHERE s.slug = ?;

-- Катки.
SELECT id, name, capacity, rink_kind FROM rinks ORDER BY name;

-- Актуальное количество сеансов для главной страницы.
SELECT COUNT(*) AS total FROM skating;

-- Статистика: только типы с двумя и более сеансами. Параметры: (2,).
SELECT session_kind, COUNT(*) AS total
FROM skating
GROUP BY session_kind
HAVING COUNT(*) >= ?
ORDER BY total DESC, session_kind;
