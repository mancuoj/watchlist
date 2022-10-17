from flask import render_template, url_for, redirect, flash
from flask_login import current_user, login_required, login_user, logout_user
from flask_babel import _

from watchlist import app, db
from watchlist.models import User, Movie, Comment
from watchlist.forms import (
    MovieForm,
    CommentForm,
    LoginForm,
    RegisterForm,
    SettingsForm,
)


@app.route("/", methods=["GET", "POST"])
def index():
    form = MovieForm()
    if form.validate_on_submit():
        title = form.title.data
        year = form.year.data

        if year.isdigit():
            movie = Movie(title=title, year=year)
            db.session.add(movie)
            db.session.commit()
            flash(_("添加成功"), "success")
            return redirect(url_for("index"))

        flash(_("无效输入"), "error")
        return redirect(url_for("index"))

    movies = Movie.query.all()
    return render_template("index.html", movies=movies, form=form)


@app.route("/movie/edit/<int:movie_id>", methods=["GET", "POST"])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    form = MovieForm()
    if form.validate_on_submit():
        title = form.title.data
        year = form.year.data

        if year.isdigit():
            movie.title = title
            movie.year = year
            db.session.commit()
            flash(_("更新成功"), "success")
            return redirect(url_for("index"))
        flash(_("无效输入"), "error")
        return redirect(url_for("edit", movie_id=movie_id))

    return render_template("edit.html", movie=movie, form=form)


@app.route("/movie/delete/<int:movie_id>", methods=["POST"])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash(_("删除成功"), "success")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if (
            user is not None
            and user.username == username
            and user.validate_password(password)
        ):
            login_user(user)
            flash(_("登录成功"), "success")
            return redirect(url_for("index"))

        flash(_("用户名或密码错误"), "error")
        return redirect(url_for("login"))

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Bye!", "message")
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        password_confirmation = form.password_confirmation.data

        if password != password_confirmation:
            flash(_("两次输入的密码不一致！"), "error")
            return redirect(url_for("register"))

        user = User.query.filter_by(username=username).first()
        if user is not None:
            flash(_("用户名已存在"), "error")
            return redirect(url_for("register"))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(_("注册成功，请登录"), "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()

        if user is not None:
            flash(_("用户名已存在"), "error")
            return redirect(url_for("settings"))

        current_user.username = username
        db.session.commit()
        flash(_("用户名更新成功"), "success")
        return redirect(url_for("index"))

    return render_template("settings.html", form=form)


@app.route("/comment", methods=["GET", "POST"])
def comment():
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(name=current_user.username, text=form.text.data)
        db.session.add(comment)
        db.session.commit()
        flash(_("评论成功"), "success")
        return redirect(url_for("comment"))

    comments = Comment.query.all()
    return render_template("comment.html", form=form, comments=comments)
