from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.setting_ui.theme_main_ui import ThemeCLI

print("主题管理器测试启动")
ThemeCLI().start()