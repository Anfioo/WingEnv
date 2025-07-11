import sys
from typing import Dict, Callable, Type
from shell import ShellJavaUI, ShellPythonUI, ShellEnvUIBase  # 你需要准备这几个类

# 所有 shell 类注册到这里
SHELL_CLASSES: Dict[str, Type[ShellEnvUIBase]] = {
    "java": ShellJavaUI,
    "python": ShellPythonUI,
}


def show_help():
    print("🛠 WE 命令行工具帮助:")
    print("  we help(h)                  - 显示此帮助信息")
    print("  we info                     - 显示项目信息")
    print("  we shell h                  - 查看支持模块列表")
    print("  we shell <模块>             - 进入指定 shell 模块设置交互")
    print("  we shell <模块> h           - 列出模块支持的子命令")
    print("  we shell <模块> <子命令>    - 执行指定模块子命令")


def handle_info():
    print("📦 项目信息：")
    print("名称: Web Environment CLI")
    print("版本: 2.0.0")
    print("作者: Anfioo")


def shell_list():
    print("📋 支持的 shell 模块:")
    for mod in SHELL_CLASSES:
        print(f"  - {mod}")


def handle_shell(sub_args):
    if not sub_args:
        print("❗ 请指定 shell 模块，例如：`we shell java` 或 `we shell h`")
        return

    if sub_args[0].lower() == "h":
        shell_list()
        return

    module = sub_args[0].lower()
    cls = SHELL_CLASSES.get(module)

    if not cls:
        print(f"❌ 不支持的 shell 模块: {module}，可用模块: h")
        return

    instance = cls()

    # 子命令是 h，列出模块支持的子命令
    if len(sub_args) > 1 and sub_args[1].lower() == "h":
        prefix = f"shell_{module}_"
        methods = [
            m for m in dir(instance)
            if m.startswith(prefix)
            and m.endswith("_ui")
            and m != f"shell_{module}_ui"
        ]
        subcommands = [m[len(prefix):-3] for m in methods]
        print(f"📋 模块 {module} 支持的子命令:")
        for sc in subcommands:
            print(f"  - {sc}")
        return

    # 没有指定子命令，调用模块交互界面
    if len(sub_args) == 1:
        if hasattr(instance, "shell_ui"):
            instance.shell_ui()
        else:
            print(f"⚠️ 模块 {module} 未实现 shell_ui 方法")
        return

    # 指定了子命令，尝试调用对应方法
    sub_cmd = sub_args[1].lower()
    method_name = f"shell_{module}_{sub_cmd}_ui"

    if hasattr(instance, method_name):
        method = getattr(instance, method_name)
        if callable(method):
            method()
        else:
            print(f"⚠️ {method_name} 不是可调用方法")
    else:
        print(f"❌ 子命令 {sub_cmd} 不存在于模块 {module}，使用 `we shell {module}` 查看交互界面")


def main():
    args = sys.argv[1:]
    if not args:
        show_help()
        return

    cmd = args[0].lower()
    sub_args = args[1:]

    command_map: Dict[str, Callable] = {
        "help": show_help,
        "h": show_help,
        "info": handle_info,
        "shell": lambda: handle_shell(sub_args),
    }

    func = command_map.get(cmd)
    if func:
        func()
    else:
        print(f"❌ 未知命令: {cmd}，输入 'we help' 获取帮助")


if __name__ == "__main__":
    main()
