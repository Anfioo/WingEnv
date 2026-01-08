from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

import time
from wing_ui.progress_bar import get_progress_bar_context

pb, iterable = get_progress_bar_context(
    iterable=range(100),
    task_description="测试进度条",
    title="测试进度条",
    total=100,
    use_true_color=True,
    use_style_name=None
)

with pb:
    for i in pb(iterable, label="测试进度条", total=100):
        time.sleep(0.02)

print("进度条测试完成")