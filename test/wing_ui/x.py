from wing_ui.progress_bar import get_progress_bar_context
import time

pb, task = get_progress_bar_context(
    iterable=range(50),
    task_description="任务进行中",
    title="测试进度条",
    total=50,
    use_true_color=True
)

with pb:  # 这里是关键，启动上下文
    for _ in task:
        time.sleep(0.1)  # 模拟任务耗时
