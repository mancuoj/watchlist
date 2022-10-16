from flask import render_template, url_for, request, redirect, flash
from flask_login import current_user, login_required, login_user, logout_user

from watchlist import app, db
from watchlist.models import User, Movie, Comment
from watchlist.forms import CommentForm


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

        user = User.query.filter_by(username=username).first()
        if (
            user is not None
            and username == user.username
            and user.validate_password(password)
        ):
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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")

        if not username or not password or len(username) > 20:
            flash("无效输入", "error")
            return redirect(url_for("register"))
        if password != password_confirmation:
            flash("两次输入的密码不一致！", "error")
            return redirect(url_for("register"))

        user = User.query.filter_by(username=username).first()
        if user is not None:
            flash("用户名已存在", "error")
            return redirect(url_for("register"))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("注册成功，请登录", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        username = request.form.get("username")
        if not username or len(username) > 20:
            flash("无效输入", "error")
            return redirect(url_for("settings"))

        user = User.query.filter_by(username=username).first()
        if user is not None:
            flash("用户名已存在", "error")
            return redirect(url_for("settings"))

        current_user.username = username
        db.session.commit()
        flash("用户名更新成功", "success")
        return redirect(url_for("index"))

    return render_template("settings.html")


@app.route("/comment", methods=["GET", "POST"])
@login_required
def comment():
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(name=current_user.username, text=form.text.data)
        db.session.add(comment)
        db.session.commit()
        flash("评论成功", "success")
        return redirect(url_for("comment"))

    comments = Comment.query.all()
    return render_template("comment.html", form=form, comments=comments)
