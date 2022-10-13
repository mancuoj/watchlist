from flask import Flask, render_template

app = Flask(__name__)

# 虚拟数据
name = 'Mancuoj'
movies = [
    {'title': 'A Perfect World', 'year': '1993'},
    {'title': 'Leon', 'year': '1994'},
    {'title': 'Mahjong', 'year': '1996'},
    {'title': 'Swallowtail Butterfly', 'year': '1996'},
    {'title': 'King of Comedy', 'year': '1999'},
    {'title': 'Devils on the Doorstep', 'year': '1999'},
    {'title': 'WALL-E', 'year': '2008'},
    {'title': 'The Pork of Music', 'year': '2012'},
]

@app.route("/")
def index():
    # 渲染模板，传入变量
    return render_template('index.html', name=name, movies=movies)