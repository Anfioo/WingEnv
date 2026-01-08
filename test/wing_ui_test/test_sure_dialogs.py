from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.sure_dialogs import yes_no_ui

result = yes_no_ui(
    title="测试确认对话框",
    text="您确定要执行此操作吗？",
    yes_text="是",
    no_text="否"
)
print(f"确认结果: {result}")