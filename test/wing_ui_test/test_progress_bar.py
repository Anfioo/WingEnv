from sys import path
from pathlib import Path

from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.dialog_ui import WingUI
from loader.style_loader import StyleLoader

# 创建样式加载器和WingUI实例
style_loader = StyleLoader()
wing_ui = WingUI(style_loader)

import time

pb, iterator = wing_ui.get_progress_bar_context(
    iterable=range(100),
    task_description="测试进度条",
    title="测试进度条",
    total=100,
    use_true_color=True,
    use_style_name="rich"
)

with pb:
    for i in iterator:
        time.sleep(0.02)

print("进度条测试完成")

#
# def fake_download():
#     for _ in range(100):
#         time.sleep(0.05)
#         yield b"x" * 1024  # 1KB
#
#
# progress, it = wing_ui.get_download_progress_context_rich(
#     fake_download(),
#     task_description="下载模型文件",
#     total=100 * 1024,
# )
#
# for _ in it:
#     pass
