from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.setting_ui.progress_bar_main_ui import ProgressBarCLI

print("进度条主题管理器测试启动")
ProgressBarCLI().start()