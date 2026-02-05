#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict, Any, Union, Optional, List, Tuple

from prompt_toolkit import HTML, prompt
from rich.align import Align
from rich.box import ROUNDED
from rich.panel import Panel

from wing_ui.dialog_ui import WingUI


class BaseConfigureFlowBuilder:
    """
    配置流程构建者，用于通过链式调用快速构建 UI 交互并收集配置数据。
    完全遵循 WingUI 的标准接口参数。
    """

    def __init__(self, wing_ui: WingUI):
        self.wing_ui = wing_ui
        from wing_utils.ui import console
        self._console = console
        self._data: Dict[str, Any] = {}

    def select_single_option(self, key: str, config: Dict[str, Any], title: str, text: str, ok_text: str = "✔ 确认",
                             cancel_text: str = "✖ 取消"):
        """单选对话框"""
        result = self.wing_ui.select_single_option_ui(config=config, title=title, text=text, ok_text=ok_text,
                                                      cancel_text=cancel_text)
        self._data[key] = result
        return self

    def pause(
            self,
            text: str = "按 Enter 继续..."
    ):
        print("> "+text)
        input()
        return self

    def select_multiple_options(self, key: str, config: Dict[str, Any], title: str, text: str, ok_text: str = "✔ 确认",
                                cancel_text: str = "✖ 取消"):
        """多选对话框"""
        result = self.wing_ui.select_multiple_options_ui(config=config, title=title, text=text, ok_text=ok_text,
                                                         cancel_text=cancel_text)
        self._data[key] = result
        return self

    def input_text(self, key: str, title: Union[str, HTML], text: Union[str, HTML], ok_text: str = "确认",
                   cancel_text: str = "取消", password: bool = False, default: str = ""):
        """文本输入对话框"""
        result = self.wing_ui.input_text_ui(title=title, text=text, ok_text=ok_text, cancel_text=cancel_text,
                                            password=password, default=default)
        self._data[key] = result
        return self

    def yes_no(self, key: str, title: str = "确认操作", text: str = "您确定吗？", yes_text: str = "是",
               no_text: str = "否"):
        """Yes/No 确认对话框"""
        result = self.wing_ui.yes_no_ui(title=title, text=text, yes_text=yes_text, no_text=no_text)
        self._data[key] = result
        return self

    def button(self, key: str, title: str = "请选择", text: str = "", buttons: List[Tuple[str, Any]] = None):
        """按钮选择对话框"""
        result = self.wing_ui.button_ui(title=title, text=text, buttons=buttons)
        self._data[key] = result
        return self

    def message(self, title: str = "提示", text: str = ""):
        """消息提示对话框（不收集数据）"""
        self.wing_ui.message_ui(title=title, text=text)
        return self

    def custom(self, callback=None):
        """
        执行自定义回调。
        callback 接收当前 builder 实例作为参数。
        """
        if callback:
            callback(self)
        return self

    def data(self) -> Dict[str, Any]:
        """返回收集到的所有配置数据"""
        return self._data
