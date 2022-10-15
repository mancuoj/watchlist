import unittest

from watchlist import app, db
from watchlist.models import Movie, User
from watchlist.commands import forge, initdb


class WatchlistTestCase(unittest.TestCase):
    def setUp(self):
        # 开启测试模式，这样在出错时不会输出多余信息
        # 然后使用 SQLite 内存型数据库，这样不会干扰开发时使用的数据库文件，且速度更快
        with app.app_context():
            app.config.update(
                TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:////:memory:"
            )
            # 创建数据库和表
            db.create_all()

            user = User(name="Test", username="test")
            user.set_password("123")
            movie = Movie(title="Test Movie Title", year="2019")

            db.session.add_all([user, movie])
            db.session.commit()

            self.client = app.test_client()  # 返回一个测试客户端对象，可以用来模拟客户端（浏览器）
            self.runner = app.test_cli_runner()  # 创建测试命令运行器

    def tearDown(self):
        with app.app_context():
            db.session.remove()  # 清除数据库会话
            db.drop_all()  # 删除数据库表

    # 测试程序实例是否存在
    def test_app_exist(self):
        self.assertIsNotNone(app)

    # 测试程序是否处于测试模式
    def test_app_is_testing(self):
        self.assertTrue(app.config["TESTING"])

    def test_404_page(self):
        # 传入 URL
        response = self.client.get("/no")
        data = response.get_data(as_text=True)
        self.assertIn("404 - 找不到该页面", data)
        self.assertEqual(response.status_code, 404)

    def test_index_page(self):
        response = self.client.get("/")
        data = response.get_data(as_text=True)
        self.assertIn("Test の 电影片单", data)
        self.assertIn("Test Movie Title", data)
        self.assertEqual(response.status_code, 200)

    # 辅助方法，用于登入用户
    def login(self):
        # 使用 post() 方法发送提交登录表单的 POST 请求
        # 使用 data 关键字以字典的形式传入请求数据（字典中的键为表单 <input> 元素的 name 属性值），作为登录表单的输入数据
        # 然后将 follow_redirects 参数设为 True 可以跟随重定向，最终返回的会是重定向后的响应
        self.client.post(
            "/login", data=dict(username="test", password="123"), follow_redirects=True
        )

    # 测试创建
    def test_create_item(self):
        self.login()

        response = self.client.post(
            "/", data=dict(title="New Movie", year="2019"), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertIn("添加成功", data)
        self.assertNotIn("无效输入", data)

        # 测试电影标题为空
        response = self.client.post(
            "/", data=dict(title="", year="2019"), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertNotIn("添加成功", data)
        self.assertIn("无效输入", data)

        # 测试电影年份为空
        response = self.client.post(
            "/", data=dict(title="New Movie", year=""), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertNotIn("添加成功", data)
        self.assertIn("无效输入", data)

    # 测试更新
    def test_update_item(self):
        self.login()

        response = self.client.get("/movie/edit/1")
        data = response.get_data(as_text=True)
        self.assertIn("Test Movie Title", data)
        self.assertIn("2019", data)
        self.assertIn("更新", data)

        # 测试更新操作
        response = self.client.post(
            "/movie/edit/1",
            data=dict(title="New Movie Edited", year="2019"),
            follow_redirects=True,
        )
        data = response.get_data(as_text=True)
        self.assertIn("更新成功", data)
        self.assertIn("New Movie Edited", data)

        # 测试电影标题为空
        response = self.client.post(
            "/movie/edit/1", data=dict(title="", year="2019"), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertNotIn("更新成功", data)
        self.assertIn("无效输入", data)

        # 测试更新条目操作，但电影年份为空
        response = self.client.post(
            "/movie/edit/1",
            data=dict(title="New Movie Edited Again", year=""),
            follow_redirects=True,
        )
        data = response.get_data(as_text=True)
        self.assertNotIn("New Movie Edited Again", data)
        self.assertNotIn("更新成功", data)
        self.assertIn("无效输入", data)

    # 测试删除
    def test_delete_item(self):
        self.login()

        response = self.client.post("/movie/delete/1", follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn("删除成功", data)
        self.assertNotIn("Test Movie Title", data)

    # 测试登录保护
    def test_login_protect(self):
        response = self.client.get("/")
        data = response.get_data(as_text=True)
        self.assertNotIn("登出", data)
        self.assertNotIn("设置", data)
        self.assertNotIn("</form>", data)
        self.assertNotIn("删除", data)
        self.assertNotIn("编辑", data)

    # 测试登录
    def test_login(self):
        response = self.client.post(
            "/login", data=dict(username="test", password="123"), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertIn("登录成功", data)
        self.assertIn("登出", data)
        self.assertIn("设置", data)
        self.assertIn("</form>", data)
        self.assertIn("删除", data)
        self.assertIn("修改", data)

        # 测试使用错误的密码登录
        response = self.client.post(
            "/login", data=dict(username="test", password="456"), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertNotIn("Login success.", data)
        self.assertIn("用户名或密码错误", data)

        # 测试使用错误的用户名登录
        response = self.client.post(
            "/login", data=dict(username="wrong", password="123"), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertNotIn("登录成功", data)
        self.assertIn("用户名或密码错误", data)

    # 测试登出
    def test_logout(self):
        self.login()

        response = self.client.get("/logout", follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn("Bye!", data)
        self.assertNotIn("登出", data)
        self.assertNotIn("设置", data)
        self.assertNotIn("</form>", data)
        self.assertNotIn("删除", data)
        self.assertNotIn("修改", data)

    # 测试设置
    def test_setting(self):
        self.login()

        # 测试设置页面
        response = self.client.get("/setting")
        data = response.get_data(as_text=True)
        self.assertIn("设置", data)
        self.assertIn("保存", data)

        # 测试更新设置
        response = self.client.post(
            "/setting",
            data=dict(
                name="Grey Li",
            ),
            follow_redirects=True,
        )
        data = response.get_data(as_text=True)
        self.assertIn("设置更新成功", data)
        self.assertIn("Grey Li", data)

        # 测试更新设置，名称为空
        response = self.client.post(
            "/setting",
            data=dict(
                name="",
            ),
            follow_redirects=True,
        )
        data = response.get_data(as_text=True)
        self.assertNotIn("设置更新成功", data)
        self.assertIn("无效输入", data)

    # 测试虚拟数据
    def test_forge_command(self):
        with app.app_context():
            result = self.runner.invoke(forge)
            self.assertIn("数据填充完毕...", result.output)
            self.assertNotEqual(Movie.query.count(), 0)

    # 测试初始化数据库
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn("初始化数据库...", result.output)

    # 测试生成管理员账户
    def test_admin_command(self):
        with app.app_context():
            db.drop_all()
            db.create_all()
            result = self.runner.invoke(
                args=["admin", "--username", "grey", "--password", "123"]
            )
            self.assertIn("创建管理员用户中...", result.output)
            self.assertIn("完成！", result.output)
            self.assertEqual(User.query.count(), 1)
            self.assertEqual(User.query.first().username, "grey")
            self.assertTrue(User.query.first().validate_password("123"))

    # 测试更新管理员账户
    def test_admin_command_update(self):
        with app.app_context():
            # 使用 args 参数给出完整的命令参数列表
            result = self.runner.invoke(
                args=["admin", "--username", "peter", "--password", "456"]
            )
            self.assertIn("更新管理员用户中...", result.output)
            self.assertIn("完成！", result.output)
            self.assertEqual(User.query.count(), 1)
            self.assertEqual(User.query.first().username, "peter")
            self.assertTrue(User.query.first().validate_password("456"))


if __name__ == "__main__":
    unittest.main()
