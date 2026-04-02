#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict, Any, Union, Optional, List, Tuple, Callable

from prompt_toolkit import HTML, prompt
from rich.align import Align
from rich.box import ROUNDED
from rich.panel import Panel

from wing_ui import TextDiffViewerApp
from wing_ui.dialog_ui import WingUI
from wing_utils.ui.diff_utils import DiffCalculator


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
        self._last_key: Optional[str] = None

    def select_single_option(self, key: str, config: Dict[str, Any], title: str, text: str, ok_text: str = "✔ 确认",
                             cancel_text: str = "✖ 取消") -> "BaseConfigureFlowBuilder":
        """单选对话框"""
        result = self.wing_ui.select_single_option_ui(config=config, title=title, text=text, ok_text=ok_text,
                                                      cancel_text=cancel_text)
        self._data[key] = result
        self._last_key = key
        return self

    def pause(
            self,
            text: str = "按 Enter 继续..."
    ):
        print("> " + text)
        input()
        return self

    def select_multiple_options(self, key: str, config: Dict[str, Any], title: str, text: str, ok_text: str = "✔ 确认",
                                cancel_text: str = "✖ 取消"):
        """多选对话框"""
        result = self.wing_ui.select_multiple_options_ui(config=config, title=title, text=text, ok_text=ok_text,
                                                         cancel_text=cancel_text)
        self._data[key] = result
        self._last_key = key
        return self

    def input_text(self, key: str, title: Union[str, HTML], text: Union[str, HTML], ok_text: str = "确认",
                   cancel_text: str = "取消", password: bool = False, default: str = ""):
        """文本输入对话框"""
        result = self.wing_ui.input_text_ui(title=title, text=text, ok_text=ok_text, cancel_text=cancel_text,
                                            password=password, default=default)
        self._data[key] = result
        self._last_key = key
        return self

    def yes_no(self, key: str, title: str = "确认操作", text: str = "您确定吗？", yes_text: str = "是",
               no_text: str = "否"):
        """Yes/No 确认对话框"""
        result = self.wing_ui.yes_no_ui(title=title, text=text, yes_text=yes_text, no_text=no_text)
        self._data[key] = result
        self._last_key = key
        return self

    def button(self, key: str, title: str = "请选择", text: str = "", buttons: List[Tuple[str, Any]] = None):
        """按钮选择对话框"""
        result = self.wing_ui.button_ui(title=title, text=text, buttons=buttons)
        self._data[key] = result
        self._last_key = key
        return self

    def message(self, title: str = "提示", text: str = ""):
        """消息提示对话框（不收集数据）"""
        self.wing_ui.message_ui(title=title, text=text)
        return self


    def branch(self, condition_func: Callable[[Dict, str], str],
               options: List[Tuple[str, Callable[["BaseConfigureFlowBuilder"], "BaseConfigureFlowBuilder"]]]) -> "BaseConfigureFlowBuilder":
        """
        分支核心逻辑：
        1. 按条件选分支 → 执行分支的子链 → 子链执行完回到主线
        2. 返回self，保证主线还能继续追加公共逻辑
        """
        if not callable(condition_func):
            raise TypeError("condition_func 必须是可调用的函数/方法，接收data并返回分支标识")
        if not isinstance(options, list) or len(options) == 0:
            raise ValueError("options 必须是非空的列表，元素为(分支标识, 分支执行函数)元组")
        for opt in options:
            if not isinstance(opt, tuple) or len(opt) != 2 or not isinstance(opt[0], str) or not callable(opt[1]):
                raise ValueError(f"options 元素格式错误，需为(str, callable)，当前错误元素：{opt}")

        # 1. 执行条件函数，选分支
        branch_key = condition_func(self._data, self._last_key)
        branch_map = {opt[0]: opt[1] for opt in options}

        # 2. 执行分支的子链（核心：分支函数返回builder，子链可无限扩展）
        if branch_key in branch_map:
            # 分支函数执行后，返回的还是当前builder（子链逻辑已追加）
            branch_map[branch_key](self)
        else:
            raise KeyError(f"无匹配分支：{branch_key}")

        # 3. 关键：返回self，主线可继续执行公共逻辑
        return self


    def diff_viewer(
            self,
            text1: str,
            text2: str,
            custom_diff_ranges: List[Tuple[Tuple[int, int], Tuple[int, int]]] = None,
    ):
        """
        显示文本差异查看器
        """
        if custom_diff_ranges is None:
            ranges = DiffCalculator.calculate_diff_ranges(text1, text2)
        else:
            ranges = custom_diff_ranges
        TextDiffViewerApp(text1, text2, ranges, self.wing_ui.get_style_loader()).run()
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
