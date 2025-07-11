from wing_install.java.jdk.jdk_shell import JdkCLI

from wing_ui.selection_dialogs import select_single_option_ui
from wing_ui.setting_ui.progress_bar_main_ui import ProgressBarCLI
from wing_ui.setting_ui.theme_main_ui import ThemeCLI
from typing import Callable, Dict, Union
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style


def shell_setting_ui():
    ui = select_single_option_ui(config={"theme": ("主题设置", "normal"), "bar": ("进度条主题设置", "normal")},
                                 title="主题设置", text="请选择主题")
    if ui == "theme":
        ThemeCLI().start()
    elif ui == "bar":
        ProgressBarCLI().start()


class ShellEnvUIBase:
    def launch_ui(self, module: str, title: str, text: str):
        """
        自动收集所有 shell_{module}_xxx_ui 方法，并展示 UI 菜单执行。
        """
        prefix = f"shell_{module}_"
        method_map: Dict[str, Callable] = {
            name: getattr(self, name)
            for name in dir(self)
            if name.startswith(prefix) and name.endswith("_ui") and callable(getattr(self, name))
        }

        config = {
            name: (name.replace(prefix, "").replace("_ui", ""), "normal")
            for name in method_map
        }

        choice = select_single_option_ui(config, title=title, text=text)
        if choice and choice in method_map:
            method_map[choice]()
        else:
            print("❌ 未选择任何操作")


class ShellJavaUI(ShellEnvUIBase):
    def shell_java_jdk_ui(self):
        print("✅ 启动 JDK UI")

    def shell_java_maven_ui(self):
        print("✅ 启动 Maven UI")

    def shell_ui(self):
        self.launch_ui(module="java", title="Java 栈配置", text="请选择要配置的项：")


class ShellPythonUI(ShellEnvUIBase):
    def shell_python_jdk_ui(self):
        print("✅ 启动 Python JDK 设置")

    def shell_python_uv_ui(self):
        print("✅ 启动 uv 虚拟环境配置")

    def shell_python_pip_ui(self):
        print("✅ 启动 pip 包管理器配置")

    def shell_ui(self):
        self.launch_ui(module="python", title="🐍 Python 栈配置", text="请选择要配置的项：")


if __name__ == "__main__":
    ShellJavaUI().shell_ui()
    ShellPythonUI().shell_ui()
