# text_editor.py

import datetime
from asyncio import Future, ensure_future
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import (
    ConditionalContainer, Float, HSplit, VSplit, Window, WindowAlign
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import DynamicLexer, PygmentsLexer
from prompt_toolkit.search import start_search
from prompt_toolkit.widgets import (
    Button, Dialog, Label, MenuContainer, MenuItem,
    SearchToolbar, TextArea
)

from utils.style_loader import StyleLoader


class TextEditorApp:
    class AppState:
        show_status_bar = True
        current_path = None

    def __init__(self, path=None):
        self.AppState = TextEditorApp.AppState
        self.AppState.current_path = path
        self.search_toolbar = SearchToolbar()
        self.text_area = TextArea(
            lexer=DynamicLexer(
                lambda: PygmentsLexer.from_filename(
                    self.AppState.current_path or ".txt", sync_from_start=False
                )
            ),
            scrollbar=True,
            line_numbers=True,
            search_field=self.search_toolbar,
        )
        self.show_open_disabled = True
        if path is None:
            self.show_open_disabled = False

        self.kb = KeyBindings()
        self._register_key_bindings()
        self.body = self._create_body()
        self.root = self._create_root()
        self.layout = Layout(self.root, focused_element=self.text_area)
        self.style = StyleLoader().get_style()
        self.app = Application(
            layout=self.layout,
            enable_page_navigation_bindings=True,
            style=self.style,
            mouse_support=True,
            full_screen=True,
        )
        if path:
            self._load_file(path)

    def _get_left_status(self):
        return (
            " 快捷键：Ctrl-S 保存 | Ctrl-C 复制 | Ctrl-D 粘贴 | Ctrl-Z 撤销 | Ctrl-X 剪切\n"
            "         Ctrl-Q 查找 | Ctrl-N 查找下一个 | Ctrl-A 全选 | Ctrl-P 帮助 | Esc 退出"
        )

    def _get_right_status(self):
        row = self.text_area.document.cursor_position_row + 1
        col = self.text_area.document.cursor_position_col + 1
        return f" {row}:{col} "

    def _create_body(self):
        return HSplit([
            self.text_area,
            self.search_toolbar,
            ConditionalContainer(
                content=VSplit([
                    Window(
                        FormattedTextControl(self._get_left_status),
                        style="class:status"
                    ),
                    Window(
                        FormattedTextControl(self._get_right_status),
                        style="class:status.right",
                        width=9,
                        align=WindowAlign.RIGHT,
                    ),
                ], height=2),
                filter=Condition(lambda: self.AppState.show_status_bar),
            ),
        ])

    def _create_root(self):
        return MenuContainer(
            body=self.body,
            menu_items=[
                MenuItem("文件", children=[
                    MenuItem("新建", handler=self.cmd_new, disabled=self.show_open_disabled),
                    MenuItem("打开", handler=self.cmd_open, disabled=self.show_open_disabled),
                    MenuItem("保存", handler=self.cmd_save),
                    MenuItem("另存为", handler=self.cmd_save_as),
                    MenuItem("-", disabled=True),
                    MenuItem("退出", handler=self.cmd_exit),
                ]),
                MenuItem("编辑", children=[
                    MenuItem("撤销", handler=self.cmd_undo, shortcut="c-z"),
                    MenuItem("剪切", handler=self.cmd_cut),
                    MenuItem("复制", handler=self.cmd_copy),
                    MenuItem("粘贴", handler=self.cmd_paste),
                    MenuItem("删除", handler=self.cmd_delete),
                    MenuItem("-", disabled=True),
                    MenuItem("查找", handler=self.cmd_find),
                    MenuItem("查找下一个", handler=self.cmd_find_next),
                    MenuItem("替换", handler=self.cmd_replace),
                    MenuItem("转到", handler=self.cmd_goto),
                    MenuItem("全选", handler=self.cmd_select_all),
                    MenuItem("时间/日期", handler=self.cmd_time_date),
                ]),
                MenuItem("视图", children=[
                    MenuItem("状态栏", handler=self.cmd_toggle_status),
                ]),
                MenuItem("关于", children=[
                    MenuItem("关于本软件", handler=lambda: self.show_message("关于", "文本编辑演示。\n作者: Anfioo"))
                ]),
            ],
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(max_height=16, scroll_offset=1),
                )
            ],
            key_bindings=self.kb,
        )

    def _register_key_bindings(self):
        @self.kb.add("c-s")
        def _(event): self.cmd_save()

        @self.kb.add("c-p")
        def _(event): self.cmd_toggle_status()

        @self.kb.add("c-c")
        def _(event): self.cmd_copy()

        @self.kb.add("c-d")
        def _(event): self.cmd_paste()

        @self.kb.add("c-z")
        def _(event): self.cmd_undo()

        @self.kb.add("c-x")
        def _(event): self.cmd_cut()

        @self.kb.add("c-a")
        def _(event): self.cmd_select_all()

        @self.kb.add("c-q")
        def _(event): self.cmd_find()

        @self.kb.add("c-n")
        def _(event): self.cmd_find_next()

        @self.kb.add(Keys.Escape)
        def _(event): self.cmd_exit()

    async def show_dialog(self, dialog):
        float_ = Float(content=dialog)
        self.root.floats.insert(0, float_)
        app = get_app()
        prev = app.layout.current_window
        app.layout.focus(dialog)
        result = await dialog.future
        app.layout.focus(prev)
        if float_ in self.root.floats:
            self.root.floats.remove(float_)
        return result

    class TextInputDialog:
        def __init__(self, title="", label_text="", completer=None):
            self.future = Future()

            def accept_text(buf):
                get_app().layout.focus(ok_button)
                buf.complete_state = None
                return True

            def accept(): self.future.set_result(self.text_input.text)

            def cancel(): self.future.set_result(None)

            self.text_input = TextArea(
                multiline=False,
                width=D(preferred=40),
                completer=completer,
                accept_handler=accept_text,
            )
            ok_button = Button(text="确定", handler=accept)
            cancel_button = Button(text="取消", handler=cancel)
            self.dialog = Dialog(
                title=title,
                body=HSplit([Label(text=label_text), self.text_input]),
                buttons=[ok_button, cancel_button],
                width=D(preferred=80),
                modal=True,
            )

        def __pt_container__(self): return self.dialog

    class MessageDialog:
        def __init__(self, title, message):
            self.future = Future()

            def done(): self.future.set_result(None)

            ok_button = Button(text="确定", handler=done)
            self.dialog = Dialog(
                title=title,
                body=HSplit([Label(text=message)]),
                buttons=[ok_button],
                width=D(preferred=80),
                modal=True,
            )

        def __pt_container__(self): return self.dialog

    def cmd_new(self):
        self.text_area.text = ""

    def cmd_open(self):
        async def _open():
            dlg = self.TextInputDialog(title="打开文件", label_text="输入文件路径：", completer=PathCompleter())
            path = await self.show_dialog(dlg)
            self.AppState.current_path = path
            if path:
                self._load_file(path)

        ensure_future(_open())

    def _load_file(self, path):
        try:
            with open(path, "rb") as f:
                self.text_area.text = f.read().decode("utf-8", errors="ignore")
        except OSError as e:
            self.show_message("错误", str(e))

    def cmd_exit(self):
        get_app().exit()

    def cmd_save(self):
        if not self.AppState.current_path:
            return self.cmd_save_as()
        try:
            with open(self.AppState.current_path, "w", encoding="utf-8") as f:
                f.write(self.text_area.text)
            self.show_message("保存成功", f"已保存到: {self.AppState.current_path}")
        except Exception as e:
            self.show_message("保存失败", str(e))

    def cmd_save_as(self):
        async def _save_as():
            dlg = self.TextInputDialog(title="另存为", label_text="输入保存路径：", completer=PathCompleter())
            path = await self.show_dialog(dlg)
            if path:
                self.AppState.current_path = path
                self.cmd_save()

        ensure_future(_save_as())

    def cmd_undo(self):
        self.text_area.buffer.undo()

    def cmd_cut(self):
        self._clipboard_set(self.text_area.buffer.cut_selection())

    def cmd_copy(self):
        self._clipboard_set(self.text_area.buffer.copy_selection())

    def cmd_select_all(self):
        buf = self.text_area.buffer
        buf.cursor_position = 0
        buf.start_selection()
        buf.cursor_position = len(buf.text)

    def cmd_paste(self):
        self.text_area.buffer.paste_clipboard_data(get_app().clipboard.get_data())

    def cmd_delete(self):
        self.text_area.buffer.cut_selection()

    def cmd_find(self):
        start_search(self.text_area.control)

    def cmd_find_next(self):
        state = get_app().current_search_state
        pos = self.text_area.buffer.get_search_position(state, include_current_position=False)
        self.text_area.buffer.cursor_position = pos

    def cmd_replace(self):
        pass  # 可扩展

    def cmd_goto(self):
        async def _goto():
            dlg = self.TextInputDialog(title="转到行", label_text="行号：")
            ln = await self.show_dialog(dlg)
            try:
                num = int(ln)
                idx = self.text_area.buffer.document.translate_row_col_to_index(num - 1, 0)
                self.text_area.buffer.cursor_position = idx
            except:
                self.show_message("无效行号", "请输入有效的整数行号。")

        ensure_future(_goto())

    def cmd_time_date(self):
        now = datetime.datetime.now().isoformat()
        self.text_area.buffer.insert_text(now)

    def cmd_toggle_status(self):
        self.AppState.show_status_bar = not self.AppState.show_status_bar

    def show_message(self, title, msg):
        async def _msg():
            dlg = self.MessageDialog(title, msg)
            await self.show_dialog(dlg)

        ensure_future(_msg())

    def _clipboard_set(self, data):
        get_app().clipboard.set_data(data)

    def run(self):
        self.app.run()















