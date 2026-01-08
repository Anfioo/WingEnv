from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.edit_ui import TextEditorApp

app = TextEditorApp()
print("文本编辑器测试启动")
print("提示：这是一个交互式应用，请使用键盘操作")
print("快捷键：Ctrl-S 保存 | Ctrl-Q 退出 | Ctrl-P 帮助")
app.run()