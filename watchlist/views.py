from flask import render_template, url_for, request, redirect, flash
from flask_login import current_user, login_required, login_user, logout_user

from watchlist import app, db
from watchlist.models import User, Movie


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not current_user.is_authenticated:
            return redirect(url_for("index"))

        title = request.form.get("title")
        year = request.form.get("year")
        if (
            not title
            or not year
            or len(title) > 60
            or len(year) != 4
            or not year.isdigit()
        ):
            flash("无效输入", "error")
            return redirect(url_for("index"))

        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash("添加成功", "success")
        return redirect(url_for("index"))

    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


@app.route("/movie/edit/<int:movie_id>", methods=["GET", "POST"])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == "POST":
        title = request.form.get("title")
        year = request.form.get("year")
        if (
            not title
            or not year
            or len(title) > 60
            or len(year) != 4
            or not year.isdigit()
        ):
            flash("无效输入", "error")
            return redirect(url_for("edit", movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash("更新成功", "success")
        return redirect(url_for("index"))

    return render_template("edit.html", movie=movie)


@app.route("/movie/delete/<int:movie_id>", methods=["POST"])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("删除成功", "success")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            flash("无效输入", "error")
            return redirect(url_for("login"))

        user = User.query.first()
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash("登录成功", "success")
            return redirect(url_for("index"))

        flash("用户名或密码错误", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Bye!", "message")
    return redirect(url_for("index"))


@app.route("/setting", methods=["GET", "POST"])
@login_required
def setting():
    if request.method == "POST":
        name = request.form.get("name")

        if not name or len(name) > 20:
            flash("无效输入", "error")
            return redirect(url_for("setting"))

        current_user.name = name
        db.session.commit()
        flash("设置更新成功", "success")
        return redirect(url_for("index"))

    return render_template("setting.html")
