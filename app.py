import os
import sys
import click

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

WIN = sys.platform.startswith("win")
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = prefix + os.path.join(app.root_path, "data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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


# 将重复使用的变量统一注入到每一个模板的上下文环境中，可以直接在模板内使用
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


@app.errorhandler(404)  # 传入错误代码
def page_not_found(e):  # 接受异常对象作为参数
    # 返回模板和状态码，因为默认会使用 200 状态码代表成功，所以之前不用写
    return render_template("404.html"), 404


@app.route("/")
def index():
    movies = Movie.query.all()
    return render_template("index.html", movies=movies)
