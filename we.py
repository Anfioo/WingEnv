# 文件名建议：we.py
import sys

from wing_env_install.java_shell_bin import java_env_set_main_shell
from wing_env_ui.select_env import select_env
from shell import handle_info, shell_main


def show_help():
    print("WE 命令行工具帮助:")
    print("  we install(i)      - 选择需要安装的环境")
    print("  we info         - 显示项目信息")
    print("  we help(h)         - 显示此帮助信息")
    print("  we env(e) <参数>     - 进入 <参数> 环境设置交互")
    print("  we shell(s)      - 进入shell 环境设置交互")


def main():
    args = sys.argv[1:]

    if not args:
        show_help()
        return

    cmd = args[0]

    if cmd == 'install' or cmd == 'i':
        select_env()
    elif cmd == 'info':
        handle_info()
    elif cmd == 'help' or cmd == 'h':
        show_help()
    elif cmd == 'shell' or cmd == 's':
        shell_main()
    elif cmd == 'env' or cmd == 'e':
        if len(args) > 1 and args[1] == 'java':
            # 处理 we env java 子命令
            java_args = args[2:]  # 把 java 后的参数传入
            java_env_set_main_shell(java_args)

        else:
            print("请指定 env 子命令，例如：we env java ls 或 we env java set 8")

    else:
        print(f"未知命令: {cmd}，输入 'we help' 获取帮助")


if __name__ == "__main__":
    main()
