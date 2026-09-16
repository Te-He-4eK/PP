import sqlite3
from flask import Flask, request, session, redirect
from datetime import datetime

app = Flask(__name__)

app.secret_key = "secret_key"


STYLE = """
<style>
    body {
        font-family: Arial, sans-serif;
        max-width: 700px;
        margin: 40px auto;
        padding: 20px;
    }

    a {
        color: #3366cc;
        margin-right: 10px;
    }

    input, textarea {
        padding: 8px;
        width: 300px;
    }

    button {
        padding: 8px 15px;
        cursor: pointer;
    }

    .post {
        border: 1px solid #cccccc;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 5px;
    }

    .post-date {
        font-size: 13px;
        color: #777777;
        margin-top: 10px;
    }

    .profile-info {
        border: 1px solid #cccccc;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 5px;
    }
</style>
"""


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

    # Проверяем таблицу пользователей
    user_columns = connection.execute(
        "PRAGMA table_info(users)"
    ).fetchall()

    user_column_names = [
        column[1] for column in user_columns
    ]

    # Добавляем поле "О себе" в старую базу
    if "about" not in user_column_names:
        connection.execute(
            "ALTER TABLE users ADD COLUMN about TEXT"
        )

    # Проверяем таблицу публикаций
    post_columns = connection.execute(
        "PRAGMA table_info(posts)"
    ).fetchall()

    post_column_names = [
        column[1] for column in post_columns
    ]

    if "created_at" not in post_column_names:
        connection.execute(
            "ALTER TABLE posts ADD COLUMN created_at TEXT"
        )

    connection.commit()
    connection.close()


@app.route("/")
def index():
    connection = sqlite3.connect("database.db")

    posts = connection.execute(
        "SELECT * FROM posts ORDER BY id DESC"
    ).fetchall()

    connection.close()

    posts_count = len(posts)

    posts_html = ""

    for post in posts:
        created_at = post[3]

        if created_at is None:
            created_at = "Дата не указана"

        posts_html += f"""
            <div class="post">

                <a href="/profile/{post[1]}">
                    <b>{post[1]}</b>
                </a>

                <p>{post[2]}</p>

                <div class="post-date">
                    Опубликовано: {created_at}
                </div>

            </div>
        """

    if not posts:
        posts_html = "<p>Пока нет публикаций.</p>"

    if "username" in session:
        return f"""
            {STYLE}

            <h1>Общая лента</h1>

            <p>
                Вы вошли как:
                <b>{session["username"]}</b>
            </p>

            <a href="/profile/{session["username"]}">
                Мой профиль
            </a>

            <a href="/create_post">
                Добавить пост
            </a>

            <a href="/my_posts">
                Мои публикации
            </a>

            <br><br>

            <a href="/logout">
                Выйти
            </a>

            <hr>

            <h2>Публикации</h2>

            <p>
                Всего публикаций:
                <b>{posts_count}</b>
            </p>

            {posts_html}
        """

    return f"""
        {STYLE}

        <h1>Общая лента</h1>

        <a href="/register">
            Регистрация
        </a>

        <a href="/login">
            Вход
        </a>

        <hr>

        <h2>Публикации</h2>

        <p>
            Всего публикаций:
            <b>{posts_count}</b>
        </p>

        {posts_html}
    """


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if username == "" or password == "":
            return f"""
                {STYLE}

                <h2>
                    Логин и пароль не могут быть пустыми
                </h2>

                <a href="/register">
                    Вернуться к регистрации
                </a>
            """

        connection = sqlite3.connect("database.db")

        existing_user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing_user:
            connection.close()

            return f"""
                {STYLE}

                <h2>
                    Пользователь с таким именем уже существует
                </h2>

                <a href="/register">
                    Выбрать другой логин
                </a>
            """

        connection.execute(
            """
            INSERT INTO users (username, password, about)
            VALUES (?, ?, ?)
            """,
            (username, password, "")
        )

        connection.commit()
        connection.close()

        return f"""
            {STYLE}

            <h2>Регистрация успешна!</h2>

            <a href="/login">
                Перейти ко входу
            </a>
        """

    return f"""
        {STYLE}

        <h2>Регистрация</h2>

        <form method="POST">

            <input
                type="text"
                name="username"
                placeholder="Имя пользователя"
                required
            >

            <br><br>

            <input
                type="password"
                name="password"
                placeholder="Пароль"
                required
            >

            <br><br>

            <button type="submit">
                Зарегистрироваться
            </button>

        </form>

        <br>

        <a href="/login">
            Уже есть аккаунт? Войти
        </a>

        <br><br>

        <a href="/">
            На главную
        </a>
    """


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        connection = sqlite3.connect("database.db")

        user = connection.execute(
            """
            SELECT * FROM users
            WHERE username = ? AND password = ?
            """,
            (username, password)
        ).fetchone()

        connection.close()

        if user:
            session["username"] = username
            return redirect("/")

        return f"""
            {STYLE}

            <h2>Неверный логин или пароль</h2>

            <a href="/login">
                Попробовать снова
            </a>
        """

    return f"""
        {STYLE}

        <h2>Вход</h2>

        <form method="POST">

            <input
                type="text"
                name="username"
                placeholder="Имя пользователя"
                required
            >

            <br><br>

            <input
                type="password"
                name="password"
                placeholder="Пароль"
                required
            >

            <br><br>

            <button type="submit">
                Войти
            </button>

        </form>

        <br>

        <a href="/register">
            Нет аккаунта? Зарегистрироваться
        </a>

        <br><br>

        <a href="/">
            На главную
        </a>
    """


@app.route("/create_post", methods=["GET", "POST"])
def create_post():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        text = request.form["text"].strip()

        if text == "":
            return f"""
                {STYLE}

                <h2>
                    Пост не может быть пустым
                </h2>

                <a href="/create_post">
                    Вернуться
                </a>
            """

        username = session["username"]

        created_at = datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )

        connection = sqlite3.connect("database.db")

        connection.execute(
            """
            INSERT INTO posts
            (username, text, created_at)
            VALUES (?, ?, ?)
            """,
            (username, text, created_at)
        )

        connection.commit()
        connection.close()

        return redirect("/")

    return f"""
        {STYLE}

        <h2>Новый пост</h2>

        <p>
            Автор:
            <b>{session["username"]}</b>
        </p>

        <form method="POST">

            <textarea
                name="text"
                placeholder="Напишите что-нибудь..."
                rows="5"
                cols="40"
                required
            ></textarea>

            <br><br>

            <button type="submit">
                Опубликовать
            </button>

        </form>

        <br>

        <a href="/">
            Назад
        </a>
    """


@app.route("/my_posts")
def my_posts():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    connection = sqlite3.connect("database.db")

    posts = connection.execute(
        """
        SELECT * FROM posts
        WHERE username = ?
        ORDER BY id DESC
        """,
        (username,)
    ).fetchall()

    connection.close()

    posts_html = ""

    for post in posts:
        created_at = post[3]

        if created_at is None:
            created_at = "Дата не указана"

        posts_html += f"""
            <div class="post">

                <p>{post[2]}</p>

                <div class="post-date">
                    Опубликовано: {created_at}
                </div>

                <br>

                <a href="/edit_post/{post[0]}">
                    Редактировать
                </a>

                <a href="/delete_post/{post[0]}">
                    Удалить
                </a>

            </div>
        """

    if not posts:
        posts_html = """
            <p>
                У вас пока нет публикаций.
            </p>
        """

    return f"""
        {STYLE}

        <h1>Мои публикации</h1>

        <p>
            Пользователь:
            <b>{username}</b>
        </p>

        <p>
            Всего моих публикаций:
            <b>{len(posts)}</b>
        </p>

        {posts_html}

        <br>

        <a href="/create_post">
            Добавить пост
        </a>

        <a href="/">
            Общая лента
        </a>
    """


@app.route("/edit_post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    connection = sqlite3.connect("database.db")

    post = connection.execute(
        """
        SELECT * FROM posts
        WHERE id = ? AND username = ?
        """,
        (post_id, username)
    ).fetchone()

    if post is None:
        connection.close()

        return f"""
            {STYLE}

            <h2>Публикация не найдена</h2>

            <a href="/my_posts">
                Вернуться
            </a>
        """

    if request.method == "POST":
        new_text = request.form["text"].strip()

        if new_text == "":
            connection.close()

            return f"""
                {STYLE}

                <h2>
                    Текст не может быть пустым
                </h2>

                <a href="/edit_post/{post_id}">
                    Вернуться
                </a>
            """

        connection.execute(
            """
            UPDATE posts
            SET text = ?
            WHERE id = ? AND username = ?
            """,
            (new_text, post_id, username)
        )

        connection.commit()
        connection.close()

        return redirect("/my_posts")

    connection.close()

    return f"""
        {STYLE}

        <h2>
            Редактирование публикации
        </h2>

        <form method="POST">

            <textarea
                name="text"
                rows="5"
                cols="40"
                required
            >{post[2]}</textarea>

            <br><br>

            <button type="submit">
                Сохранить
            </button>

        </form>

        <br>

        <a href="/my_posts">
            Отмена
        </a>
    """


@app.route("/delete_post/<int:post_id>")
def delete_post(post_id):
    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    connection = sqlite3.connect("database.db")

    connection.execute(
        """
        DELETE FROM posts
        WHERE id = ? AND username = ?
        """,
        (post_id, username)
    )

    connection.commit()
    connection.close()

    return redirect("/my_posts")


# Публичный профиль пользователя
@app.route("/profile/<username>")
def profile(username):
    connection = sqlite3.connect("database.db")

    user = connection.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if user is None:
        connection.close()

        return f"""
            {STYLE}

            <h2>Пользователь не найден</h2>

            <a href="/">
                На главную
            </a>
        """

    posts = connection.execute(
        """
        SELECT * FROM posts
        WHERE username = ?
        ORDER BY id DESC
        """,
        (username,)
    ).fetchall()

    connection.close()

    about = user[3]

    if about is None or about == "":
        about = "Пользователь пока ничего о себе не написал."

    posts_html = ""

    for post in posts:
        created_at = post[3]

        if created_at is None:
            created_at = "Дата не указана"

        posts_html += f"""
            <div class="post">

                <p>{post[2]}</p>

                <div class="post-date">
                    Опубликовано: {created_at}
                </div>

            </div>
        """

    if not posts:
        posts_html = """
            <p>
                У пользователя пока нет публикаций.
            </p>
        """

    edit_link = ""

    # Кнопка редактирования есть только
    # у владельца профиля
    if session.get("username") == username:
        edit_link = """
            <a href="/edit_profile">
                Редактировать профиль
            </a>
            <br><br>
        """

    return f"""
        {STYLE}

        <h1>Профиль: {username}</h1>

        <div class="profile-info">

            <h3>О себе</h3>

            <p>{about}</p>

            <p>
                Публикаций:
                <b>{len(posts)}</b>
            </p>

            {edit_link}

        </div>

        <h2>Публикации пользователя</h2>

        {posts_html}

        <br>

        <a href="/">
            Вернуться в общую ленту
        </a>
    """


# Редактирование своего профиля
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    connection = sqlite3.connect("database.db")

    user = connection.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if request.method == "POST":
        about = request.form["about"].strip()

        connection.execute(
            """
            UPDATE users
            SET about = ?
            WHERE username = ?
            """,
            (about, username)
        )

        connection.commit()
        connection.close()

        return redirect(f"/profile/{username}")

    connection.close()

    about = user[3]

    if about is None:
        about = ""

    return f"""
        {STYLE}

        <h2>Редактирование профиля</h2>

        <p>
            Пользователь:
            <b>{username}</b>
        </p>

        <form method="POST">

            <textarea
                name="about"
                placeholder="Расскажите немного о себе..."
                rows="5"
                cols="40"
            >{about}</textarea>

            <br><br>

            <button type="submit">
                Сохранить
            </button>

        </form>

        <br>

        <a href="/profile/{username}">
            Отмена
        </a>
    """


@app.route("/logout")
def logout():
    session.pop("username", None)

    return redirect("/")




"""def show_users():
    connection = sqlite3.connect("database.db")
    users = connection.execute("SELECT * FROM users").fetchall()
    connection.close()

    print(users)"""
if __name__ == "__main__":
    create_database()
    app.run(debug=True)