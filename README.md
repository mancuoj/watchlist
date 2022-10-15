- [第 8 章：用户认证 - Flask 入门教程](https://tutorial.helloflask.com/login/)
- [Jinja 官网](https://jinja.palletsprojects.com/en/3.0.x/)
- [Jinja 过滤器](https://jinja.palletsprojects.com/en/3.0.x/templates/#builtin-filters)
- [Flask-SQLAlchemy 官方文档](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [Flask-WTF 表单处理工具](https://flask-wtf.readthedocs.io/en/1.0.x/)
- ...

## 虚拟环境 venv

```sh
python3 -m venv <env>
. env/bin/activate
# 激活成功命令行前会显示 (env)

deactivate

pip install flask
flask run
```

## python-dotenv

为了不用每次打开新的终端会话都要设置环境变量，我们安装用来自动导入系统环境变量的 python-dotenv：

```sh
pip install python-dotenv
```

Flask 会从项目根目录的 .flaskenv 和 .env 文件读取环境变量并设置
- .flaskenv 用来存储 Flask 命令行系统相关的公开环境变量
- 而 .env 则用来存储敏感数据，不应该提交进 Git 仓库
  

可以在 .flaskenv 中写上：

```
FLASK_DEBUG=1
```

## 数据库

[SQLAlchemy](https://www.sqlalchemy.org/)——一个 Python 数据库工具（ORM，即对象关系映射）。借助 SQLAlchemy，你可以通过定义 Python 类来表示数据库里的一张表（类属性表示表中的字段 / 列），通过对这个类进行各种操作来代替写 SQL 语句。

```sh
pip install flask-sqlalchemy
```



### 引入 SQLAlchemy

```python
import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 兼容性处理
WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')  # 找到数据库连接地址
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)
```

### 创建模型类 & db

在 watchlist 中需要存两类数据，用户信息和电影信息：

```python
# app.py
class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字


class Movie(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份
```



- 模型类要声明继承 `db.Model`
- 每一个类属性要实例化 `db.Column`，传入的参数为类型
- 在 `db.Column()` 中添加额外的选项（参数）可以对字段进行设置。比如，`primary_key` 设置当前字段是否为主键。除此之外，常用的选项还有 `nullable`（布尔值，是否允许为空值）、`index`（布尔值，是否设置索引）、`unique`（布尔值，是否允许重复值）、`default`（设置默认值）等。

常用的字段类型如下表所示：

| 字段类           | 说明                                          |
| :--------------- | :-------------------------------------------- |
| db.Integer       | 整型                                          |
| db.String (size) | 字符串，size 为最大长度，比如 `db.String(20)` |
| db.Text          | 长文本                                        |
| db.DateTime      | 时间日期，Python `datetime` 对象              |
| db.Float         | 浮点数                                        |
| db.Boolean       | 布尔值                                        |

根据模型类创建db：

```sh
flask shell
>>> from app import db
>>> db.create_all()

# 删除重新创建
>>> db.drop_all()
>>> db.create_all()
```

### 自定义终端命令

```python
import click

...

@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息
```

## CRUD

**创建**：id 会自动处理，只需要在最后一行调用 `db.session.commit()` 即可把记录提交进数据库中

```python
>>> from app import User, Movie  # 导入模型类
>>> user = User(name='Grey Li')  # 创建一个 User 记录
>>> m1 = Movie(title='Leon', year='1994')  # 创建一个 Movie 记录
>>> m2 = Movie(title='Mahjong', year='1996')  # 再创建一个 Movie 记录
>>> db.session.add(user)  # 把新创建的记录添加到数据库会话
>>> db.session.add(m1)
>>> db.session.add(m2)
>>> db.session.commit()  # 提交数据库会话，只需要在最后调用一次即可
```

**读取**：`<模型类>.query.<过滤方法（可选）>.<查询方法>`

```python
>>> from app import Movie  # 导入模型类
>>> movie = Movie.query.first()  # 获取 Movie 模型的第一个记录（返回模型类实例）
>>> movie.title  # 对返回的模型类实例调用属性即可获取记录的各字段数据
'Leon'
>>> movie.year
'1994'
>>> Movie.query.all()  # 获取 Movie 模型的所有记录，返回包含多个模型类实例的列表
[<Movie 1>, <Movie 2>]
>>> Movie.query.count()  # 获取 Movie 模型所有记录的数量
2
>>> Movie.query.get(1)  # 获取主键值为 1 的记录
<Movie 1>
>>> Movie.query.filter_by(title='Mahjong').first()  # 获取 title 字段值为 Mahjong 的记录
<Movie 2>
>>> Movie.query.filter(Movie.title=='Mahjong').first()  # 等同于上面的查询，但使用不同的过滤方法
<Movie 2>
```



常用的过滤方法：

| 过滤方法    | 说明                                                         |
| :---------- | :----------------------------------------------------------- |
| filter()    | 使用指定的规则过滤记录，返回新产生的查询对象                 |
| filter_by() | 使用指定规则过滤记录（以关键字表达式的形式），返回新产生的查询对象 |
| order_by()  | 根据指定条件对记录进行排序，返回新产生的查询对象             |
| group_by()  | 根据指定条件对记录进行分组，返回新产生的查询对象             |

常用的查询方法：

| 查询方法       | 说明                                                         |
| :------------- | :----------------------------------------------------------- |
| all()          | 返回包含所有查询记录的列表                                   |
| first()        | 返回查询的第一条记录，如果未找到，则返回 None                |
| get(id)        | 传入主键值作为参数，返回指定主键值的记录，如果未找到，则返回 None |
| count()        | 返回查询结果的数量                                           |
| first_or_404() | 返回查询的第一条记录，如果未找到，则返回 404 错误响应        |
| get_or_404(id) | 传入主键值作为参数，返回指定主键值的记录，如果未找到，则返回 404 错误响应 |
| paginate()     | 返回一个 Pagination 对象，可以对记录进行分页处理             |



**更新**：

```python
>>> movie = Movie.query.get(2)
>>> movie.title = 'WALL-E'  # 直接对实例属性赋予新的值即可
>>> movie.year = '2008'
>>> db.session.commit()  # 注意仍然需要调用这一行来提交改动
```



**删除**：

```python
>>> movie = Movie.query.get(1)
>>> db.session.delete(movie)  # 使用 db.session.delete() 方法删除记录，传入模型实例
>>> db.session.commit()  # 提交改动
```

## imdb or douban

```html
<a class="imdb" href="https://www.imdb.com/find?q={{ movie.title }}">
<a class="douban" href="https://search.douban.com/movie/subject_search?search_text={{ movie.title }}">
```

## request and flash

- Flask 会在请求触发后把请求信息放到 request 对象里，只能在视图函数内部调用它
- 它包含请求相关的所有信息，比如请求的路径（request.path）、请求的方法（request.method）、表单数据（request.form）、查询字符串（request.args）等
- flash() 函数在内部会把消息存储到 Flask 提供的 session 对象里
- session 用来在请求间存储数据，它会把数据签名后存储到浏览器的 Cookie 中
- 在模板中使用 get_flashed_messages() 函数获取消息
- 所以我们需要设置签名所需的密钥：

```python
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
# 这个密钥的值在开发时可以随便设置。基于安全的考虑，在部署时应该设置为随机字符，且不应该明文写在代码里
```

## 安全存储密码

把密码明文存储在数据库中是极其危险的，假如攻击者窃取了你的数据库，那么用户的账号和密码就会被直接泄露。更保险的方式是对每个密码进行计算生成独一无二的密码散列值，这样即使攻击者拿到了散列值，也几乎无法逆向获取到密码。

Flask 的依赖 Werkzeug 内置了用于生成和验证密码散列值的函数，`werkzeug.security.generate_password_hash()` 用来为给定的密码生成密码散列值，而 `werkzeug.security.check_password_hash()` 则用来检查给定的散列值和密码是否对应。使用示例如下所示：

```python
>>> from werkzeug.security import generate_password_hash, check_password_hash
>>> pw_hash = generate_password_hash('dog')  # 为密码 dog 生成密码散列值
>>> pw_hash  # 查看密码散列值
'pbkdf2:sha256:50000$mm9UPTRI$ee68ebc71434a4405a28d34ae3f170757fb424663dc0ca15198cb881edc0978f'
>>> check_password_hash(pw_hash, 'dog')  # 检查散列值是否对应密码 dog
True
>>> check_password_hash(pw_hash, 'cat')  # 检查散列值是否对应密码 cat
False
```