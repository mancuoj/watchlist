import os
import sys
import click

from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

WIN = sys.platform.startswith("win")
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = prefix + os.path.join(app.root_path, "data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev"  # 等同于 app.secret_key = 'dev'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


@app.cli.command()
@click.option("--drop", is_flag=True, help="删除后重建数据库...")
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("初始化数据库...")


@app.cli.command()
def forge():
    db.drop_all()
    db.create_all()

    name = "Mancuoj"
    user = User(name=name)
    db.session.add(user)

    movies = [
        {"title": "死亡诗社", "year": "1989"},
        {"title": "美丽人生", "year": "1997"},
        {"title": "肖申克的救赎", "year": "1994"},
        {"title": "霸王别姬 ", "year": "1993"},
        {"title": "这个杀手不太冷", "year": "1994"},
        {"title": "活着", "year": "1994"},
        {"title": "无间道 ", "year": "2002"},
        {"title": "忠犬八公的故事", "year": "2009"},
    ]
    for m in movies:
        movie = Movie(title=m["title"], year=m["year"])
        db.session.add(movie)

    db.session.commit()
    click.echo("数据填充完毕...")


@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# 让 index 视图同时接受两种请求方式
# 对于 GET 请求，返回渲染后的页面
# 对于 POST 请求，获取提交的表单数据并保存
# 当表单中的提交按钮被按下，浏览器会创建一个新的请求，默认发往当前 URL
@app.route("/", methods=["GET", "POST"])
def index():
    # 当接受请求为 POST 时，处理表单数据
    if request.method == "POST":
        title = request.form.get("title")
        year = request.form.get("year")

        # 输入无效信息时，显示错误信息，并重定向到主页
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
        flash("添加成功", "message")
        return redirect(url_for("index"))

    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


# URL 变量
@app.route("/movie/edit/<int:movie_id>", methods=["GET", "POST"])
def edit(movie_id):
    # 能找到就返回对应主键的记录，如果没有找到，则返回 404 错误响应。
    movie = Movie.query.get_or_404(movie_id)

    if request.method == "POST":  # 处理编辑表单的提交请求
        title = request.form["title"]
        year = request.form["year"]

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
        flash("更新成功", "message")
        return redirect(url_for("index"))

    return render_template("edit.html", movie=movie)


# 为了安全的考虑，我们一般会使用 POST 请求来提交删除请求，也就是使用表单来实现（而不是用链接）
# 不涉及数据的传递，所以只需要接受 POST 请求
@app.route("/movie/delete/<int:movie_id>", methods=["POST"])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("删除成功", "message")
    return redirect(url_for("index"))
