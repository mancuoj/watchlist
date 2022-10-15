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
        user = User(username=username, name="Admin")
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo("完成！")
