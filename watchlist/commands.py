import os
import click

from watchlist import app, db
from watchlist.models import User, Movie


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

    movies = [
        {"title": "Dead Poets Society", "year": "1989"},
        {"title": "活着", "year": "1994"},
        {"title": "霸王别姬 ", "year": "1993"},
        {"title": "Léon: The Professional", "year": "1994"},
        {"title": "Hachi: A Dog's Tale", "year": "2009"},
    ]
    for m in movies:
        movie = Movie(title=m["title"], year=m["year"])
        db.session.add(movie)

    db.session.commit()
    click.echo("数据填充完毕...")


@app.cli.command()
@click.option("--username", prompt=True, help="用户名 - 用于登录")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="密码 - 用于登录",
)
def admin(username, password):
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo("更新管理员用户中...")
        user.username = username
        user.password = password
        user.set_password(password)
    else:
        click.echo("创建管理员用户中...")
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo("完成！")


@app.cli.group()
def translate():
    pass


@translate.command()
@click.argument("locale")
def init(locale):
    if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
        raise RuntimeError("提取失败")
    if os.system("pybabel init -i messages.pot -d watchlist/translations -l " + locale):
        raise RuntimeError("初始化失败")
    os.remove("message.pot")


@translate.command()
def update():
    if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
        raise RuntimeError("提取失败")
    if os.system("pybabel update -i messages.pot -d watchlist/translations"):
        raise RuntimeError("更新失败")
    os.remove("messages.pot")


@translate.command()
def compile():
    if os.system("pybabel compile -d watchlist/translations"):
        raise RuntimeError("编译失败")
