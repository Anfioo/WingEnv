from typing import Union

from prompt_toolkit import HTML
from prompt_toolkit.shortcuts import input_dialog  # 添加导入

from utils.style_loader import StyleLoader


def input_text_ui(
    title: Union[str, HTML],
    text: Union[str, HTML],
    ok_text: str = "确认",
    cancel_text: str = "取消",
    password: bool = False,
    default: str = "",
):
    """
    显示一个支持样式的输入对话框，支持默认值与密码模式。
    """
    # 样式处理

    style = StyleLoader().get_style()

    return input_dialog(
        title=title,
        text=text,
        ok_text=ok_text,
        cancel_text=cancel_text,
        password=password,
        style=style,
        default=default
    ).run()
