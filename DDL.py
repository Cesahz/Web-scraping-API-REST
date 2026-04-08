import sqlite3

conn = sqlite3.connect("books_pipeline.db")
cur = conn.cursor()

#activar clave foranea manualmente en sqlite
cur.execute("PRAGMA foreign_keys = ON")

# ── Tabla categories ──────────────────────────────────────────────────────────
cur.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT UNIQUE   NOT NULL
    )
""")

# ── Tabla authors ─────────────────────────────────────────────────────────────
cur.execute("""
    CREATE TABLE IF NOT EXISTS authors (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        name              TEXT    NOT NULL,
        birth_year        INTEGER,
        country           TEXT,
        external_api_id   TEXT    UNIQUE,
        total_known_works INTEGER,
        api_source        TEXT,
        created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

# ── Tabla books ───────────────────────────────────────────────────────────────
cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        title       TEXT    NOT NULL,
        price       REAL    NOT NULL CHECK (price >= 0),
        rating      INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        category_id INTEGER NOT NULL,
        url         TEXT,
        created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
""")

# ── Tabla book_author (tabla puente N:M) ──────────────────────────────────────
cur.execute("""
    CREATE TABLE IF NOT EXISTS book_author (
        book_id   INTEGER NOT NULL,
        author_id INTEGER NOT NULL,
        PRIMARY KEY (book_id, author_id),
        FOREIGN KEY (book_id)   REFERENCES books(id)   ON DELETE CASCADE,
        FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
    )
""")

conn.commit()
conn.close()
print("Base de datos creada: books_pipeline.db")