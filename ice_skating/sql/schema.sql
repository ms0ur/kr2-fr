CREATE TABLE rinks (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    rink_kind TEXT NOT NULL
);
CREATE TABLE skating (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    session_kind TEXT NOT NULL,
    start_date TEXT NOT NULL,
    duration INTEGER NOT NULL CHECK (duration > 0),
    skaters INTEGER NOT NULL CHECK (skaters >= 0),
    status TEXT NOT NULL CHECK (status IN ('запланирован', 'идёт', 'завершён')),
    rink_id INTEGER NOT NULL REFERENCES rinks(id)
);
