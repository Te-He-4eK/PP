import sqlite3
from datetime import datetime

from flask import Flask, request, session, redirect, render_template, url_for

from database import create_database


app = Flask(__name__)
app.secret_key = "secret_key"


# Главная страница с общей лентой
@app.route("/")
def index():
    connection = sqlite3.connect("database.db")

    posts = connection.execute(
        "SELECT * FROM posts ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        posts=posts,
        username=session.get("username")
    )


# Регистрация
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            return render_template(
                "message.html",
                message="Логин и пароль не могут быть пустыми",
                back_url=url_for("register"),
                back_text="Вернуться к регистрации"
            )

        connection = sqlite3.connect("database.db")

        existing_user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing_user:
            connection.close()

            return render_template(
                "message.html",
                message="Пользователь с таким именем уже существует",
                back_url=url_for("register"),
                back_text="Выбрать другой логин"
            )

        connection.execute(
            """
            INSERT INTO users (username, password, about)
            VALUES (?, ?, ?)
            """,
            (username, password, "")
        )

        connection.commit()
        connection.close()

        return render_template(
            "message.html",
            message="Регистрация успешна!",
            back_url=url_for("login"),
            back_text="Перейти ко входу"
        )

    return render_template("register.html")


# Вход
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
            return redirect(url_for("index"))

        return render_template(
            "message.html",
            message="Неверный логин или пароль",
            back_url=url_for("login"),
            back_text="Попробовать снова"
        )

    return render_template("login.html")


# Создание новой публикации
@app.route("/create_post", methods=["GET", "POST"])
def create_post():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    if request.method == "POST":
        text = request.form["text"].strip()

        if not text:
            return render_template(
                "message.html",
                message="Пост не может быть пустым",
                back_url=url_for("create_post"),
                back_text="Вернуться"
            )

        created_at = datetime.now().strftime("%d.%m.%Y %H:%M")

        connection = sqlite3.connect("database.db")

        connection.execute(
            """
            INSERT INTO posts (username, text, created_at)
            VALUES (?, ?, ?)
            """,
            (username, text, created_at)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("index"))

    return render_template(
        "create_post.html",
        username=username
    )


# Публикации текущего пользователя
@app.route("/my_posts")
def my_posts():
    if "username" not in session:
        return redirect(url_for("login"))

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

    return render_template(
        "my_posts.html",
        posts=posts,
        username=username
    )


# Редактирование своей публикации
@app.route("/edit_post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    connection = sqlite3.connect("database.db")

    post = connection.execute(
        """
        SELECT * FROM posts
        WHERE id = ? AND username = ?
        """,
        (post_id, username)
    ).fetchone()

    if not post:
        connection.close()

        return render_template(
            "message.html",
            message="Публикация не найдена",
            back_url=url_for("my_posts"),
            back_text="Вернуться"
        )

    if request.method == "POST":
        new_text = request.form["text"].strip()

        if not new_text:
            connection.close()

            return render_template(
                "message.html",
                message="Текст не может быть пустым",
                back_url=url_for(
                    "edit_post",
                    post_id=post_id
                ),
                back_text="Вернуться"
            )

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

        return redirect(url_for("my_posts"))

    connection.close()

    return render_template(
        "edit_post.html",
        post=post
    )


# Удаление своей публикации
@app.route("/delete_post/<int:post_id>")
def delete_post(post_id):
    if "username" not in session:
        return redirect(url_for("login"))

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

    return redirect(url_for("my_posts"))


# Публичный профиль пользователя
@app.route("/profile/<username>")
def profile(username):
    connection = sqlite3.connect("database.db")

    user = connection.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if not user:
        connection.close()

        return render_template(
            "message.html",
            message="Пользователь не найден",
            back_url=url_for("index"),
            back_text="На главную"
        )

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

    if not about:
        about = "Пользователь пока ничего о себе не написал."

    can_edit = session.get("username") == username

    return render_template(
        "profile.html",
        username=username,
        about=about,
        posts=posts,
        can_edit=can_edit
    )


# Редактирование своего профиля
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "username" not in session:
        return redirect(url_for("login"))

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

        return redirect(
            url_for("profile", username=username)
        )

    connection.close()

    about = user[3] if user[3] else ""

    return render_template(
        "edit_profile.html",
        username=username,
        about=about
    )


# Выход из аккаунта
@app.route("/logout")
def logout():
    session.pop("username", None)

    return redirect(url_for("index"))


if __name__ == "__main__":
    create_database()
    app.run(debug=True)