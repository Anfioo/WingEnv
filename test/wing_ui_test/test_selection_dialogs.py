from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.selection_dialogs import select_single_option_ui, select_multiple_options_ui

config = {
    "option1": "选项1",
    "option2": ("选项2", "normal"),
    "option3": ("重要选项", "important"),
    "option4": ("普通选项", "ignore"),
}

result1 = select_single_option_ui(
    config=config,
    title="测试单选对话框",
    text="请选择一个选项："
)
print(f"单选结果: {result1}")

result2 = select_multiple_options_ui(
    config=config,
    title="测试多选对话框",
    text="请选择多个选项："
)
print(f"多选结果: {result2}")