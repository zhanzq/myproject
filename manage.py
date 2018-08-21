#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created by liaoyangyang1 on 2018/8/21 下午3:40.
"""


from flask_script import Manager, Server
from backend import create_app

app = create_app()

app.debug = app.config["DEBUG"]
# 获取根目录config.py的配置项
host = app.config["HOST"]
port = app.config["PORT"]

# Init manager object via app object
manager = Manager(app)

# Create a new commands: server
# This command will be run the Flask development_env server
manager.add_command("runserver", Server(host=host,port=port,threaded=True))

@manager.shell
def make_shell_context():
    """Create a python CLI.

    return: Default import object
    type: `Dict`
    """
    # 确保有导入 Flask app object，否则启动的 CLI 上下文中仍然没有 app 对象
    return dict(app=app)



if __name__ == '__main__':
    manager.run()