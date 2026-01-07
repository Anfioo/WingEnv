from prompt_toolkit.shortcuts import yes_no_dialog
from typing import Union
from prompt_toolkit import HTML
from loader.style_loader import StyleLoader


def yes_no_ui(
        title: Union[str, HTML] = "确认操作",
        text: Union[str, HTML] = "您确定吗？",
        yes_text: str = "是",
        no_text: str = "否"
) -> bool:
    """
    显示一个 Yes/No 对话框，使用统一样式，支持 HTML 富文本。

    :return: True 表示确认（Yes），False 表示取消（No）
    """
    style = StyleLoader().get_style()

    return yes_no_dialog(
        title=title,
        text=text,
        yes_text=yes_text,
        no_text=no_text,
        style=style
    ).run()

