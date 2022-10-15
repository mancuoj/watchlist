import os
import sys
import click

from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)


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
app.config["SECRET_KEY"] = "dev"
db = SQLAlchemy(app)
login_manager = LoginManager(app)
# 未登录的用户访问对应的 URL，Flask-Login 会把用户重定向到登录页面，并显示一个错误提示
# 可以通过设置 login_manager.login_message 来自定义错误提示消息
login_manager.login_view = "login"
login_manager.login_message = "请登录！"

#################################################
#               用户加载回调函数                #
#################################################
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


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
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


#################################################
#             将 user 注入模板上下文            #
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


#################################################
#                   添加操作                    #
#################################################
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
        flash("添加成功", "message")
        return redirect(url_for("index"))

    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


#################################################
#                   编辑操作                    #
#################################################
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
        flash("更新成功", "message")
        return redirect(url_for("index"))

    return render_template("edit.html", movie=movie)


#################################################
#                   删除操作                    #
#################################################
@app.route("/movie/delete/<int:movie_id>", methods=["POST"])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("删除成功", "message")
    return redirect(url_for("index"))


#################################################
#                   用户登录                    #
#################################################
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
            flash("登录成功", "message")
            return redirect(url_for("index"))

        flash("用户名或密码错误", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


#################################################
#                   用户登出                    #
#################################################
@app.route("/logout")
@login_required  # 未登录不允许查看
def logout():
    logout_user()
    flash("Bye!", "message")
    return redirect(url_for("index"))


#################################################
#                   用户设置                    #
#################################################
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
        flash("设置更新成功", "message")
        return redirect(url_for("index"))

    return render_template("setting.html")
