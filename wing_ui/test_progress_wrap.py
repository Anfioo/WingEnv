
import time
import datetime
from asyncio import ensure_future
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign, Float, ConditionalContainer
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import (
    MenuItem, TextArea, Button, Frame, RadioList, Label, Box, Checkbox, ProgressBar
)
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.styles import Style

from loader.style_loader import StyleLoader
from wing_ui.patch.menu_item_fix import MenuContainerFix

class DashboardDemoApp:
    def __init__(self):
        self.style_loader = StyleLoader()
        
        # --- UI 组件定义 ---
        
        # 1. 侧边栏导航
        self.nav_list = RadioList(
            values=[
                ("profile", "个人资料"),
                ("tasks", "任务管理"),
                ("settings", "系统设置"),
                ("logs", "实时日志"),
            ]
        )
        
        # 2. 主内容展示区 (TextArea)
        self.content_view = TextArea(
            text="欢迎来到 WingEnv 控制面板\n\n"
                 "这是一个纯 UI 布局演示，参考了 full-screen-demo 的多窗格设计。\n"
                 "您可以使用 Tab 键在不同的区域之间切换焦点。\n\n"
                 "当前模块: Dashboard 概览",
            read_only=True,
            scrollbar=True,
        )

        # 3. 右侧设置面板
        self.check_auto_save = Checkbox(text="自动保存")
        self.check_notifications = Checkbox(text="开启通知")
        self.check_debug_mode = Checkbox(text="调试模式")
        
        # 4. 底部进度条演示
        self.demo_pb = ProgressBar()
        self.demo_pb.percentage = 45 # 初始静态值

        # 5. 底部按钮
        self.btn_action_1 = Button("刷新数据", handler=lambda: self.log("正在刷新..."))
        self.btn_action_2 = Button("执行任务", handler=lambda: self.log("任务已启动"))
        self.btn_action_3 = Button("导出报告", handler=lambda: self.log("报告生成中"))

        # --- 布局构建 ---
        
        # 顶部主要工作区 (三列布局)
        main_workspace = VSplit([
            # 左侧：导航
            Frame(
                body=self.nav_list,
                title="导航菜单",
                width=D(preferred=20)
            ),
            # 中间：核心内容
            HSplit([
                Frame(
                    body=self.content_view,
                    title="主要内容区"
                ),
                Frame(
                    body=self.demo_pb,
                    title="实时任务状态",
                    height=3
                )
            ]),
            # 右侧：设置
            Frame(
                body=HSplit([
                    Label("模块选项:", style="class:label"),
                    self.check_auto_save,
                    self.check_notifications,
                    self.check_debug_mode,
                    Window(height=1),
                    Button("应用更改", handler=lambda: self.log("设置已应用"))
                ], padding=1),
                title="快速设置",
                width=D(preferred=25)
            )
        ])

        # 底部操作条
        bottom_bar = Box(
            body=VSplit([
                self.btn_action_1,
                self.btn_action_2,
                self.btn_action_3,
            ], padding=3, align="CENTER"),
            height=3,
            style="class:button-bar"
        )

        # 组合整体布局
        root_body = HSplit([
            main_workspace,
            bottom_bar
        ])

        # 包装菜单容器
        self.root = MenuContainerFix(
            body=root_body,
            menu_items=[
                MenuItem("文件", children=[
                    MenuItem("新建任务", handler=lambda: self.log("新建任务点击")),
                    MenuItem("打开控制台", handler=lambda: self.log("打开控制台")),
                    MenuItem("-", disabled=True),
                    MenuItem("退出", handler=self.exit_app, shortcut="Esc"),
                ]),
                MenuItem("编辑", children=[
                    MenuItem("全选", shortcut="Ctrl-A"),
                    MenuItem("清除日志", handler=lambda: setattr(self.content_view, 'text', "")),
                ]),
                MenuItem("视图", children=[
                    MenuItem("切换全屏", handler=lambda: self.log("全屏模式切换")),
                    MenuItem("刷新 UI", handler=lambda: self.log("UI 已刷新")),
                ]),
                MenuItem("关于", children=[
                    MenuItem("版本信息", handler=lambda: self.log("WingEnv Dashboard v1.0.0")),
                ]),
            ],
        )

        # --- 系统配置 ---
        
        self.kb = KeyBindings()
        self.kb.add("tab")(focus_next)
        self.kb.add("s-tab")(focus_previous)
        self.kb.add("escape")(lambda _: self.exit_app())

        self.layout = Layout(self.root, focused_element=self.nav_list)
        
        # 使用自定义样式增强视觉
        custom_style = Style.from_dict({
            "window.border": "#888888",
            "frame.label": "fg:#ffffff bg:#444444 bold",
            "button-bar": "bg:#333333",
            "button.focused": "bg:#ff0000 fg:#ffffff",
            "label": "fg:#00ff00 bold",
            "status": "reverse",
        })

        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=custom_style,
            mouse_support=True,
            full_screen=True,
        )

    def log(self, message):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.content_view.text += f"\n[{now}] {message}"
        self.content_view.buffer.cursor_position = len(self.content_view.text)

    def exit_app(self):
        get_app().exit()

    def run(self):
        self.app.run()

if __name__ == "__main__":
    DashboardDemoApp().run()
