import sqlite3
from flask import Flask, request, session

app = Flask(__name__)

app.secret_key = "secret_key"


# Простые стили для приложения
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
</style>
"""


def create_database():
    connection = sqlite3.connect("database.db")

    # Таблица пользователей
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Таблица постов
    connection.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            text TEXT NOT NULL
        )
    """)

    connection.close()


@app.route("/")
def index():
    connection = sqlite3.connect("database.db")

    posts = connection.execute(
        "SELECT * FROM posts ORDER BY id DESC"
    ).fetchall()

    connection.close()

    posts_html = ""

    for post in posts:
        posts_html += f"""
            <div class="post">
                <b>{post[1]}</b>
                <p>{post[2]}</p>
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

            <a href="/create_post">Добавить пост</a>
            <br><br>

            <a href="/logout">Выйти</a>

            <hr>

            <h2>Публикации</h2>

            {posts_html}
        """

    return f"""
        {STYLE}

        <h1>Общая лента</h1>

        <a href="/register">Регистрация</a>
        <br><br>

        <a href="/login">Вход</a>

        <hr>

        <h2>Публикации</h2>

        {posts_html}
    """


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # Проверяем пустые поля
        if username == "" or password == "":
            return f"""
                {STYLE}

                <h2>Логин и пароль не могут быть пустыми</h2>

                <a href="/register">
                    Вернуться к регистрации
                </a>
            """

        connection = sqlite3.connect("database.db")

        # Проверяем, существует ли такой пользователь
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
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
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
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()

        connection.close()

        if user:
            session["username"] = username

            return f"""
                {STYLE}

                <h2>Вход выполнен!</h2>

                <a href="/">
                    Перейти на главную
                </a>
            """

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
        return f"""
            {STYLE}

            <h2>Сначала войдите в аккаунт</h2>

            <a href="/login">
                Войти
            </a>
        """

    if request.method == "POST":
        text = request.form["text"].strip()

        # Запрещаем пустые посты
        if text == "":
            return f"""
                {STYLE}

                <h2>Пост не может быть пустым</h2>

                <a href="/create_post">
                    Вернуться
                </a>
            """

        username = session["username"]

        connection = sqlite3.connect("database.db")

        connection.execute(
            "INSERT INTO posts (username, text) VALUES (?, ?)",
            (username, text)
        )

        connection.commit()
        connection.close()

        return f"""
            {STYLE}

            <h2>Пост опубликован!</h2>

            <a href="/">
                Вернуться в общую ленту
            </a>
        """

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


@app.route("/logout")
def logout():
    session.pop("username", None)

    return f"""
        {STYLE}

        <h2>Вы вышли из аккаунта</h2>

        <a href="/">
            На главную
        </a>
    """




"""def show_users():
    connection = sqlite3.connect("database.db")
    users = connection.execute("SELECT * FROM users").fetchall()
    connection.close()

    print(users)"""
if __name__ == "__main__":
    create_database()
    app.run(debug=True)