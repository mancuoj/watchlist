# Watch List

- [Flask 入门](https://tutorial.helloflask.com/)

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

## Jinja

- [官网](https://jinja.palletsprojects.com/en/3.0.x/)
- [过滤器](https://jinja.palletsprojects.com/en/3.0.x/templates/#builtin-filters)
- ...