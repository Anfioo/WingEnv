from typing import Set
from wing_utils import IniConfigUtils
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts.progress_bar import formatters


class ProgressBarManager:
    """
    管理进度条样式主题配置（持久化到 ini 文件中）
    """
    def __init__(self):
        self.config = IniConfigUtils()
        self.section_user = "user"
        self.available_themes: Set[str] = {"default", "rainbow", "simple"}

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

    def set_progress_bar_theme(self, theme_name: str):
        """设置当前使用的进度条主题"""
        if theme_name not in self.available_themes:
            raise ValueError(f"无效的 ProgressBar 主题: '{theme_name}'，可选: {', '.join(self.available_themes)}")
        self.config.set(self.section_user, "progress_bar", theme_name)

    def get_progress_bar_theme(self) -> str:
        """获取当前配置的进度条主题名称"""
        return self.config.get(self.section_user, "progress_bar", fallback="default")

    def get_available_themes(self) -> Set[str]:
        """返回支持的全部 ProgressBar 主题名称"""
        return self.available_themes





