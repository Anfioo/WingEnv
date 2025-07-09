from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import print_formatted_text as print_html
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import patch_stdout
import shlex

from utils.ini.progress_bar_manager import ProgressBarManager


class ProgressBarCLI:
    def __init__(self):
        self.pbm = ProgressBarManager()
        self.session = PromptSession(
            HTML('<prompt><b><ansicyan>ProgressBarManager &gt; </ansicyan></b></prompt>'),
            completer=self.build_completer(),
            style=Style.from_dict({
                'prompt': '#00ffff',
                'success': '#00ff00',
                'error': '#ff0000',
                'info': '#ffaa00'
            }),
        )

    def build_completer(self):
        themes = {theme: None for theme in self.pbm.get_available_themes()}
        return NestedCompleter.from_nested_dict({
            'ls': None,
            'show': None,
            'set': themes,
            'help': None,
            'exit': None,
            'quit': None,
        })

    def start(self):
        print_html(HTML('<ansigreen>🎉 欢迎使用 <b>进度条主题管理器</b>！输入 <b>help</b> 查看命令。</ansigreen>'))
        with patch_stdout():
            while True:
                try:
                    text = self.session.prompt()
                    args = shlex.split(text.strip())
                    if not args:
                        continue
                    cmd = args[0].lower()
                    method = getattr(self, f"do_{cmd}", None)
                    if method:
                        method(args[1:])
                    else:
                        print_html(HTML(f'<error>❓ 未知命令: {cmd}，输入 help 查看命令</error>'))
                except (EOFError, KeyboardInterrupt):
                    self.do_exit([])
                    break
                except Exception as e:
                    print_html(HTML(f'<error>❌ 程序异常: {e}</error>'))

    def do_help(self, _):
        print_html(HTML('''
<u><b>命令列表：</b></u>
  <b>ls            </b>\t列出所有支持的进度条主题
  <b>show          </b>\t显示当前设置的进度条主题
  <b>set &lt;name&gt;     </b>\t设置当前进度条主题
  <b>help          </b>\t显示帮助信息
  <b>exit / quit   </b>\t退出管理器
'''))

    def do_ls(self, _):
        themes = sorted(self.pbm.get_available_themes())
        if not themes:
            print_html(HTML('<error>⚠️ 没有可用主题</error>'))
        else:
            print_html(HTML('<info>支持的进度条主题列表：</info>'))
            for t in themes:
                print_html(HTML(f'  <b>{t}</b>'))

    def do_show(self, _):
        current = self.pbm.get_progress_bar_theme()
        print_html(HTML(f'当前进度条主题：<success><b>{current}</b></success>'))

    def do_set(self, args):
        if not args:
            print_html(HTML('<error>❌ 用法错误: set &lt;主题名&gt;</error>'))
            return
        name = args[0]
        try:
            self.pbm.set_progress_bar_theme(name)
            print_html(HTML(f'<success>✅ 主题已设置为 <b>{name}</b></success>'))
        except ValueError as e:
            print_html(HTML(f'<error>❌ {e}</error>'))

    def do_exit(self, _):
        print_html(HTML('<info>👋 再见！</info>'))
        exit(0)

    def do_quit(self, args):
        self.do_exit(args)


if __name__ == '__main__':
    ProgressBarCLI().start()
