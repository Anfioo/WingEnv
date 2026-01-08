from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.message_dialogs import message_ui

message_ui(
    title="测试消息对话框",
    text="这是一个测试消息对话框，用于测试 wing_ui 组件。"
)
print("消息对话框测试完成")