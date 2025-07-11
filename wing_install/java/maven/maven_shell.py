from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import print_formatted_text as print_html
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import patch_stdout
import os
import shutil
import shlex

from utils.env_variable_manager import WinEnvManager
from utils.ini.maven_manager import MavenManager  # 你需要实现类似 JavaManager 的 MavenManager
from wing_install.java.maven.maven_install_ import maven_install_main


class MavenCLI:
    def __init__(self):
        self.mm = MavenManager()
        self.completer = self.build_completer()
        self.session = PromptSession(
            HTML('<prompt><b><ansiblue>MavenManager &gt; </ansiblue></b></prompt>'),
            completer=self.completer,
            style=Style.from_dict({
                'prompt': '#00ffff',
                'success': '#00ff00',
                'error': '#ff0066',
                'info': '#ffaa00'
            })
        )

    def build_completer(self):
        versions = list(self.mm.list_maven_versions().keys())
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
        print_html(HTML('<ansigreen>🎉 欢迎使用 <b>Maven 管理控制台</b>！输入 <b>help</b> 查看命令。</ansigreen>'))
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
  <b>ls               </b>\t查看所有已配置的 Maven 版本
  <b>version       </b>\t显示当前使用的 Maven 版本
  <b>set &lt;version&gt;       </b>\t设置当前使用的 Maven 版本
  <b>add             </b>\t手动导入 Maven 安装路径
  <b>install       </b>\t安装 Maven 界面
  <b>remove &lt;version&gt;</b>\t移除指定 Maven 版本
  <b>help             </b>\t显示帮助信息
  <b>exit / quit       </b>\t退出 Maven 管理器
'''))

    def do_ls(self, _):
        versions = self.mm.list_maven_versions()
        if not versions:
            print_html(HTML('<ansired>⚠️ 当前没有已配置的 Maven 版本。</ansired>'))
        else:
            print_html(HTML("<u><b>📦 已配置的 Maven 版本：</b></u>"))
            for ver, path in versions.items():
                print_html(HTML(f"  <b>{ver}</b> → <ansicyan>{path}</ansicyan>"))

    def do_version(self, _):
        version = self.mm.get_current_version()
        path = self.mm.get_current_maven_path()
        print_html(HTML(f"当前版本: <b><ansigreen>{version}</ansigreen></b>"))
        print_html(HTML(f"Maven 路径: <ansicyan>{path or '未找到路径'}</ansicyan>"))

    def do_set(self, args):
        if not args:
            print_html(HTML('<ansired>❌ 用法错误: set &lt;version&gt;</ansired>'))
            return
        version = args[0]
        if not self.mm.maven_version_exists(version):
            print_html(HTML(f"<ansired>❌ 版本 {version} 未配置</ansired>"))
        else:
            self.mm.set_current_version(version)
            maven_path = self.mm.get_current_maven_path()
            print("🔧 设置用户环境变量...")
            user_env = WinEnvManager()
            user_env.set_variable("MAVEN_HOME", maven_path) \
                .add_path(r"%MAVEN_HOME%\bin") \
                .execute()
            print("✅ 用户环境变量已更新。")
            print_html(HTML(f"<ansigreen>✅ 当前版本已设置为 <b>{version}</b></ansigreen>"))

    def do_install(self, _):
        print_html(HTML("<ansiyellow>📦 开始执行 Maven 安装流程...</ansiyellow>"))
        try:
            maven_install_main()  # 调用实际安装逻辑

            print_html(HTML("<ansigreen>✅ 安装流程已完成。可以关闭该窗口获取最新的信息</ansigreen>"))

        except Exception as e:
            print_html(HTML(f"<ansired>❌ 安装失败: {e}</ansired>"))

    def do_add(self, _):
        sub_session = PromptSession()
        version = sub_session.prompt("请输入 Maven 版本号 (如 3.8.7): ").strip()
        path = sub_session.prompt("请输入 Maven 安装路径: ").strip()

        if " " in path and not (path.startswith('"') and path.endswith('"')):
            print_html(HTML("<ansired>❌ 路径中含有空格，请使用英文双引号括起来，如 \"C:\\路径\\带 空格\"</ansired>"))
            return

        path = path.strip('"')

        if version and path:
            try:
                self.mm.add_maven_version(version, path)
                print_html(HTML(f"<ansigreen>✅ 已导入版本 <b>{version}</b></ansigreen>"))
                self.refresh_completer()
            except Exception as e:
                print_html(HTML(f"<ansired>❌ 错误: {e}</ansired>"))
        else:
            print_html(HTML("<ansired>❌ 输入无效，导入取消</ansired>"))

    def do_remove(self, args):
        if not args:
            print_html(HTML('<ansired>❌ 用法错误: remove &lt;version&gt;</ansired>'))
            return

        version = args[0]
        if not self.mm.maven_version_exists(version):
            print_html(HTML(f"<ansired>❌ 未找到版本: {version}</ansired>"))
            return

        path = self.mm.get_maven_path(version)

        self.mm.remove_maven_version(version)
        print_html(HTML(f"<ansiyellow>✅ 已移除版本 <b>{version}</b></ansiyellow>"))

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
    MavenCLI().start()
