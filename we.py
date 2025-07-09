# # 文件名建议：we.py
# import sys
#
# from wing_env_install.java_shell_bin import java_env_set_main_shell
# from wing_env_ui.select_env import select_env
# from shell import handle_info, shell_main
#
#
# def show_help():
#     print("WE 命令行工具帮助:")
#     print("  we install(i)      - 选择需要安装的环境")
#     print("  we info         - 显示项目信息")
#     print("  we help(h)         - 显示此帮助信息")
#     print("  we env(e) <参数>     - 进入 <参数> 环境设置交互")
#     print("  we shell(s)      - 进入shell 环境设置交互")
#
#
# def main():
#     args = sys.argv[1:]
#
#     if not args:
#         show_help()
#         return
#
#     cmd = args[0].lower()  # 转换为小写
#
#     # 使用字典映射命令到函数
#     command_map = {
#         'install': select_env,
#         'i': select_env,
#         'info': handle_info,
#         'help': show_help,
#         'h': show_help,
#         'shell': shell_main,
#         's': shell_main,
#     }
#
#     if cmd in command_map:
#         command_map[cmd]()
#     elif cmd == 'env' or cmd == 'e':
#         # 处理 env 子命令
#         if len(args) > 1 and args[1] == 'java':
#             java_args = args[2:]
#             java_env_set_main_shell(java_args)
#         else:
#             print("请指定 env 子命令，例如：we env java ls 或 we env java set 8")
#     else:
#         print(f"未知命令: {cmd}，输入 'we help' 获取帮助")
#
#
# if __name__ == "__main__":
#     main()
