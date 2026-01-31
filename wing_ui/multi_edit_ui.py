#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
from asyncio import Future, ensure_future
from typing import Dict, List, Optional

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import (
    ConditionalContainer, Float, HSplit, VSplit, Window, WindowAlign, DynamicContainer
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import DynamicLexer, PygmentsLexer
from prompt_toolkit.search import start_search
from prompt_toolkit.widgets import (
    Button, Dialog, Label, MenuItem,
    SearchToolbar, TextArea, RadioList, Frame, Box
)
from prompt_toolkit.styles import Style

from loader.style_loader import StyleLoader
from wing_ui.patch.menu_item_fix import MenuContainerFix


class MyRadioList(RadioList):
    """自定义 RadioList，支持在值改变时回调"""

    def __init__(self, values, on_change=None):
        self._initialized = False
        self.on_change = on_change
        super().__init__(values)
        self._initialized = True

    def _handle_click(self, value):
        super()._handle_click(value)
        if self._initialized and self.on_change:
            self.on_change(value)

    @property
    def current_value(self):
        return self._current_value

    @current_value.setter
    def current_value(self, value):
        old_value = getattr(self, "_current_value", None)
        self._current_value = value
        # 只有在完全初始化后，且值真的改变时才触发回调
        if self._initialized and old_value != value and self.on_change:
            self.on_change(value)


class MultiFileEditor:
    def __init__(self, initial_paths: Optional[List[str]] = None):
        self.editors: Dict[str, TextArea] = {}
        self.file_paths: List[str] = []
        self.current_path: Optional[str] = None
        self.show_status_bar = True

        self.search_toolbar = SearchToolbar()

        # 使用自定义的 RadioList
        self.file_list = MyRadioList(
            values=[("none", "没有打开的文件")],
            on_change=self._on_file_selected
        )

        # 默认空状态窗口
        self.empty_window = Window(
            content=FormattedTextControl("请在菜单中选择'文件 -> 打开'来编辑文件，或者使用 Ctrl-O。"),
            align=WindowAlign.CENTER
        )

        # 预加载文件
        if initial_paths:
            if isinstance(initial_paths, str):
                initial_paths = [initial_paths]
            for path in initial_paths:
                if os.path.exists(path) and os.path.isfile(path):
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        self._add_editor(path, content)
                    except Exception:
                        pass

        # 布局
        self.kb = KeyBindings()
        self._register_key_bindings()

        self.body = self._create_body()
        self.root = self._create_root()

        self.style_loader = StyleLoader()
        self.style = self.style_loader.get_style()

        self.layout = Layout(self.root)

        # 初始焦点设置
        if self.file_paths:
            # 如果有预加载文件，设置初始焦点到第一个编辑器
            self.current_path = self.file_paths[0]
            self.file_list.current_value = self.current_path
            self.layout.focus(self.editors[self.current_path])
        else:
            self.layout.focus(self.file_list)

        self.app = Application(
            layout=self.layout,
            enable_page_navigation_bindings=True,
            style=self.style,
            mouse_support=True,
            full_screen=True,
            key_bindings=self.kb,
        )

    def _on_file_selected(self, path):
        """当左侧文件列表选择改变时的回调"""
        if path and path != "none" and path in self.editors:
            try:
                app = get_app()
            except Exception:
                # 如果 app 尚未启动（例如在 __init__ 期间），直接返回
                return

            if app:
                # 1. 立即标记布局失效
                app.invalidate()

                # 2. 自动将焦点从列表移至编辑器
                # 只有当 app 已经在运行时才尝试聚焦，否则会报 Window does not appear in the layout 错误
                if app.is_running:
                    try:
                        editor = self.editors[path]
                        app.layout.focus(editor)
                    except (ValueError, AssertionError):
                        pass

                # 3. 异步再次刷新，确保鼠标命中测试（Hit-testing）地图已更新
                if hasattr(app, "loop") and app.loop is not None:
                    def force_refresh():
                        try:
                            app.invalidate()
                            # 再次确认焦点，防止 DynamicContainer 切换瞬间丢失焦点
                            if app.layout.current_window not in [e.window for e in self.editors.values()]:
                                app.layout.focus(self.editors[self.file_list.current_value])
                        except Exception:
                            pass

                    app.loop.call_soon(force_refresh)

    def _create_body(self):
        # 缓存容器，避免 DynamicContainer 每次都重新计算
        self._container_cache = {}

        def get_current_editor_container():
            # 安全检查：确保 file_list 已初始化
            if not hasattr(self, "file_list"):
                return self.empty_window

            selected_path = self.file_list.current_value

            if not selected_path or selected_path == "none" or selected_path not in self.editors:
                return self.empty_window

            # 同步 current_path
            if self.current_path != selected_path:
                self.current_path = selected_path

            return self.editors[selected_path]

        editor_container = DynamicContainer(get_current_editor_container)

        return HSplit([
            VSplit([
                Frame(
                    title="已打开文件",
                    body=self.file_list,
                    width=25
                ),
                Frame(
                    title=lambda: self.current_path or "未命名",
                    body=HSplit([
                        editor_container,
                        self.search_toolbar,
                    ])
                )
            ], height=D()),
            # 状态栏
            ConditionalContainer(
                content=VSplit([
                    Window(
                        FormattedTextControl(self._get_left_status),
                        style="class:status"
                    ),
                    Window(
                        FormattedTextControl(self._get_right_status),
                        style="class:status.right",
                        width=12,
                        align=WindowAlign.RIGHT,
                    ),
                ], height=2),
                filter=Condition(lambda: self.show_status_bar),
            ),
        ])

    def _get_left_status(self):
        return (
            " 快捷键: Ctrl-S 保存 | Ctrl-C 复制 | Ctrl-D 粘贴 | Ctrl-Z 撤销 | Ctrl-X 剪切\n"
            "         Ctrl-Q 查找 | Ctrl-N 查找下一个 | Ctrl-A 全选 | Ctrl-P 状态栏 | Esc 退出"
        )

    def _get_right_status(self):
        if not self.current_path or self.current_path not in self.editors:
            return " 0:0 "
        editor = self.editors[self.current_path]
        row = editor.document.cursor_position_row + 1
        col = editor.document.cursor_position_col + 1
        return f" {row}:{col} "

    def _create_root(self):
        return MenuContainerFix(
            body=self.body,
            menu_items=[
                MenuItem("文件", children=[
                    MenuItem("新建", handler=self.cmd_new),
                    MenuItem("打开", handler=self.cmd_open),
                    MenuItem("保存", handler=self.cmd_save),
                    MenuItem("另存为", handler=self.cmd_save_as),
                    MenuItem("关闭当前文件", handler=self.cmd_close),
                    MenuItem("-", disabled=True),
                    MenuItem("退出", handler=self.cmd_exit),
                ]),
                MenuItem("编辑", children=[
                    MenuItem("撤销", handler=self.cmd_undo),
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
                    MenuItem("关于本软件", handler=lambda: self.show_message("关于", "多文件编辑器\n作者: Anfioo"))
                ]),
            ],
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(max_height=16, scroll_offset=1),
                )
            ],
        )

    def _register_key_bindings(self):
        @self.kb.add("c-o")
        def _(event):
            self.cmd_open()

        @self.kb.add("c-s")
        def _(event):
            self.cmd_save()

        @self.kb.add("c-w")
        def _(event):
            self.cmd_close()

        @self.kb.add("c-q")
        def _(event):
            self.cmd_find()

        @self.kb.add("c-n")
        def _(event):
            self.cmd_find_next()

        # 参考 edit_ui.py 补充快捷键
        @self.kb.add("c-z")
        def _(event):
            self.cmd_undo()

        @self.kb.add("c-a")
        def _(event):
            self.cmd_select_all()

        @self.kb.add("c-c")
        def _(event):
            self.cmd_copy()

        @self.kb.add("c-x")
        def _(event):
            self.cmd_cut()

        @self.kb.add("c-d")
        def _(event):
            self.cmd_paste()

        @self.kb.add("c-p")
        def _(event):
            self.cmd_toggle_status()

        @self.kb.add("tab")
        def _(event):
            event.app.layout.focus_next()

        @self.kb.add("s-tab")
        def _(event):
            event.app.layout.focus_previous()

        @self.kb.add(Keys.Escape)
        def _(event):
            self.cmd_exit()

        # 监听 RadioList 的变化
        @Condition
        def is_file_list_focused():
            return get_app().layout.has_focus(self.file_list)

        # 移除手动的 up/down 绑定，让 RadioList 处理，但我们需要一个方式在值改变时触发刷新
        # 实际上 RadioList.current_value 改变时，DynamicContainer 会在下一次渲染时检测到并更新
        # 为了更流畅，我们可以显式在渲染循环中保持刷新，或者通过 keybinding 触发

    def _add_editor(self, path: str, content: str = ""):
        if path in self.editors:
            self.current_path = path
            self.file_list.current_value = path
            return

        # 为大文件优化：如果文件很大，禁用 lexer 或使用同步
        lexer = None
        if path:
            try:
                lexer = PygmentsLexer.from_filename(path, sync_from_start=False)
            except:
                pass

        editor = TextArea(
            text=content,
            lexer=lexer,
            scrollbar=True,
            line_numbers=True,
            search_field=self.search_toolbar,
            # 优化：禁用一些耗时的实时计算
            preview_search=False,
        )
        self.editors[path] = editor
        self.file_paths.append(path)
        self._update_file_list()
        self.current_path = path
        self.file_list.current_value = path

    def _update_file_list(self):
        if not self.file_paths:
            self.file_list.values = [("none", "没有打开的文件")]
        else:
            # 保持 values 列表的稳定性
            new_values = [(path, os.path.basename(path)) for path in self.file_paths]
            if self.file_list.values != new_values:
                self.file_list.values = new_values

    # 命令实现
    def cmd_new(self):
        # 简单实现：未命名的文件使用 timestamp
        path = f"new_file_{datetime.datetime.now().strftime('%H%M%S')}.txt"
        self._add_editor(path)
        # 自动聚焦到编辑器
        if self.current_path in self.editors:
            get_app().layout.focus(self.editors[self.current_path])

    def cmd_open(self):
        async def _open():
            dlg = self.TextInputDialog(title="打开文件", label_text="输入文件路径：", completer=PathCompleter())
            path = await self.show_dialog(dlg)
            if path and os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    self._add_editor(path, content)
                    # 自动聚焦到编辑器
                    if self.current_path in self.editors:
                        get_app().layout.focus(self.editors[self.current_path])
                except Exception as e:
                    self.show_message("错误", str(e))
            elif path:
                self.show_message("错误", "文件不存在")

        ensure_future(_open())

    def cmd_save(self):
        if not self.current_path:
            return
        editor = self.editors[self.current_path]
        try:
            with open(self.current_path, "w", encoding="utf-8") as f:
                f.write(editor.text)
            self.show_message("成功", f"已保存: {self.current_path}")
        except Exception as e:
            self.show_message("错误", str(e))

    def cmd_save_as(self):
        if not self.current_path:
            return

        async def _save_as():
            dlg = self.TextInputDialog(title="另存为", label_text="输入新路径：", completer=PathCompleter())
            new_path = await self.show_dialog(dlg)
            if new_path:
                editor = self.editors[self.current_path]
                try:
                    with open(new_path, "w", encoding="utf-8") as f:
                        f.write(editor.text)
                    # 替换旧的编辑器路径
                    content = editor.text
                    self.cmd_close()
                    self._add_editor(new_path, content)
                except Exception as e:
                    self.show_message("错误", str(e))

        ensure_future(_save_as())

    def cmd_close(self):
        if not self.current_path:
            return
        path_to_close = self.current_path
        del self.editors[path_to_close]
        self.file_paths.remove(path_to_close)
        self._update_file_list()

        app = get_app()
        if self.file_paths:
            self.current_path = self.file_paths[0]
            self.file_list.current_value = self.current_path
            # 自动聚焦到新的当前文件
            if app and self.current_path in self.editors:
                app.layout.focus(self.editors[self.current_path])
        else:
            self.current_path = None
            self.file_list.current_value = "none"
            # 当所有文件关闭时，将焦点移至文件列表，
            # 这样用户可以通过快捷键或菜单继续操作，且鼠标不会因失去目标而失效
            if app:
                app.layout.focus(self.file_list)

    def cmd_exit(self):
        get_app().exit()

    def cmd_undo(self):
        if self.current_path:
            self.editors[self.current_path].buffer.undo()

    def cmd_find(self):
        if self.current_path:
            start_search(self.editors[self.current_path].control)

    def cmd_find_next(self):
        if self.current_path:
            state = get_app().current_search_state
            pos = self.editors[self.current_path].buffer.get_search_position(state, include_current_position=False)
            self.editors[self.current_path].buffer.cursor_position = pos

    def cmd_select_all(self):
        if self.current_path:
            buf = self.editors[self.current_path].buffer
            buf.cursor_position = 0
            buf.start_selection()
            buf.cursor_position = len(buf.text)

    def cmd_time_date(self):
        if self.current_path:
            now = datetime.datetime.now().isoformat()
            self.editors[self.current_path].buffer.insert_text(now)

    def cmd_cut(self):
        if self.current_path:
            data = self.editors[self.current_path].buffer.cut_selection()
            get_app().clipboard.set_data(data)

    def cmd_copy(self):
        if self.current_path:
            data = self.editors[self.current_path].buffer.copy_selection()
            get_app().clipboard.set_data(data)

    def cmd_paste(self):
        if self.current_path:
            self.editors[self.current_path].buffer.paste_clipboard_data(get_app().clipboard.get_data())

    def cmd_delete(self):
        if self.current_path:
            self.editors[self.current_path].buffer.cut_selection()

    def cmd_replace(self):
        # 暂时作为占位符，可以后续扩展
        self.show_message("提示", "替换功能尚未实现，敬请期待。")

    def cmd_goto(self):
        if not self.current_path:
            return

        async def _goto():
            dlg = self.TextInputDialog(title="转到行", label_text="行号：")
            ln = await self.show_dialog(dlg)
            try:
                if ln:
                    num = int(ln)
                    editor = self.editors[self.current_path]
                    idx = editor.buffer.document.translate_row_col_to_index(num - 1, 0)
                    editor.buffer.cursor_position = idx
            except Exception:
                self.show_message("无效行号", "请输入有效的整数行号。")

        ensure_future(_goto())

    def cmd_toggle_status(self):
        self.show_status_bar = not self.show_status_bar

    # 对话框工具
    async def show_dialog(self, dialog):
        float_ = Float(content=dialog)
        self.root.floats.insert(0, float_)
        app = get_app()
        prev = app.layout.current_window
        app.layout.focus(dialog)
        result = await dialog.future
        try:
            if prev:
                app.layout.focus(prev)
        except (ValueError, AssertionError):
            # 如果之前的窗口已失效，尝试焦点到当前编辑器或文件列表
            if self.current_path and self.current_path in self.editors:
                app.layout.focus(self.editors[self.current_path])
            else:
                app.layout.focus(self.file_list)

        if float_ in self.root.floats:
            self.root.floats.remove(float_)
        return result

    def show_message(self, title, msg):
        async def _msg():
            dlg = self.MessageDialog(title, msg)
            await self.show_dialog(dlg)

        ensure_future(_msg())

    class TextInputDialog:
        def __init__(self, title="", label_text="", completer=None):
            self.future = Future()

            def accept(): self.future.set_result(self.text_input.text)

            def cancel(): self.future.set_result(None)

            self.text_input = TextArea(multiline=False, width=D(preferred=40), completer=completer,
                                       accept_handler=lambda b: accept())
            ok_button = Button(text="确定", handler=accept)
            cancel_button = Button(text="取消", handler=cancel)
            self.dialog = Dialog(
                title=title,
                body=HSplit([Label(text=label_text), self.text_input]),
                buttons=[ok_button, cancel_button],
                width=D(preferred=60),
                modal=True,
            )

        def __pt_container__(self): return self.dialog

    class MessageDialog:
        def __init__(self, title, message):
            self.future = Future()
            ok_button = Button(text="确定", handler=lambda: self.future.set_result(None))
            self.dialog = Dialog(
                title=title,
                body=HSplit([Label(text=message)]),
                buttons=[ok_button],
                width=D(preferred=60),
                modal=True,
            )

        def __pt_container__(self): return self.dialog

    def run(self):
        self.app.run()


if __name__ == "__main__":
    initial_files = [
        r"C:\Users\Anfioo\.we\we_config.ini",
        r"D:\Downloads\XDownDownload\helix-25.07.1-x86_64-windows\README.md"
    ]
    MultiFileEditor(initial_paths=initial_files).run()
