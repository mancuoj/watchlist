- [第 4 章：静态文件 - Flask 入门教程](https://tutorial.helloflask.com/static/)
- [Jinja 官网](https://jinja.palletsprojects.com/en/3.0.x/)
- [Jinja 过滤器](https://jinja.palletsprojects.com/en/3.0.x/templates/#builtin-filters)
- [Flask-SQLAlchemy 官方文档](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
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

```sh
pip install flask-sqlalchemy
```

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