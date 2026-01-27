import time
from typing import Tuple
from prompt_toolkit import HTML

# from wing_ui.button_choice_dialogs import button_ui
# from wing_ui.message_dialogs import message_ui
# from wing_ui.progress_bar import get_progress_bar_context
# from wing_ui.selection_dialogs import select_single_option_ui, select_multiple_options_ui
# from wing_ui.sure_dialogs import yes_no_ui
# from prompt_toolkit import HTML
#
# from wing_ui.input_dialogs import input_text_ui

from wing_ui.dialog_ui import WingUI
from loader.style_loader import StyleLoader, ProgressBarStyleName


# 创建样式加载器和WingUI实例

class TestUiUtils:
    def __init__(self, wing_ui: WingUI):
        self.wing_ui = wing_ui

    def button_choice_dialogs_test(self):
        # 定义按钮列表，每个按钮是一个 (显示文本, 返回值) 的元组
        buttons: Tuple[Tuple[str, str], ...] = (
            ("确定", "ok"),
            ("取消", "cancel"),
        )

        # 调用自定义的按钮对话框函数
        result = self.wing_ui.button_ui(
            title=HTML("<style bg='ansiblue' fg='white'>操作确认 - 主题预览测试</style>"),
            text=HTML("你 <b>确定</b> 要继续执行该操作吗？"),
            buttons=buttons
        )

        # 处理返回值
        print(f"用户选择: {result}")

    def input_dialogs_test(self):
        # 使用 HTML 样式设置标题和文本
        title = HTML("用户输入 - 主题预览测试")
        text = HTML("请输入你的 <b>用户名</b>:")

        # 弹出输入框，允许设置默认值、是否为密码等
        user_input = self.wing_ui.input_text_ui(
            title=title,
            text=text,
            default="admin",
            password=False,  # 设置 True 则为密码模式
            ok_text="登录",
            cancel_text="取消"
        )

        print(f"用户输入结果: {user_input}")

    def message_dialogs_test(self):
        self.wing_ui.message_ui(
            title=HTML("系统提示 - 主题预览测试"),
            text=HTML("操作 <b>成功</b>！请按回车继续。")
        )

    def test_single_select(self):
        config = {
            "opt1": "普通选项",
            "opt2": ("重要选项", "important"),
            "opt3": ("忽略选项", "ignore"),
            "opt4": HTML('<style fg="#0000ff">HTML 自定义项</style>')
        }

        result = self.wing_ui.select_single_option_ui(
            config=config,
            title=HTML("<b>请选择一个操作 - 主题预览测试</b>"),
            text=HTML("从下列<b>选项</b>中选择一项：")
        )

        print(f"用户选择了: {result}")

    def test_multi_select(self):
        config = {
            "feature1": "启用日志",
            "feature2": ("强制校验", "important"),
            "feature3": ("跳过缓存", "ignore"),
            "feature4": HTML('<style fg="#008800">绿色特性</style>')
        }

        result = self.wing_ui.select_multiple_options_ui(
            config=config,
            title=HTML("<u>选择功能模块 - 主题预览测试</u>"),
            text=HTML("你可以选择多个要启用的功能：")
        )

        print(f"用户选择了: {result}")

    def test_yes_no_dialog(self):
        result = self.wing_ui.yes_no_ui(
            title=HTML("<style fg='white' bg='ansired'>删除确认</style>"),
            text="你真的要永久删除这项数据吗？此操作不可恢复！ - 主题预览测试",
            yes_text="我确定",
            no_text="取消"
        )

        if result:
            print("用户选择了确认")
        else:
            print("用户取消了操作")

    def run_test_progress_bar(self, test_bar_name: ProgressBarStyleName = None):
        pb, task = self.wing_ui.get_progress_bar_context(
            iterable=range(50),
            task_description="任务进行中",
            title="测试进度条",
            total=50,
            use_true_color=True,
            use_style_name=test_bar_name
        )

        with pb:  # 启动进度条上下文
            for _ in task:
                time.sleep(0.1)  # 模拟任务耗时



if __name__ == "__main__":
    utils = TestUiUtils(WingUI(StyleLoader()))
    utils.run_test_progress_bar("rainbow")
    # utils.button_choice_dialogs_test()
    # utils.input_dialogs_test()
    # message_dialogs_test()
    # test_single_select()
    # test_multi_select()
    # test_yes_no_dialog()
    #
