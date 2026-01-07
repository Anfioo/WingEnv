from prompt_toolkit.shortcuts import message_dialog
from typing import Union
from prompt_toolkit import HTML


from loader.style_loader import StyleLoader


def message_ui(
    title: Union[str, HTML] = "提示",
    text: Union[str, HTML] = ""
) -> None:
    """
    显示一个支持样式的消息对话框，使用统一样式。
    """
    style = StyleLoader().get_style()

    return message_dialog(
        title=title,
        text=text,
        style=style
    ).run()


