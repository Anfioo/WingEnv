# import os
# import sys
# import winreg
#
# from prompt_toolkit import PromptSession
# from prompt_toolkit.completion import Completer, Completion
#
# from wing_env_install.java_install.java_env_shell import java_env_set_main
# from wing_env_install.java_install.java_set_env import broadcast_env_change
# from wing_env_ui.print_avatar_ui import print_avatar
# from wing_env_ui.select_env import select_env
#
# from prompt_toolkit import print_formatted_text
# from prompt_toolkit.formatted_text import HTML
#
#
# class MyCompleter(Completer):
#     def __init__(self):
#         self.top_commands = ['init', 'install', 'info', 'help', 'env']
#         self.env_subcommands = ['java']
#
#     def get_completions(self, document, complete_event):
#         text = document.text_before_cursor.lstrip()
#         parts = text.split()
#
#         if len(parts) == 0:
#             for cmd in self.top_commands:
#                 yield Completion(cmd, start_position=0)
#         elif len(parts) == 1:
#             for cmd in self.top_commands:
#                 if cmd.startswith(parts[0]):
#                     yield Completion(cmd, start_position=-len(parts[0]))
#         elif len(parts) == 2 and parts[0] == 'env':
#             for subcmd in self.env_subcommands:
#                 if subcmd.startswith(parts[1]):
#                     yield Completion(subcmd, start_position=-len(parts[1]))
#
#
# def shell_main():
#     completer = MyCompleter()
#     start_interactive_shell(completer)
#
#
# def start_interactive_shell(completer):
#     session = PromptSession('we> ', completer=completer)
#
#     while True:
#         try:
#             user_input = session.prompt()
#             if not user_input.strip():
#                 continue
#
#             parts = user_input.strip().split()
#             if not parts:
#                 continue
#
#             cmd = parts[0]
#
#             if cmd == 'exit':
#                 break
#             elif cmd == 'init':
#                 handle_init()
#             elif cmd == 'install':
#                 select_env()
#             elif cmd == 'info':
#                 handle_info()
#             elif cmd == 'help':
#                 show_help()
#             elif cmd == 'env':
#                 if len(parts) > 1 and parts[1] == 'java':
#                     java_env_set_main()
#                 else:
#                     print("请指定 env 子命令，例如：env java")
#             else:
#                 print(f"错误: 未知命令 '{cmd}'。输入 'help' 获取帮助。")
#
#         except KeyboardInterrupt:
#             continue
#         except EOFError:
#             break
#
#
# def set_user_we_env(we_home_path: str):
#     if not os.path.isdir(we_home_path):
#         print(f"❌ 无效的路径: {we_home_path}")
#         return
#
#     try:
#         reg_path = r"Environment"
#         reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
#
#         try:
#             current_path, _ = winreg.QueryValueEx(reg_key, "Path")
#         except FileNotFoundError:
#             current_path = ""
#
#         we_bin_abs_path = we_home_path
#
#         if we_bin_abs_path.lower() not in current_path.lower():
#             new_path = f"{we_bin_abs_path};{current_path}" if current_path else we_bin_abs_path
#             winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
#             print(f"✅ 已将绝对路径 {we_bin_abs_path} 添加到 PATH")
#         else:
#             print(f"ℹ️ PATH 中已包含 {we_bin_abs_path}，无需添加")
#
#         winreg.CloseKey(reg_key)
#
#         print("\n⚠️ 修改后的环境变量将在重新打开命令行或资源管理器后生效")
#
#     except PermissionError:
#         print("❌ 权限不足，无法写入用户环境变量。")
#
#     broadcast_env_change()
#
#
# def get_app_path():
#     if getattr(sys, 'frozen', False):
#         # 打包后的exe运行时路径（PyInstaller）
#         return os.path.dirname(sys.executable)
#     else:
#         # 脚本直接运行时路径
#         return os.path.abspath(os.path.dirname(__file__))
#
# def handle_init():
#     we_home_path = get_app_path() # 当前脚本文件所在目录绝对路径
#     set_user_we_env(we_home_path)
#     print("初始化完成，已设置 WE_HOME 并添加到 PATH")
#
#
#
# def handle_info():
#     print_formatted_text(HTML('<u><b>项目信息:</b></u>'))
#     print_formatted_text(HTML('  <b>名称:</b> WingEnv'))
#     print_formatted_text(HTML('  <b>介绍:</b> 更方便安装环境的工具'))
#     print_formatted_text(HTML('  <b>版本:</b> 1.0.0'))
#     print_formatted_text(HTML('  <b>作者:</b> Anfioo'))
#     print_formatted_text(HTML('  <b>CSDN:</b> <ansiblue><u>https://blog.csdn.net/m0_73579391?type=blog</u></ansiblue>'))
#     print_formatted_text(HTML('  <b>bilibili:</b> <ansiblue><u>https://space.bilibili.com/1821689715</u></ansiblue>'))
#     print_formatted_text(HTML('  <b>github:</b> <ansiblue><u>https://github.com/Anfioo</u></ansiblue>'))
#     print_formatted_text(HTML('  <b>知乎:</b> <ansiblue><u>https://www.zhihu.com/people/54-37-39-24</u></ansiblue>'))
#     print_avatar()
#
#
# def show_help():
#     print("WE 命令行工具帮助:")
#     print("  we init         - 初始化项目")
#     print("  we install      - 选择需要安装的环境")
#     print("  we info         - 显示项目信息")
#     print("  we help         - 显示此帮助信息")
#     print("  we env java     - 进入 Java 环境设置交互")
#

from utils.downloader import download_with_progress


if __name__ == "__main__":
    download_with_progress(
        url="https://download.java.net/java/GA/jdk12.0.2/e482c34c86bd4bf8b56c0b35558996b9/10/GPL/openjdk-12.0.2_windows-x64_bin.zip",
        save_dir=r"C:\Users\Anfioo\Downloads\Demo"
    )
