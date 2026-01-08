from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.button_choice_dialogs import button_ui

result = button_ui(
    title="测试按钮对话框",
    text="这是一个测试按钮对话框",
    buttons=[("按钮1", "value1"), ("按钮2", "value2"), ("取消", None)]
)
print(f"选择结果: {result}")