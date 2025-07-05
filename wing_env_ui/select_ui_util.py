# WingEnvUI/select_util.py

from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog
from typing import List, Optional, Tuple


def select_from_list(options: List[str], title: str = "请选择", text: str = "请选择一个选项") -> Optional[
    Tuple[int, str]]:
    """
    弹出选择对话框，供用户从给定列表中选择一个项。

    Args:
        options (List[str]): 待选择的字符串列表
        title (str): 弹窗标题
        text (str): 提示文字

    Returns:
        Optional[Tuple[int, str]]: (index, value)，如果用户取消则返回 None
    """
    if not options:
        print("⚠️  没有可选项。")
        return None

    values = [(str(i), val) for i, val in enumerate(options)]

    result = radiolist_dialog(
        title=title,
        text=text,
        values=values
    ).run()

    if result is None:
        return None

    index = int(result)
    return index, options[index]


def multi_select_from_list(options: List[str], title: str = "请选择", text: str = "可多选（空格选择，回车确认）") -> \
        Optional[List[Tuple[int, str]]]:
    """
    弹出多选对话框，供用户从给定列表中选择多个项。

    Args:
        options (List[str]): 待选择的字符串列表
        title (str): 弹窗标题
        text (str): 提示文字

    Returns:
        Optional[List[Tuple[int, str]]]: 选中项的 (index, value) 列表，如果用户取消则返回 None
    """
    if not options:
        print("⚠️  没有可选项。")
        return None

    values = [(str(i), val) for i, val in enumerate(options)]

    result = checkboxlist_dialog(
        title=title,
        text=text,
        values=values
    ).run()

    if result is None:
        return None

    return [(int(i), options[int(i)]) for i in result]
