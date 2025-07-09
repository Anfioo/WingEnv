from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import print_formatted_text as print_html
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import patch_stdout
import os
import shutil
import shlex

# 你需要自行提供的工具类，示例假设已有
from utils.env_variable_manager import WinEnvManager
from utils.ini.java_manager import JavaManager
from wing_install.java.jdk.jdk_install import java_install_main


class JdkCLI:
    def __init__(self):
        self.jm = JavaManager()
        self.completer = self.build_completer()
        self.session = PromptSession(
            HTML('<prompt><b><ansiblue>JavaManager &gt; </ansiblue></b></prompt>'),
            completer=self.completer,
            style=Style.from_dict({
                'prompt': '#00ffff',
                'success': '#00ff00',
                'error': '#ff0066',
                'info': '#ffaa00'
            })
        )

    def build_completer(self):
        versions = list(self.jm.list_java_versions().keys())

        # 版本号可能为空时，传 None 防止异常
        set_versions = {ver: None for ver in versions} if versions else None
        remove_versions = {ver: None for ver in versions} if versions else None

        return NestedCompleter.from_nested_dict({
            "ls": None,
            "version": None,
            "help": None,
            "exit": None,
            "quit": None,
            "set": set_versions,
            "remove": remove_versions,
            "add": None,
            "install": None,
        })

    def refresh_completer(self):
        self.session.completer = self.build_completer()

    def start(self):
        print_html(HTML('<ansigreen>🎉 欢迎使用 <b>Java 管理控制台</b>！输入 <b>help</b> 查看命令。</ansigreen>'))
        with patch_stdout():
            while True:
                try:
                    text = self.session.prompt()
                    args = shlex.split(text.strip())
                    if not args:
                        continue

                    command = args[0].lower()
                    method = getattr(self, f"do_{command}", None)
                    if method:
                        method(args[1:])
                    else:
                        print_html(HTML(f"<ansired>❓ 未知命令: {command}，输入 help 查看命令</ansired>"))

                except (EOFError, KeyboardInterrupt):
                    self.do_exit([])
                    break
                except Exception as e:
                    print_html(HTML(f"<ansired>❌ 程序异常: {e}</ansired>"))

    def do_help(self, _):
        print_html(HTML('''\
<u><b>命令列表：</b></u>
  <b>ls               </b>\t查看所有已配置的 Java 版本
  <b>version       </b>\t显示当前使用的 Java 版本
  <b>set &lt;version&gt;       </b>\t设置当前使用的 Java 版本
  <b>add             </b>\t手动导入 Java 安装路径
  <b>install       </b>\t安装  Java 界面
  <b>remove &lt;version&gt;</b>\t移除指定 Java 版本
  <b>help             </b>\t显示帮助信息
  <b>exit / quit       </b>\t退出 Java 管理器
'''))

    def do_ls(self, _):
        versions = self.jm.list_java_versions()
        if not versions:
            print_html(HTML('<ansired>⚠️ 当前没有已配置的 JDK 版本。</ansired>'))
        else:
            print_html(HTML("<u><b>📦 已配置的 JDK 版本：</b></u>"))
            for ver, path in versions.items():
                print_html(HTML(f"  <b>{ver}</b> → <ansicyan>{path}</ansicyan>"))

    def do_version(self, _):
        version = self.jm.get_current_version()
        path = self.jm.get_current_java_path()
        print_html(HTML(f"当前版本: <b><ansigreen>{version}</ansigreen></b>"))
        print_html(HTML(f"JDK 路径: <ansicyan>{path or '未找到路径'}</ansicyan>"))

    def do_set(self, args):
        if not args:
            print_html(HTML('<ansired>❌ 用法错误: set &lt;version&gt;</ansired>'))
            return
        version = args[0]
        if not self.jm.java_version_exists(version):
            print_html(HTML(f"<ansired>❌ 版本 {version} 未配置</ansired>"))
        else:
            self.jm.set_current_version(version)
            java_path = self.jm.get_current_java_path()
            print("🔧 设置用户环境变量...")
            user_env = WinEnvManager()
            user_env.set_variable("JAVA_HOME", java_path) \
                .add_path(r"%JAVA_HOME%\bin") \
                .add_path(r"%JAVA_HOME%\jre\bin") \
                .execute()
            print("✅ 用户环境变量已更新。")
            print_html(HTML(f"<ansigreen>✅ 当前版本已设置为 <b>{version}</b></ansigreen>"))

    def do_install(self, _):
        print_html(HTML("<ansiyellow>📦 开始执行 Java 安装流程...</ansiyellow>"))
        try:
            java_install_main()  # 调用实际安装逻辑

            print_html(HTML("<ansigreen>✅ 安装流程已完成。可以关闭该窗口获取最新的信息</ansigreen>"))

        except Exception as e:
            print_html(HTML(f"<ansired>❌ 安装失败: {e}</ansired>"))

    def do_add(self, _):
        sub_session = PromptSession()
        version = sub_session.prompt("请输入 JDK 主版本号 (如 17): ").strip()
        path = sub_session.prompt("请输入 JDK 安装路径: ").strip()

        if " " in path and not (path.startswith('"') and path.endswith('"')):
            print_html(HTML("<ansired>❌ 路径中含有空格，请使用英文双引号括起来，如 \"C:\\路径\\带 空格\"</ansired>"))
            return

        path = path.strip('"')

        if version and path:
            try:
                self.jm.add_java_version(version, path)
                print_html(HTML(f"<ansigreen>✅ 已导入版本 <b>{version}</b></ansigreen>"))
                self.refresh_completer()  # 动态刷新补全
            except Exception as e:
                print_html(HTML(f"<ansired>❌ 错误: {e}</ansired>"))
        else:
            print_html(HTML("<ansired>❌ 输入无效，导入取消</ansired>"))

    def do_remove(self, args):
        if not args:
            print_html(HTML('<ansired>❌ 用法错误: remove &lt;version&gt;</ansired>'))
            return

        version = args[0]
        if not self.jm.java_version_exists(version):
            print_html(HTML(f"<ansired>❌ 未找到版本: {version}</ansired>"))
            return

        # 获取对应的安装路径
        path = self.jm.get_java_path(version)

        # 删除映射关系
        self.jm.remove_java_version(version)
        print_html(HTML(f"<ansiyellow>✅ 已移除版本 <b>{version}</b></ansiyellow>"))

        # 询问是否删除文件夹
        if path and os.path.exists(path):
            sub_session = PromptSession()
            answer = sub_session.prompt(
                HTML(f'<ansired>是否要删除对应文件夹 <b>"{path}"</b>？(y/n): </ansired>')
            ).strip().lower()
            if answer == 'y':
                try:
                    shutil.rmtree(path)
                    print_html(HTML(f"<ansigreen>🗑️ 已删除文件夹 <b>{path}</b></ansigreen>"))
                except Exception as e:
                    print_html(HTML(f"<ansired>⚠️ 删除失败: {e}</ansired>"))
            else:
                print_html(HTML("<ansiblue>📁 保留了文件夹内容。</ansiblue>"))

        self.refresh_completer()

    def do_exit(self, _):
        print_html(HTML("<ansiblue>👋 再见！</ansiblue>"))
        exit(0)

    def do_quit(self, args):
        self.do_exit(args)


if __name__ == "__main__":
    JdkCLI().start()
