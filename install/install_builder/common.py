from loader import StyleLoader
from wing_ui import WingUI

style_loader = StyleLoader()
wing_ui = WingUI(style_loader)


def wing_dialog_selector(prompt, config):
    """
    使用 WingUI 的单选对话框作为选择器
    """
    return wing_ui.select_single_option_ui(
        config=config,
        title=prompt,
        text="请从下方列表中选择一项："
    )
