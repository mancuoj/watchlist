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

# 创建模型类，程序只有一个用户，所以没有将 User 表和 Movie 表建立关联
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


# 自定义命令行命令，设置选项，如 flask initdb
@app.cli.command()
@click.option("--drop", is_flag=True, help="删除后重建数据库...")
def initdb(drop):
    # 判断是否输入了选项
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("初始化数据库...")


# 生成虚拟数据
@app.cli.command()
def forge():
    # 如果没有创建数据库就创建一个
    db.create_all()

    name = "Mancuoj"
    user = User(name=name)
    db.session.add(user)

    movies = [
        {"title": "Dead Poets Society", "year": "1989"},
        {"title": "A Perfect World", "year": "1993"},
        {"title": "Leon", "year": "1994"},
        {"title": "Mahjong", "year": "1996"},
        {"title": "Swallowtail Butterfly", "year": "1996"},
        {"title": "King of Comedy", "year": "1999"},
        {"title": "Devils on the Doorstep", "year": "1999"},
        {"title": "WALL-E", "year": "2008"},
        {"title": "The Pork of Music", "year": "2012"},
    ]
    for m in movies:
        movie = Movie(title=m["title"], year=m["year"])
        db.session.add(movie)

    db.session.commit()
    click.echo("数据填充完毕...")


@app.route("/")
def index():
    user = User.query.first()
    movies = Movie.query.all()
    return render_template("index.html", user=user, movies=movies)
