from pathlib import Path
from typing import Optional, Dict

from utils.ini.ini_config_manager import IniConfigManager


class ThemeManager:
    def __init__(self):
        self.config = IniConfigManager()
        self.section_user = "user"
        self.section_theme = "theme"

    def add_theme(self, name: str, css_path: str):
        """添加新的主题映射"""
        path = Path(css_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"样式文件不存在: {path}")
        self.config.set_value(self.section_theme, name, str(path))

    def remove_theme(self, name: str):
        """删除主题映射（不删除 CSS 文件）"""
        self.config.remove_option(self.section_theme, name)
        current = self.get_current_theme()
        if current == name:
            self.set_current_theme("default")

    def list_themes(self) -> Dict[str, str]:
        """列出所有主题及其对应 CSS 路径"""
        return self.config.get_section_items(self.section_theme)

    def set_current_theme(self, name: str):
        """设置当前使用的主题"""
        if not self.config.has_option(self.section_theme, name):
            raise ValueError(f"不存在主题: {name}")
        self.config.set_value(self.section_user, "style", name)

    def get_current_theme(self) -> str:
        """获取当前主题名"""
        return self.config.get_value(self.section_user, "style", fallback="default")

    def get_current_theme_path(self) -> Optional[str]:
        """获取当前主题对应的 CSS 文件路径"""
        theme = self.get_current_theme()
        return self.config.get_value(self.section_theme, theme)

    def theme_exists(self, name: str) -> bool:
        """是否存在指定主题"""
        return self.config.has_option(self.section_theme, name)
