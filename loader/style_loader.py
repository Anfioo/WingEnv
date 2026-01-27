import re
import threading
from typing import Literal

from prompt_toolkit.styles import Style

from loader.ini.progress_bar_manager import ProgressBarManager
from loader.ini.theme_manager import ThemeManager

ProgressBarStyleName = Literal["default", "rainbow", "simple"]


class StyleLoader:
    """
    样式加载器（单例）
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 防止 __init__ 被多次调用
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        self.theme_manager = ThemeManager()
        self.progress_bar_manager = ProgressBarManager()

        self.css_path = None
        self.style_dict = {}

        self.flash()  # ⭐ 初始化即加载

    # ================== 核心刷新方法 ==================

    def flash(self):
        """
        刷新主题 / CSS / Style（热更新）
        """
        with self._lock:
            css_path = self.theme_manager.get_current_theme_path()

            if not css_path:
                raise FileNotFoundError("未找到当前主题对应的 CSS 路径，请检查配置。")
            # 路径没变可以选择不重载（可选）
            if css_path == self.css_path:
                return

            self.css_path = css_path
            self.style_dict = self._parse_css()

    # ==================================================

    def _parse_css(self):
        style_dict = {}
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()

        pattern = re.compile(r'\.([\w\.\- ]+)\s*\{\s*([^}]+)\s*\}', re.MULTILINE)

        for match in pattern.finditer(css):
            raw_class_name = match.group(1).strip()

            if raw_class_name == 'dialog.shadow':
                class_name = 'dialog shadow'
            elif raw_class_name == 'dialog.body label':
                class_name = 'dialog.body label'
            elif raw_class_name == 'progressbar.title':
                class_name = 'progressbar title'
            else:
                class_name = raw_class_name

            rules = match.group(2).strip().split(';')
            properties = []
            for rule in rules:
                if ':' not in rule:
                    continue
                key, value = rule.strip().split(':', 1)
                key = key.strip()
                value = value.strip()
                if key == 'bold' and value.lower() == 'true':
                    properties.append('bold')
                elif key == 'underline' and value.lower() == 'true':
                    properties.append('underline')
                else:
                    properties.append(f"{key}:{value}")

            style_dict[class_name] = ' '.join(properties)

        return style_dict

    def get_style(self) -> Style:
        return Style.from_dict(self.style_dict)

    def get_pro_config(self, style_name: ProgressBarStyleName = None):
        if style_name is None:
            cfg = self.progress_bar_manager.styles.get(
                self.progress_bar_manager.get_progress_bar_theme(),
                self.progress_bar_manager.styles["default"]
            )
        else:
            cfg = self.progress_bar_manager.styles.get(
                style_name,
                self.progress_bar_manager.styles["default"]
            )

        enabled = cfg.get("enabled", True)
        style_dict = cfg.get("style_dict", None)

        if enabled:
            if style_dict is None:
                style = self.get_style()
            else:
                if not isinstance(style_dict, dict):
                    raise TypeError(f"Expected style_dict to be dict but got {type(style_dict)}")
                style = Style.from_dict(style_dict)
        else:
            style = None

        return {
            "formatters": cfg["formatters"],
            "style": style,
        }
