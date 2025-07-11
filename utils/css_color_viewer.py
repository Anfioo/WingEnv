import re
from prompt_toolkit import HTML, print_formatted_text
from pathlib import Path


class CssColorViewer:
    COLOR_PATTERN = re.compile(r'#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b')

    def __init__(self, css_file: str):
        self.css_path = Path(css_file)

        if not self.css_path.exists() or not self.css_path.is_file():
            raise FileNotFoundError(f"CSS 文件不存在: {css_file}")

    def extract_colors(self):
        text = self.css_path.read_text(encoding='utf-8')
        colors = set(match.group(0) for match in self.COLOR_PATTERN.finditer(text))
        return sorted(colors)

    def show_colors(self):
        colors = self.extract_colors()
        if not colors:
            print("未找到任何颜色。")
            return


        # 构造 HTML 字符串，每个颜色用对应前景色的 # 号表示
        fragments = []
        for color in colors:
            # 防止颜色太浅看不清，用黑色边框模拟（prompt_toolkit不支持直接边框，简单用空格分隔）
            fragments.append(f'<style fg="{color}">▀</style> ')

        print_formatted_text(f"< {self.css_path.name} >主题配色")
        print_formatted_text(HTML(''.join(fragments)))
