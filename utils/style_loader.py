import re
from prompt_toolkit.styles import Style
from utils.ini.theme_manager import ThemeManager


class StyleLoader:
    def __init__(self):
        self.theme_manager = ThemeManager()
        self.css_path = self.theme_manager.get_current_theme_path()

        if not self.css_path:
            raise FileNotFoundError("未找到当前主题对应的 CSS 路径，请检查配置。")

        self.style_dict = self._parse_css()

    def _parse_css(self):
        style_dict = {}
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()

        # 匹配 .selector { ... } 的结构
        pattern = re.compile(r'\.([\w\.\- ]+)\s*\{\s*([^}]+)\s*\}', re.MULTILINE)

        for match in pattern.finditer(css):
            raw_class_name = match.group(1).strip()

            # ✅ 仅对这两种进行特殊处理
            if raw_class_name == 'dialog.shadow':
                class_name = 'dialog shadow'
            elif raw_class_name == 'dialog.body label':
                class_name = 'dialog.body label'
            elif raw_class_name == 'progressbar.title':
                class_name = 'progressbar title'
            else:
                class_name = raw_class_name  # 其他保持原样

            # 解析样式属性
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
        print(self.style_dict)
        return Style.from_dict(self.style_dict)
