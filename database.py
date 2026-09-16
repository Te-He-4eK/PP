import sqlite3


def create_database():
    connection = sqlite3.connect("database.db")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            about TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT
        )
    """)

    # Проверяем старую таблицу пользователей.
    # Если поля about ещё нет, добавляем его.
    user_columns = connection.execute(
        "PRAGMA table_info(users)"
    ).fetchall()

    user_column_names = [column[1] for column in user_columns]

    if "about" not in user_column_names:
        connection.execute(
            "ALTER TABLE users ADD COLUMN about TEXT"
        )

    # То же самое делаем для даты публикации.
    post_columns = connection.execute(
        "PRAGMA table_info(posts)"
    ).fetchall()

    post_column_names = [column[1] for column in post_columns]

    if "created_at" not in post_column_names:
        connection.execute(
            "ALTER TABLE posts ADD COLUMN created_at TEXT"
        )

    connection.commit()
    connection.close()