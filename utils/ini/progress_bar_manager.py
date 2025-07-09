from typing import Set
from utils.ini.ini_config_manager import IniConfigManager


class ProgressBarManager:
    """
    管理进度条样式主题配置（持久化到 ini 文件中）
    """
    def __init__(self):
        self.config = IniConfigManager()
        self.section_user = "user"
        self.available_themes: Set[str] = {"default", "rainbow", "simple"}

    def set_progress_bar_theme(self, theme_name: str):
        """设置当前使用的进度条主题"""
        if theme_name not in self.available_themes:
            raise ValueError(f"无效的 ProgressBar 主题: '{theme_name}'，可选: {', '.join(self.available_themes)}")
        self.config.set_value(self.section_user, "progress_bar", theme_name)

    def get_progress_bar_theme(self) -> str:
        """获取当前配置的进度条主题名称"""
        return self.config.get_value(self.section_user, "progress_bar", fallback="default")

    def get_available_themes(self) -> Set[str]:
        """返回支持的全部 ProgressBar 主题名称"""
        return self.available_themes





