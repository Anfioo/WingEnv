from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts.progress_bar import formatters
from prompt_toolkit.styles import Style

from utils.style_loader import StyleLoader
from utils.ini.progress_bar_manager import ProgressBarManager


class ProgressBarConfig:
    """
    进度条配置类，支持多种预设格式器和样式风格。

    每个风格包含：
    - formatters: 进度条格式器列表
    - enabled: 是否启用样式（True使用样式，False不使用）
    - style_dict: 样式字典，优先级高于统一样式加载器
    """

    def __init__(self):
        self.style_loader = StyleLoader()  # 统一样式加载器实例
        self.manager = ProgressBarManager()

        self.styles = {
            "default": {
                "formatters": [
                    formatters.Label(),
                    formatters.Text(" "),
                    formatters.SpinningWheel(),
                    formatters.Text(" "),
                    formatters.Text(HTML("<tildes> ~~~ </tildes>")),
                    formatters.Bar(sym_a="█", sym_b="░", sym_c="·"),
                    formatters.Text(" 进度 "),
                    formatters.Rainbow(formatters.Percentage()),
                    formatters.Text(" | 剩余时间 "),
                    formatters.Rainbow(formatters.TimeLeft()),
                ],
                "enabled": True,
                "style_dict": None,  # 使用 StyleLoader 统一样式
            },
            "rainbow": {
                "formatters": [
                    formatters.Label(),
                    formatters.Text(" "),
                    formatters.Rainbow(formatters.Bar()),
                    formatters.Text(" 进度 "),
                    formatters.Rainbow(formatters.Percentage()),
                    formatters.Text(" | 剩余时间 "),
                    formatters.Rainbow(formatters.TimeLeft()),
                ],
                "enabled": False,
                "style_dict": {
                    "progressbar title": "fg:#61afef bold",
                    "item-title": "#e5c07b underline",
                    "percentage": "#98c379 bold",
                    "bar-a": "bg:#98c379",
                    "bar-b": "bg:#56b6c2",
                    "bar-c": "bg:#3e4452",
                    "tildes": "fg:#c678dd",
                    "time-left": "bg:#3e4452 fg:#abb2bf",
                    "spinning-wheel": "fg:#d19a66 bold",
                },
            },
            "simple": {
                "formatters": [
                    formatters.Label(),
                    formatters.Bar(),
                    formatters.Percentage(),

                ],
                "enabled": False,  # 不使用样式
                "style_dict": None,
            },
        }

    def get_config(self):

        """
        获取指定样式的配置，包括格式器和样式对象。

        :return: dict 包含 keys: "formatters" (list), "style" (Style 或 None)
        """
        cfg = self.styles.get(self.manager.get_progress_bar_theme(), self.styles["default"])
        enabled = cfg.get("enabled", True)
        style_dict = cfg.get("style_dict", None)

        if enabled:
            if style_dict is None:
                style = self.style_loader.get_style()
            else:
                # 这里确保传入的是 dict[str, str]
                if not isinstance(style_dict, dict):
                    raise TypeError(f"Expected style_dict to be dict but got {type(style_dict)}")
                style = Style.from_dict(style_dict)
        else:
            style = None

        return {
            "formatters": cfg["formatters"],
            "style": style,
        }

    def get_config_by_name(self, style_name: str):

        """
        获取指定样式的配置，包括格式器和样式对象。

        :return: dict 包含 keys: "formatters" (list), "style" (Style 或 None)
        """
        cfg = self.styles.get(style_name, self.styles["default"])
        enabled = cfg.get("enabled", True)
        style_dict = cfg.get("style_dict", None)

        if enabled:
            if style_dict is None:
                style = self.style_loader.get_style()
            else:
                # 这里确保传入的是 dict[str, str]
                if not isinstance(style_dict, dict):
                    raise TypeError(f"Expected style_dict to be dict but got {type(style_dict)}")
                style = Style.from_dict(style_dict)
        else:
            style = None

        return {
            "formatters": cfg["formatters"],
            "style": style,
        }
