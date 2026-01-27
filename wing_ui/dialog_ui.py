from typing import Union, Optional, Literal

from prompt_toolkit import HTML
from prompt_toolkit.shortcuts import input_dialog, message_dialog, yes_no_dialog, button_dialog
from typing import Optional, Sequence, Tuple, Any

# wing_env/wing_ui/selection_dialogs.py
from typing import Dict, Union

from prompt_toolkit import HTML  # 导入HTML支持
from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog

from loader.style_loader import StyleLoader, ProgressBarStyleName
from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.output import ColorDepth


class WingUI:
    def __init__(self, styleLoader: StyleLoader):
        self.styleLoader = styleLoader
        self.style = styleLoader.get_style()

    def flash(self):
        self.styleLoader.flash()
        self.style = self.styleLoader.get_style()

    def input_text_ui(
            self,
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
        return input_dialog(
            title=title,
            text=text,
            ok_text=ok_text,
            cancel_text=cancel_text,
            password=password,
            style=self.style,
            default=default
        ).run()

    def message_ui(
            self,
            title: Union[str, HTML] = "提示",
            text: Union[str, HTML] = ""
    ) -> None:
        """
        显示一个支持样式的消息对话框，使用统一样式。
        """
        return message_dialog(
            title=title,
            text=text,
            style=self.style,
        ).run()

    def _convert_value(self, k, v):
        if isinstance(v, HTML):
            return k, v
        elif isinstance(v, tuple) and len(v) == 2:
            label, mode = v
            base = f'<style fg="#3e2723">{label}</style>'
            if mode == 'important':
                return k, HTML(f'<u>{base}</u>')
            elif mode == 'ignore':
                return k, HTML(f'<i>{base}</i>')
            else:
                return k, HTML(base)
        elif isinstance(v, str):
            return k, HTML(f'<style fg="#3e2723">{v}</style>')
        else:
            raise ValueError(f"不支持的配置类型: {v}")

    def _deal_config(self, config, title, text):
        values = [self._convert_value(k, v) for k, v in config.items()]

        # 加载样式

        return values, title, text

    def select_single_option_ui(self, config: Dict[str, Union[str, HTML, tuple]],
                                title: Union[str, HTML],
                                text: Union[str, HTML],
                                ok_text: str = "✔ 确认",
                                cancel_text: str = "✖ 取消"
                                ):
        """
        显示一个美化的复选框对话框，样式从 CSS 文件中加载。
        """
        values, title, text = self._deal_config(config, title, text)

        return radiolist_dialog(
            title=title,
            text=text,
            ok_text=ok_text,
            cancel_text=cancel_text,
            values=values,
            style=self.style,
            default=None
        ).run()

    def select_multiple_options_ui(self, config: Dict[str, Union[str, HTML, tuple]],
                                   title: Union[str, HTML],
                                   text: Union[str, HTML],
                                   ok_text: str = "✔ 确认",
                                   cancel_text: str = "✖ 取消"
                                   ):
        """
        显示一个美化的复选框对话框，样式从 CSS 文件中加载。
        """

        values, title, text = self._deal_config(config, title, text)

        return checkboxlist_dialog(
            title=title,
            text=text,
            ok_text=ok_text,
            cancel_text=cancel_text,
            values=values,
            style=self.style,
            default_values=[]
        ).run()

    def yes_no_ui(self,
                  title: Union[str, HTML] = "确认操作",
                  text: Union[str, HTML] = "您确定吗？",
                  yes_text: str = "是",
                  no_text: str = "否"
                  ) -> bool:
        """
        显示一个 Yes/No 对话框，使用统一样式，支持 HTML 富文本。

        :return: True 表示确认（Yes），False 表示取消（No）
        """
        return yes_no_dialog(
            title=title,
            text=text,
            yes_text=yes_text,
            no_text=no_text,
            style=self.style
        ).run()

    def button_ui(
            self,
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

        if buttons is None:
            buttons = []

        return button_dialog(
            title=title,
            text=text,
            buttons=buttons,
            style=self.style
        ).run()

    def get_progress_bar_context(
            self,
            iterable,
            task_description="任务进行中",
            title="进度",
            total=None,
            use_true_color=True,
            use_style_name: ProgressBarStyleName = None
    ):
        """
        创建一个统一样式的进度条上下文。
        """
        if use_style_name:
            config = self.styleLoader.get_pro_config(use_style_name)
            custom_formatters = config["formatters"]
            style = config["style"]
        else:
            config = self.styleLoader.get_pro_config()
            custom_formatters = config["formatters"]
            style = config["style"]

        color_depth = ColorDepth.DEPTH_24_BIT if use_true_color else ColorDepth.DEPTH_8_BIT

        pb = ProgressBar(
            title=title,
            formatters=custom_formatters,
            style=style,
            color_depth=color_depth
        )

        task = pb(iterable, label=task_description, total=total)
        return pb, task
