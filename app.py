# 默认名 app.py 或者 wsgi.py
# 可以通过环境变量 FLASK_APP 来进行修改
# 开发时通常使用 export FLASK_ENV=development 来开启调试模式（已弃用）
from flask import Flask, url_for
from markupsafe import escape

app = Flask(__name__)

# view function
# 用装饰器来为这个函数绑定对应的 URL（可以用多个装饰器绑定多个 URL）
# 当用户在浏览器访问这个 URL 的时候，就会触发这个函数获取返回值，并把返回值显示到浏览器
@app.route("/home")
@app.route("/index")
@app.route("/")
def hello():
    return "<h1>Hello Flask!</h1>"


# 也可以在装饰器中定义变量
@app.route("/user/<name>")
def user_page(name):
    # 用户输入的数据可能会包含恶意代码，需要对齐做转义处理
    return f"User: {escape(name)}"


# 视图函数的名称代表某个路由的端点（endpoint），同时用来生成视图函数对应的 URL
@app.route("/test")
def test_url_for():
    # 显示在命令行窗口
    print(url_for("hello"))  # /，显示最后一个装饰器
    print(url_for("user_page", name="mancuoj"))  # /user/mancuoj
    print(url_for("user_page", name="a"))  # /user/a
    print(url_for("test_url_for"))  # /test
    # 传入多余参数，会被作为查询字符串附加到 URL 后面
    print(url_for("test_url_for", num=2))  # /test?num=2
    return "Test Page"
