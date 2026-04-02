import os
import re
import time
from datetime import datetime
from typing import Optional, Callable
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout as PTLayout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style


class RichFileBrowser:
    """
    Rich 风格文件浏览器
    支持：仅文件 / 仅目录 / 均可选 + 正则匹配选择
    主题：优先使用 StyleLoader 提供的主题，缺失的样式类使用 Catppuccin 后备配色
    """

    # 文件浏览器使用的样式类名
    # 这些类名将被映射到 StyleLoader 提供的样式类名
    STYLE_CLASSES = [
        "selected",  # 选中项
        "status-bar",  # 状态栏
        "title",  # 标题
        "header",  # 表头
        "dir",  # 目录
        "file",  # 文件
        "parent",  # 上级目录
        "size",  # 文件大小
        "time",  # 修改时间
        "error",  # 错误信息
        "info",  # 信息
        "message",  # 消息
    ]

    def __init__(
            self,
            style_loader,
            start_path: str = ".",
            select_mode: str = "both",
            file_filter: Optional[Callable] = None,
            title: Optional[str] = None,
            select_regex: Optional[str] = None,
            regex_match_fullpath: bool = False
    ):
        self.style_loader = style_loader

        self.title = title or "📂 文件浏览器"
        self.select_mode = select_mode.lower()
        self.file_filter = file_filter
        self.select_regex = re.compile(select_regex) if select_regex else None
        self.regex_match_fullpath = regex_match_fullpath

        self.current_path = os.path.abspath(start_path)
        self.selected_index = 0
        self.items = []

        self.history = [self.current_path]
        self.history_index = 0

        # 临时消息（基于时间戳自动过期）
        self.message = None
        self.message_expire = 0

        # 样式字典（将在 _get_style 中填充）
        self._style_dict = {}

        self.kb = KeyBindings()
        self._register_keys()

        self.layout = PTLayout(self._create_body())

        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            full_screen=True,
            mouse_support=True,
            refresh_interval=0.1,
            style=self._get_style()
        )

        self._refresh_items()

    # ------------------------------ 样式定义 ------------------------------
    def _get_style(self) -> Style:
        """直接从 StyleLoader 获取样式，文件浏览器样式类名映射到 StyleLoader 样式类名"""
        try:
            # 直接从 style_loader 获取 Style 对象
            style_obj = self.style_loader.get_style()

            # 获取样式字典（从 style_rules 转换或直接使用 style_dict）
            style_dict = {}
            if hasattr(style_obj, 'style_rules'):
                # style_rules 是列表格式 [(class_name, style_string), ...]
                style_dict = dict(style_obj.style_rules)
            elif hasattr(self.style_loader, 'style_dict'):
                # 或者直接从 style_loader 获取字典
                style_dict = self.style_loader.style_dict

            # 文件浏览器样式类名到 StyleLoader 样式类名的映射
            style_mapping = {
                "selected": "button.focused",  # 选中项 -> 按钮聚焦样式
                "status-bar": "status",  # 状态栏 -> 状态样式
                "title": "frame.label",  # 标题 -> 框架标签样式
                "header": "label",  # 表头 -> 标签样式
                "dir": "button",  # 目录 -> 按钮样式
                "file": "text-area",  # 文件 -> 文本区域样式
                "parent": "tildes",  # 上级目录 -> 波浪线样式
                "size": "percentage",  # 文件大小 -> 百分比样式
                "time": "time-left",  # 修改时间 -> 时间剩余样式
                "error": "error",  # 错误信息
                "info": "info",  # 信息
                "message": "message",  # 消息
            }

            # 创建文件浏览器专用的样式字典
            file_browser_styles = {}

            # 为每个文件浏览器样式类名创建映射
            for fb_class in self.STYLE_CLASSES:
                mapped_class = style_mapping.get(fb_class, fb_class)
                if mapped_class in style_dict:
                    # 使用映射的样式
                    file_browser_styles[fb_class] = style_dict[mapped_class]
                else:
                    # 如果没有找到映射的样式，使用一个简单的后备样式
                    if fb_class == "selected":
                        file_browser_styles[fb_class] = "reverse"
                    elif fb_class == "status-bar":
                        # 尝试从 dialog 或 frame 中提取颜色
                        bg_color = self._extract_color_from_style(style_dict, "dialog", "bg") or \
                                   self._extract_color_from_style(style_dict, "frame", "bg") or "#263238"
                        fg_color = self._extract_color_from_style(style_dict, "dialog", "fg") or \
                                   self._extract_color_from_style(style_dict, "frame", "fg") or "#eceff1"
                        file_browser_styles[fb_class] = f"bg:{bg_color} fg:{fg_color}"
                    elif fb_class == "title":
                        file_browser_styles[fb_class] = "bold"
                    else:
                        file_browser_styles[fb_class] = ""

            # 存储样式字典供其他方法使用
            self._style_dict = style_dict

            # 转换为 prompt_toolkit Style 对象
            return Style.from_dict(file_browser_styles)

        except Exception as e:
            # 如果出现错误，返回一个简单的默认样式
            import sys
            print(f"样式加载错误，使用默认样式: {e}", file=sys.stderr)

            # 创建最简单的默认样式
            default_styles = {
                "selected": "reverse",
                "status-bar": "reverse",
                "title": "bold",
            }
            # 为其他样式类名添加空样式
            for fb_class in self.STYLE_CLASSES:
                if fb_class not in default_styles:
                    default_styles[fb_class] = ""

            # 存储空的样式字典
            self._style_dict = {}

            return Style.from_dict(default_styles)

    # ------------------------------ 颜色提取辅助方法 ------------------------------
    def _extract_color_from_style(self, style_dict, target_class, color_type="bg"):
        """
        从样式字典中提取颜色
        style_dict: 样式字典
        target_class: 目标样式类名
        color_type: 颜色类型 ('bg', 'fg', 或其他)
        """
        if target_class not in style_dict:
            return None

        style_string = style_dict[target_class]
        # 解析样式字符串，查找颜色
        parts = style_string.split()
        for part in parts:
            if part.startswith(f"{color_type}:"):
                return part[3:]  # 去掉 "bg:" 或 "fg:" 前缀

        return None

    # ------------------------------ 文件操作 ------------------------------
    def _refresh_items(self):
        self.items = []
        try:
            parent_dir = os.path.dirname(self.current_path)
            if parent_dir != self.current_path:
                self.items.append(("..", "parent", True, "", ""))

            entries = os.listdir(self.current_path)
            dirs, files = [], []

            for name in entries:
                full_path = os.path.join(self.current_path, name)
                if not os.access(full_path, os.R_OK):
                    continue
                if os.path.isdir(full_path):
                    dirs.append(name)
                else:
                    if self.file_filter and not self.file_filter(full_path):
                        continue
                    files.append(name)

            dirs.sort(key=lambda x: x.lower())
            files.sort(key=lambda x: x.lower())

            for d in dirs:
                size, mtime = self._get_file_info(os.path.join(self.current_path, d))
                self.items.append((d, "dir", True, size, mtime))
            for f in files:
                size, mtime = self._get_file_info(os.path.join(self.current_path, f))
                self.items.append((f, "file", False, size, mtime))

        except Exception as e:
            self.items = [(f"⚠️ 错误: {str(e)}", "error", False, "", "")]

        self.selected_index = max(0, min(self.selected_index, len(self.items) - 1))

    def _navigate(self, path: str, record_history: bool = True):
        path = os.path.abspath(path)
        if not os.path.isdir(path) or not os.access(path, os.R_OK):
            return

        self.current_path = path
        if record_history:
            self.history = self.history[:self.history_index + 1]
            self.history.append(path)
            self.history_index = len(self.history) - 1
        self._refresh_items()

    def _get_file_info(self, path: str) -> tuple[str, str]:
        try:
            st = os.stat(path)
            size = st.st_size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 ** 2:
                size_str = f"{size / 1024:.1f} KB"
            elif size < 1024 ** 3:
                size_str = f"{size / 1024 ** 2:.1f} MB"
            else:
                size_str = f"{size / 1024 ** 3:.1f} GB"
            mtime = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
            return size_str, mtime
        except:
            return "—", "—"

    # ------------------------------ 正则匹配检查 ------------------------------
    def _match_regex(self, name: str, full_path: str) -> bool:
        if self.select_regex is None:
            return True
        target = full_path if self.regex_match_fullpath else name
        return bool(self.select_regex.search(target))

    # ------------------------------ UI 渲染 ------------------------------
    def _get_file_icon(self, is_dir: bool, name: str) -> str:
        if is_dir:
            return "📁"
        ext = os.path.splitext(name)[1].lower()
        icons = {
            ".py": "🐍", ".js": "📜", ".ts": "📘", ".java": "☕", ".cpp": "⚙️",
            ".html": "🌐", ".css": "🎨", ".json": "📋", ".xml": "📄",
            ".jpg": "🖼️", ".png": "🖼️", ".gif": "🎞️", ".svg": "📐",
            ".pdf": "📕", ".doc": "📘", ".docx": "📘", ".xls": "📊",
            ".txt": "📝", ".md": "📝", ".log": "📋",
            ".zip": "📦", ".rar": "📦", ".7z": "📦", ".tar": "📦",
            ".exe": "⚙️", ".sh": "🐚", ".bat": "💻",
            ".mp3": "🎵", ".mp4": "🎬", ".avi": "🎬", ".mkv": "🎬",
            ".git": "🔀", ".toml": "⚙️", ".yml": "📋",
        }
        return icons.get(ext, "📄")

    def _render_main(self) -> FormattedText:
        # 检查消息是否过期
        if self.message and time.time() > self.message_expire:
            self.message = None

        res = []

        # 标题栏
        title_text = f" {self.title} "
        res.append(("class:title", f"┌{'─' * (78 - len(title_text) - 2)}"))
        res.append(("class:title", f"{title_text}"))
        res.append(("class:title", f"{'─' * (78 - len(title_text) - 2)}┐\n"))

        # 表头
        headers = [
            ("class:header", "  "), ("class:header", "名称"), ("", " " * 33),
            ("class:header", "类型"), ("", " " * 4),
            ("class:header", "大小"), ("", " " * 6),
            ("class:header", "修改时间")
        ]
        for style, txt in headers:
            res.append((style, txt))
        res.append(("", "\n"))
        # 从样式字典中提取边框颜色
        border_color = self._extract_color_from_style(self._style_dict, "frame.border", "bg") or \
                       self._extract_color_from_style(self._style_dict, "tildes", "fg") or "#6c7086"
        res.append((f"fg:{border_color}", f"├{'─' * 32}┼{'─' * 6}┼{'─' * 10}┼{'─' * 16}┤\n"))

        # 文件列表
        for idx, (name, typ, is_dir, size, mtime) in enumerate(self.items):
            # 交替行背景色（如果用户样式未提供，则使用 surface1 作为背景）
            # 从样式字典中提取背景颜色
            odd_bg = self._extract_color_from_style(self._style_dict, "checkbox-list", "bg") or \
                     self._extract_color_from_style(self._style_dict, "menu", "bg") or "#45475a"
            even_bg = self._extract_color_from_style(self._style_dict, "dialog", "bg") or \
                      self._extract_color_from_style(self._style_dict, "frame", "bg") or "#1e1e2e"
            row_bg = f"bg:{odd_bg}" if idx % 2 == 1 else f"bg:{even_bg}"
            selected = idx == self.selected_index
            prefix_style = "class:selected" if selected else row_bg

            cursor = "▶ " if selected else "  "
            res.append((prefix_style, cursor))

            icon = self._get_file_icon(is_dir, name)
            name_style = "class:dir" if is_dir else ("class:parent" if typ == "parent" else "class:file")
            if selected:
                name_style = "class:selected"
            display_name = name if len(name) <= 28 else name[:25] + "..."
            res.append((prefix_style, f"{icon} "))
            res.append((name_style, display_name))
            res.append((prefix_style, " " * max(0, 32 - len(display_name))))

            # 类型
            if typ == "parent":
                t_str, t_style = "⬆上级", "class:parent"
            elif is_dir:
                t_str, t_style = "📂目录", "class:dir"
            else:
                t_str, t_style = "📄文件", "class:file"
            if selected:
                t_style = "class:selected"
            res.append((prefix_style, " "))
            res.append((t_style, t_str))
            res.append((prefix_style, " " * max(0, 7 - len(t_str))))

            # 大小
            size_pad = " " * (10 - len(size))
            res.append((prefix_style, f"{size_pad}"))
            res.append(("class:size", size))
            res.append((prefix_style, " "))

            # 时间
            res.append(("class:time", mtime))
            res.append((prefix_style, "\n"))

        res.append((f"fg:{border_color}", f"└{'─' * 32}┴{'─' * 6}┴{'─' * 10}┴{'─' * 16}┘\n"))

        # 临时消息（如果有）
        if self.message:
            res.append(("class:message", f"⚠️ {self.message}\n"))
        return res

    def _render_status(self) -> FormattedText:
        path = self.current_path
        if len(path) > 45:
            path = "…" + path[-44:]

        mode_map = {"file": "📄仅文件", "dir": "📁仅目录", "both": "📂文件/目录"}
        mode = mode_map.get(self.select_mode, "全部")

        total = len(self.items)
        scroll_pct = 0
        if total > 0:
            scroll_pct = int((self.selected_index + 1) / total * 100)

        status_items = [
            ("📂 路径:", path),
            ("⚙️ 模式:", mode),
            ("📋 项目:", str(total)),
            ("📍 位置:", f"{scroll_pct}%"),
        ]

        if self.select_regex:
            pattern = self.select_regex.pattern
            if len(pattern) > 20:
                pattern = pattern[:17] + "..."
            status_items.append(("🔍 正则:", pattern))

        res = [("class:status-bar", " ")]
        for label, value in status_items:
            res.append(("class:status-bar", f" {label} "))
            # 从样式字典中提取 cyan 颜色
            cyan_color = self._extract_color_from_style(self._style_dict, "percentage", "fg") or \
                         self._extract_color_from_style(self._style_dict, "cyan", "fg") or "#94e2d5"
            res.append((f"fg:{cyan_color}", f"{value} "))
            res.append(("class:status-bar", "│"))

        hints = " ↑↓ 选择  ↵ 进入  ←→ 历史  F5刷新  F10确认  ESC退出"
        used_len = sum(len(t) for _, t in res) + len(hints)
        fill = max(0, 78 - used_len)
        res.append(("class:status-bar", " " * fill))
        # 从样式字典中提取提示颜色
        hint_color = self._extract_color_from_style(self._style_dict, "spinning-wheel", "fg") or \
                     self._extract_color_from_style(self._style_dict, "peach", "fg") or "#fab387"
        res.append((f"fg:{hint_color}", hints))
        res.append(("class:status-bar", " "))
        return res

    def _create_body(self):
        main_win = Window(
            content=FormattedTextControl(self._render_main),
            always_hide_cursor=True
        )
        # 从样式字典中提取状态栏背景颜色
        status_bg = self._extract_color_from_style(self._style_dict, "status", "bg") or \
                    self._extract_color_from_style(self._style_dict, "dialog", "bg") or "#313244"

        status_win = Window(
            content=FormattedTextControl(self._render_status),
            height=1,
            style=f"bg:{status_bg}"
        )
        return HSplit([main_win, status_win])

    # ------------------------------ 键盘绑定 ------------------------------
    def _register_keys(self):
        @self.kb.add("up")
        def _(e): self.selected_index = max(0, self.selected_index - 1)

        @self.kb.add("down")
        def _(e): self.selected_index = min(len(self.items) - 1, self.selected_index + 1)

        @self.kb.add("pageup")
        def _(e): self.selected_index = max(0, self.selected_index - 10)

        @self.kb.add("pagedown")
        def _(e): self.selected_index = min(len(self.items) - 1, self.selected_index + 10)

        @self.kb.add("home")
        def _(e): self.selected_index = 0

        @self.kb.add("end")
        def _(e): self.selected_index = len(self.items) - 1

        @self.kb.add("enter")
        def _(e): self._on_enter()

        @self.kb.add("left")
        def _(e): self._go_back()

        @self.kb.add("right")
        def _(e): self._go_forward()

        @self.kb.add("f5")
        def _(e): self._refresh_items()

        @self.kb.add("f10")
        def _(e): self._confirm_select()

        @self.kb.add("escape")
        @self.kb.add("c-c")
        def _(e): e.app.exit()

    def _show_message(self, msg: str):
        """显示临时消息（1.5秒后自动清除）"""
        self.message = msg
        self.message_expire = time.time() + 1.5
        self.app.invalidate()

    def _on_enter(self):
        if not self.items:
            return
        name, typ, is_dir, _, _ = self.items[self.selected_index]
        if typ == "parent":
            self._navigate(os.path.dirname(self.current_path))
        elif is_dir:
            self._navigate(os.path.join(self.current_path, name))

    def _go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self._navigate(self.history[self.history_index], record_history=False)

    def _go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._navigate(self.history[self.history_index], record_history=False)

    def _confirm_select(self):
        if not self.items:
            return
        name, typ, is_dir, _, _ = self.items[self.selected_index]

        if typ in ("parent", "error"):
            self._show_message("不能选择上级目录或错误项")
            return

        full_path = os.path.join(self.current_path, name)

        if self.select_mode == "file" and is_dir:
            self._show_message("当前模式为「仅文件」，不能选择文件夹")
            return
        if self.select_mode == "dir" and not is_dir:
            self._show_message("当前模式为「仅目录」，不能选择文件")
            return

        if not self._match_regex(name, full_path):
            self._show_message(f"所选项目不匹配正则表达式: {self.select_regex.pattern if self.select_regex else ''}")
            return

        self.selected_result = full_path
        self.app.exit()

    # ------------------------------ 运行入口 ------------------------------
    def run(self) -> Optional[str]:
        self.selected_result = None
        self.app.run()
        return self.selected_result


# ------------------------------ 快捷调用函数 ------------------------------
def rich_browse_file(style_loader, start_path=".", title=None, select_regex=None, regex_match_fullpath=False) -> \
        Optional[str]:
    return RichFileBrowser(style_loader, start_path, "file", title=title,
                           select_regex=select_regex, regex_match_fullpath=regex_match_fullpath).run()


def rich_browse_dir(style_loader, start_path=".", title=None, select_regex=None, regex_match_fullpath=False) -> \
        Optional[str]:
    return RichFileBrowser(style_loader, start_path, "dir", title=title,
                           select_regex=select_regex, regex_match_fullpath=regex_match_fullpath).run()


def rich_browse_all(style_loader, start_path=".", title=None, select_regex=None, regex_match_fullpath=False) -> \
        Optional[str]:
    return RichFileBrowser(style_loader, start_path, "both", title=title,
                           select_regex=select_regex, regex_match_fullpath=regex_match_fullpath).run()


# ------------------------------ 测试 ------------------------------
if __name__ == "__main__":
    try:
        from loader.style_loader import StyleLoader

        style = StyleLoader()
    except ImportError:
        # 模拟一个空的 StyleLoader（仅用于演示）
        class DummyStyle:
            style_dict = {}


        style = DummyStyle()

    print("启动文件浏览器（支持正则匹配选择）…")
    result = rich_browse_all(style, title="✨ 正则选择示例", select_regex=r"\.(py|txt)$")
    print(f"\n✅ 最终选择：{result}")
    print(style.get_style().style_rules)

    print(style.style_dict)
