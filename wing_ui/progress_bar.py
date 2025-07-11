import time
from typing import Literal

from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.output import ColorDepth
from utils.progress_bar_config import ProgressBarConfig

StyleName = Literal["default", "rainbow", "simple"]


def get_progress_bar_context(
        iterable,
        task_description="任务进行中",
        title="进度",
        total=None,
        use_true_color=True,
        use_style_name: StyleName = None
):
    """
    创建一个统一样式的进度条上下文。
    """
    cfg = ProgressBarConfig()

    if use_style_name:
        config = cfg.get_config_by_name(use_style_name)
        custom_formatters = config["formatters"]
        style = config["style"]
    else:
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
