from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.input_dialogs import input_text_ui

result = input_text_ui(
    title="测试输入对话框",
    text="请输入您的名字：",
    ok_text="确认",
    cancel_text="取消",
    default="默认名称"
)
print(f"输入结果: {result}")