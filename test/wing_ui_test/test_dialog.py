from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.dialog_ui import WingUI
from loader.style_loader import StyleLoader

# 创建样式加载器和WingUI实例
style_loader = StyleLoader()
wing_ui = WingUI(style_loader)

# 测试输入对话框
print("=== 测试输入对话框 ===")
result_input = wing_ui.input_text_ui(
    title="测试输入对话框",
    text="请输入您的名字：",
    ok_text="确认",
    cancel_text="取消",
    default="默认名称"
)
print(f"输入结果: {result_input}")

# 测试密码输入对话框
print("\n=== 测试密码输入对话框 ===")
result_password = wing_ui.input_text_ui(
    title="测试密码输入",
    text="请输入密码：",
    ok_text="确认",
    cancel_text="取消",
    password=True,
    default=""
)
print(f"密码输入结果: {result_password}")

# 测试消息对话框
print("\n=== 测试消息对话框 ===")
wing_ui.message_ui(
    title="测试消息对话框",
    text="这是一个测试消息对话框，用于测试 wing_ui 组件。"
)
print("消息对话框测试完成")

# 测试单选对话框
print("\n=== 测试单选对话框 ===")
config = {
    "option1": "选项1",
    "option2": ("选项2", "normal"),
    "option3": ("重要选项", "important"),
    "option4": ("普通选项", "ignore"),
}
result_single = wing_ui.select_single_option_ui(
    config=config,
    title="测试单选对话框",
    text="请选择一个选项："
)
print(f"单选结果: {result_single}")

# 测试多选对话框
print("\n=== 测试多选对话框 ===")
result_multiple = wing_ui.select_multiple_options_ui(
    config=config,
    title="测试多选对话框",
    text="请选择多个选项："
)
print(f"多选结果: {result_multiple}")

# 测试Yes/No对话框
print("\n=== 测试Yes/No对话框 ===")
result_yes_no = wing_ui.yes_no_ui(
    title="测试确认对话框",
    text="您确定要执行此操作吗？",
    yes_text="是",
    no_text="否"
)
print(f"Yes/No结果: {result_yes_no}")

# 测试按钮对话框
print("\n=== 测试按钮对话框 ===")
buttons = [
    ("按钮1", "value1"),
    ("按钮2", "value2"),
    ("按钮3", "value3")
]
result_button = wing_ui.button_ui(
    title="测试按钮对话框",
    text="请选择一个按钮：",
    buttons=buttons
)
print(f"按钮选择结果: {result_button}")

print("\n所有测试完成！")
