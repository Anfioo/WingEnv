# wing_env/wing_ui/selection_dialogs.py
from typing import Dict, Union

from prompt_toolkit import HTML  # 导入HTML支持
from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog

from loader.style_loader import StyleLoader


def _convert_value(k, v):
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


def _deal_config(config, title, text):
    values = [_convert_value(k, v) for k, v in config.items()]

    # 加载样式
    style = StyleLoader().get_style()
    return values, title, text, style


def select_single_option_ui(config: Dict[str, Union[str, HTML, tuple]],
                         title: Union[str, HTML],
                         text: Union[str, HTML],
                         ok_text: str = "✔ 确认",
                         cancel_text: str = "✖ 取消"
                         ):
    """
    显示一个美化的复选框对话框，样式从 CSS 文件中加载。
    """
    values, title, text, style = _deal_config(config, title, text)

    return radiolist_dialog(
        title=title,
        text=text,
        ok_text=ok_text,
        cancel_text=cancel_text,
        values=values,
        style=style,
        default=None
    ).run()


def select_multiple_options_ui(config: Dict[str, Union[str, HTML, tuple]],
                            title: Union[str, HTML],
                            text: Union[str, HTML],
                            ok_text: str = "✔ 确认",
                            cancel_text: str = "✖ 取消"
                            ):
    """
    显示一个美化的复选框对话框，样式从 CSS 文件中加载。
    """

    values, title, text, style = _deal_config(config, title, text)

    return checkboxlist_dialog(
        title=title,
        text=text,
        ok_text=ok_text,
        cancel_text=cancel_text,
        values=values,
        style=style,
        default_values=[]
    ).run()
