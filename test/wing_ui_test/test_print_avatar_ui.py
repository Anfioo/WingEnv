from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.print_avatar_ui import print_avatar

print("开始打印头像...")
print_avatar()
print("头像打印完成")