from typing import List, Any, Callable, Optional, Dict, Union, Self
import re

class Select:
    class First: pass
    class End: pass
    
    @staticmethod
    def Option(value: str) -> tuple[str, str]:
        """指定具体的选项值作为默认值"""
        return ("option", value)
        
    @staticmethod
    def Find(function: Callable[[List[Any]], Any]) -> tuple[str, Callable]:
        """使用自定义函数从选项列表中查找默认值"""
        return ("find", function)

class Block:
    class First: pass
    
    @staticmethod
    def Find(pattern: str) -> tuple[str, str]:
        """使用正则表达式模式屏蔽选项"""
        return ("pattern", pattern)

class Note:
    def __init__(self, text: str, mode: str = "normal", exact: bool = False):
        """
        为 UI 选项添加标注
        :param text: 匹配的文本
        :param mode: 标注模式 (important, warn, ignore, normal, recommend)
        :param exact: 是否精确匹配
        """
        self.text = text
        self.mode = mode # important, warn, ignore, normal, recommend
        self.exact = exact

class BaseFlowBuilder:
    def __init__(self, data: Any = None, selector: Callable = None):
        """
        构建者基类
        :param data: 初始数据
        :param selector: UI 选择器函数
        """
        self._raw_data = data
        self._current_options = []
        self._selected_value = None
        self._selector = selector
        self._metadata = {}
        self._skip_ui = False
        self._is_interrupted = False # 中断标记
        self._notes: List[Note] = []

    def deal(self, default: Any = None, block: List[Union[str, type]] = None, note: List[Note] = None) -> Self:
        """
        处理当前选项：屏蔽、自动选择、应用样式
        :param default: 默认选择逻辑 (Select.First, Select.End, Select.Option, Select.Find)
        :param block: 屏蔽逻辑列表 (字符串支持通配符 *, 或者 Block.First)
        :param note: 标注逻辑列表 (Note 对象列表)
        :return: Self (支持链式调用)
        """
        if self._is_interrupted or not self._current_options:
            return self

        # 1. 处理屏蔽 (Block)
        if block:
            new_options = []
            for opt in self._current_options:
                should_block = False
                for b in block:
                    if b == Block.First:
                        if opt == self._current_options[0]: should_block = True
                    elif isinstance(b, str):
                        # 支持通配符简单匹配
                        pattern = b.replace("*", ".*")
                        if re.match(f"^{pattern}$", str(opt)): should_block = True
                    if should_block: break
                if not should_block:
                    new_options.append(opt)
            self._current_options = new_options

        # 2. 处理 Note (UI样式)
        self._notes = note or []

        # 3. 处理默认选择 (Select)
        if default:
            target = None
            if default == Select.First:
                target = self._current_options[0] if self._current_options else None
            elif default == Select.End:
                target = self._current_options[-1] if self._current_options else None
            elif isinstance(default, tuple):
                type_, val = default
                if type_ == "option":
                    if val in self._current_options: target = val
                elif type_ == "find":
                    target = val(self._current_options)
            
            if target:
                self._selected_value = target
                self._skip_ui = True
        
        return self

    def select_ui(self, prompt: str = None) -> Self:
        """
        执行选择界面，让用户进行交互选择
        :param prompt: 提示文本，如果不提供则使用最后一次设置的提示
        :return: Self (支持链式调用)
        """
        if self._is_interrupted or self._skip_ui:
            self._skip_ui = False # 重置
            return self

        current_selector = self._selector
        if not current_selector:
            raise ValueError("No selector provided for UI")

        # 将选项和 Note 结合，准备给 UI
        ui_config = {}
        for opt in self._current_options:
            label = str(opt)
            mode = "normal"
            
            for n in self._notes:
                match = False
                if n.exact:
                    match = (n.text == label)
                else:
                    match = (n.text in label)
                
                if match:
                    mode = n.mode
                    if mode in ["important", "recommend", "warn"]:
                        break
            
            ui_config[opt] = (label, mode)

        display_prompt = prompt or getattr(self, "_last_prompt", "请选择")
        res = current_selector(display_prompt, ui_config)
        
        if res is None:
            self._is_interrupted = True
        else:
            self._selected_value = res
            
        return self

    def data(self) -> Optional[Dict[str, Any]]:
        """
        收集并返回最终生成的元数据字典
        :return: 元数据字典，如果流程被中断则返回 None
        """
        if self._is_interrupted:
            return None
        return self._metadata
