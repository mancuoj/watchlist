import os
import sys
import click

from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

#################################################
#                   基础配置                    #
#################################################
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

#################################################
#                   错误处理                    #
#################################################
@app.errorhandler(400)
def page_not_found(e):
    return render_template("error/400.html"), 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error/404.html"), 404


@app.errorhandler(405)
def page_not_found(e):
    return render_template("error/405.html"), 405


@app.errorhandler(500)
def page_not_found(e):
    return render_template("error/500.html"), 500


#################################################
#                  数据模型类                   #
#################################################
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


#################################################
#              将变量注入模板上下文             #
#################################################
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


#################################################
#                  自定义命令                   #
#################################################
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


#################################################
#                   添加操作                    #
#################################################
@app.route("/", methods=["GET", "POST"])
def index():
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
            return redirect(url_for("index"))

        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash("添加成功", "message")
        return redirect(url_for("index"))

    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


#################################################
#                   编辑操作                    #
#################################################
@app.route("/movie/edit/<int:movie_id>", methods=["GET", "POST"])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == "POST":
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


#################################################
#                   删除操作                    #
#################################################
@app.route("/movie/delete/<int:movie_id>", methods=["POST"])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("删除成功", "message")
    return redirect(url_for("index"))
