#!/usr/bin/env python
"""
一个简单的记事本式文本编辑器示例。
"""

import datetime
from asyncio import Future, ensure_future

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    Float,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import DynamicLexer, PygmentsLexer
from prompt_toolkit.search import start_search
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    Label,
    MenuContainer,
    MenuItem,
    SearchToolbar,
    TextArea,
)

from utils.style_loader import StyleLoader


class AppState:
    """
    应用程序状态。
    """

    show_status_bar = True
    current_path = None


def get_left_status():
    return " 快捷键：Ctrl-S 保存 | Ctrl-C 复制 | Ctrl-D 粘贴 | Ctrl-Z 撤销 | Ctrl-Q 查找  | Ctrl-N 查找下一个  | Esc 退出  | Ctrl-P 显示说明"


def get_right_status():
    row = text_area.document.cursor_position_row + 1
    col = text_area.document.cursor_position_col + 1
    return f" {row}:{col} "


# 搜索栏
search_toolbar = SearchToolbar()

# 文本编辑区
text_area = TextArea(
    lexer=DynamicLexer(
        lambda: PygmentsLexer.from_filename(
            AppState.current_path or ".txt", sync_from_start=False
        )
    ),
    scrollbar=True,
    line_numbers=True,
    search_field=search_toolbar,
)


class TextInputDialog:
    def __init__(self, title="", label_text="", completer=None):
        self.future = Future()

        def accept_text(buf):
            get_app().layout.focus(ok_button)
            buf.complete_state = None
            return True

        def accept():
            self.future.set_result(self.text_input.text)

        def cancel():
            self.future.set_result(None)

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
            body=HSplit([
                Label(text=label_text),
                self.text_input,
            ]),
            buttons=[ok_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


class MessageDialog:
    def __init__(self, title, message):
        self.future = Future()

        def done():
            self.future.set_result(None)

        ok_button = Button(text="确定", handler=done)
        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=message)]),
            buttons=[ok_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


body = HSplit([
    text_area,
    search_toolbar,
    ConditionalContainer(
        content=VSplit([
            Window(
                FormattedTextControl(get_left_status),
                style="class:status",
            ),
            Window(
                FormattedTextControl(get_right_status),
                style="class:status.right",
                width=9,
                align=WindowAlign.RIGHT,
            ),
        ], height=1),
        filter=Condition(lambda: AppState.show_status_bar),
    ),
])

# 全局快捷键
kb = KeyBindings()


# Ctrl+S 保存
@kb.add("c-s")
def _(event):
    cmd_save()


# Ctrl+M 状态栏
@kb.add("c-p")
def _(event):
    cmd_toggle_status()


# Ctrl+C 改为复制
@kb.add("c-c")
def _(event):
    cmd_copy()


# Ctrl+D 粘贴
@kb.add("c-d")
def _(event):
    cmd_paste()


# Ctrl+Z 撤销
@kb.add("c-z")
def _(event):
    cmd_undo()


# Ctrl+X 剪切
@kb.add("c-x")
def _(event):
    cmd_cut()


# Ctrl+A 全选
@kb.add("c-a")
def _(event):
    cmd_select_all()


@kb.add("c-q")
def _(event):
    cmd_find()


@kb.add(Keys.Escape)
def _(event):
    cmd_exit()

@kb.add("c-n")
def _(event):
    cmd_find_next()




# 对话框显示辅助函数
async def show_dialog(dialog):
    float_ = Float(content=dialog)
    root.floats.insert(0, float_)
    app = get_app()
    prev = app.layout.current_window
    app.layout.focus(dialog)
    result = await dialog.future
    app.layout.focus(prev)
    if float_ in root.floats:
        root.floats.remove(float_)
    return result


# 菜单命令

def cmd_new():
    text_area.text = ""


def cmd_open():
    async def _open():
        dlg = TextInputDialog(
            title="打开文件",
            label_text="输入文件路径：",
            completer=PathCompleter(),
        )
        path = await show_dialog(dlg)
        AppState.current_path = path
        if path:
            try:
                with open(path, "rb") as f:
                    text_area.text = f.read().decode("utf-8", errors="ignore")
            except OSError as e:
                show_message("错误", str(e))

    ensure_future(_open())


def cmd_exit():
    get_app().exit()


def cmd_save():
    if not AppState.current_path:
        return cmd_save_as()
    try:
        with open(AppState.current_path, "w", encoding="utf-8") as f:
            f.write(text_area.text)
        show_message("保存成功", f"已保存到: {AppState.current_path}")
    except Exception as e:
        show_message("保存失败", str(e))


def cmd_save_as():
    async def _save_as():
        dlg = TextInputDialog(
            title="另存为",
            label_text="输入保存路径：",
            completer=PathCompleter(),
        )
        path = await show_dialog(dlg)
        if path:
            AppState.current_path = path
            cmd_save()

    ensure_future(_save_as())


def cmd_undo(): text_area.buffer.undo()


def cmd_cut():
    data = text_area.buffer.cut_selection()
    get_app().clipboard.set_data(data)


def cmd_copy():
    data = text_area.buffer.copy_selection()
    get_app().clipboard.set_data(data)


def cmd_select_all():
    buf = text_area.buffer
    buf.cursor_position = 0
    buf.start_selection()
    buf.cursor_position = len(buf.text)


def cmd_paste(): text_area.buffer.paste_clipboard_data(get_app().clipboard.get_data())


def cmd_delete(): text_area.buffer.cut_selection()


def cmd_find(): start_search(text_area.control)


def cmd_find_next():
    state = get_app().current_search_state
    pos = text_area.buffer.get_search_position(state, include_current_position=False)
    text_area.buffer.cursor_position = pos


def cmd_replace():
    # 简单示例：先查找，再替换
    pass


def cmd_goto():
    async def _goto():
        dlg = TextInputDialog(title="转到行", label_text="行号：")
        ln = await show_dialog(dlg)
        try:
            num = int(ln)
            idx = text_area.buffer.document.translate_row_col_to_index(num - 1, 0)
            text_area.buffer.cursor_position = idx
        except:
            show_message("无效行号", "请输入有效的整数行号。")

    ensure_future(_goto())


def cmd_time_date():
    now = datetime.datetime.now().isoformat()
    text_area.buffer.insert_text(now)


def cmd_toggle_status():
    AppState.show_status_bar = not AppState.show_status_bar


def show_message(title, msg):
    async def _msg():
        dlg = MessageDialog(title, msg)
        await show_dialog(dlg)

    ensure_future(_msg())
def cmd_done():
    cmd_save()
    show_message("完成", f"配置处理完成: {AppState.current_path or '未命名'}")
    cmd_exit()


# 菜单容器
root = MenuContainer(
    body=body,
    menu_items=[
        MenuItem("文件", children=[
            MenuItem("新建", handler=cmd_new),
            MenuItem("打开", handler=cmd_open),
            MenuItem("保存", handler=cmd_save),
            MenuItem("另存为", handler=cmd_save_as),
            MenuItem("-", disabled=True),
            MenuItem("退出", handler=cmd_exit),
        ]),
        MenuItem("编辑", children=[
            MenuItem("撤销", handler=cmd_undo),
            MenuItem("剪切", handler=cmd_cut),
            MenuItem("复制", handler=cmd_copy),
            MenuItem("粘贴", handler=cmd_paste),
            MenuItem("删除", handler=cmd_delete),
            MenuItem("-", disabled=True),
            MenuItem("查找", handler=cmd_find),
            MenuItem("查找下一个", handler=cmd_find_next),
            MenuItem("替换", handler=cmd_replace),
            MenuItem("转到", handler=cmd_goto),
            MenuItem("全选", handler=cmd_select_all),
            MenuItem("时间/日期", handler=cmd_time_date),
        ]),
        MenuItem("视图", children=[
            MenuItem("状态栏", handler=cmd_toggle_status),
        ]),
        MenuItem("关于", children=[
            MenuItem("关于本软件", handler=lambda: show_message("关于", "文本编辑演示。\n作者: Anfioo"))]),
    ],
    floats=[
        Float(
            xcursor=True,
            ycursor=True,
            content=CompletionsMenu(max_height=16, scroll_offset=1),
        ),
        # 顶部右侧“完成”按钮
        Float(
            top=0,
            right=2,
            content=Button(text="完成", handler=cmd_done),
        ),
    ],
    key_bindings=kb,
)

loader = StyleLoader()
style = loader.get_style()

# 应用布局
layout = Layout(root, focused_element=text_area)

app = Application(
    layout=layout,
    enable_page_navigation_bindings=True,
    style=style,
    mouse_support=True,
    full_screen=True,
)


def main():
    app.run()


if __name__ == "__main__":
    main()
