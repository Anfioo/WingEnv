import time

from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.output import ColorDepth
from utils.progress_bar_config import ProgressBarConfig


def get_progress_bar_context(
    iterable,
    task_description="任务进行中",
    title="进度",
    total=None,
    use_true_color=True
):
    """
    创建一个统一样式的进度条上下文。
    """
    cfg = ProgressBarConfig()
    config = cfg.get_config()
    custom_formatters = config["formatters"]
    style = config["style"]

    color_depth = ColorDepth.DEPTH_24_BIT if use_true_color else ColorDepth.DEPTH_8_BIT

    pb = ProgressBar(
        title=title,
        formatters=custom_formatters,
        style=style,
        color_depth=color_depth
    )

    task = pb(iterable, label=task_description, total=total)
    return pb, task


# 示例：下载或处理任务

if __name__ == "__main__":
    get_progress_bar_context(
        iterable=range(20),
        fn=lambda _: time.sleep(0.1),
        task_description="📦 模拟解压中...",
        title="📥 下载任务",

    )
