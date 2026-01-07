from prompt_toolkit.shortcuts import button_dialog
from typing import Union, Sequence, Tuple, Any
from prompt_toolkit import HTML
from loader.style_loader import StyleLoader

from typing import Optional, Sequence, Tuple, Any


def button_ui(
        title: Union[str, HTML] = "请选择",
        text: Union[str, HTML] = "",
        buttons: Optional[Sequence[Tuple[str, Any]]] = None
):
    """
    显示一个支持样式的按钮对话框。

    :param title: 标题，支持 str 或 HTML。
    :param text: 正文内容，支持 str 或 HTML。
    :param buttons: 按钮列表，格式为 [(按钮文字, 返回值)]。
    """
    style = StyleLoader().get_style()

    if buttons is None:
        buttons = []

    return button_dialog(
        title=title,
        text=text,
        buttons=buttons,
        style=style
    ).run()


