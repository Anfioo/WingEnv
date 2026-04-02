from sys import path
from pathlib import Path

from wing_client.theme_cli import ThemeCLI

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

print("主题管理器测试启动")
ThemeCLI().execute_argv(["help"])
