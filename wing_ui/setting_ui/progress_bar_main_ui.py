from wing_ui.progress_bar import get_progress_bar_context
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import print_formatted_text as print_html
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import patch_stdout
import shlex

from loader.ini.progress_bar_manager import ProgressBarManager


def run_test_progress_bar(test_bar_name, fast_mode=False):
    pb, task = get_progress_bar_context(
        iterable=range(50),
        task_description="任务进行中",
        title=f"测试进度条 - {test_bar_name}",
        total=50,
        use_true_color=True,
        use_style_name=test_bar_name
    )

    with pb:
        for _ in task:
            if not fast_mode:
                time.sleep(0.05)  # 原始速度


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
            'info': None,
            'set': themes,
            'test': themes,
            'help': None,
            'get': {"all": None, **{name: None for name in themes}} if themes else {"all": None},
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
  <b>info          </b>\t显示当前设置的进度条主题
  <b>set &lt;name&gt;     </b>\t设置当前进度条主题
  <b>get &lt;all|name&gt;  </b>\t展示指定或所有进度条的颜色
  <b>test &lt;name&gt;    </b>\t测试指定主题的进度条效果
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

    def do_info(self, _):
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

    def do_get(self, args):
        themes = self.pbm.get_available_themes()
        if not themes:
            print_html(HTML('<error>⚠️ 没有可用主题</error>'))
            return

        if not args:
            print_html(HTML('<error>❌ 用法错误: get all 或 get &lt;主题名&gt;</error>'))
            return

        target = args[0].lower()

        if target == 'all':
            print_html(HTML(f'<info>📦 正在展示所有进度条主题（快速模式）...</info>'))
            for theme in themes:
                print_html(HTML(f'<info>▶ 主题：<b>{theme}</b></info>'))
                run_test_progress_bar(theme, fast_mode=True)
            print_html(HTML('<success>✅ 所有主题展示完毕！</success>'))
        elif target in themes:
            print_html(HTML(f'<info>▶ 正在展示主题：<b>{target}</b>（快速模式）</info>'))
            run_test_progress_bar(target, fast_mode=True)
            print_html(HTML('<success>✅ 展示完成</success>'))
        else:
            print_html(HTML(f'<error>❌ 未知主题 "{target}"，可用主题包括：{", ".join(themes)}</error>'))

    def do_test(self, args):
        if not args:
            print_html(HTML('<error>❌ 用法错误: test &lt;主题名&gt;</error>'))
            return
        name = args[0]
        available = self.pbm.get_available_themes()
        if name not in available:
            print_html(HTML(f'<error>❌ 主题 "{name}" 不存在。可用主题：{", ".join(available)}</error>'))
            return
        print_html(HTML(f'<info>⏳ 正在测试进度条主题 <b>{name}</b>，请稍候...</info>'))
        run_test_progress_bar(name)
        print_html(HTML('<success>✅ 测试完成！</success>'))

    def do_exit(self, _):
        print_html(HTML('<info>👋 再见！</info>'))
        exit(0)

    def do_quit(self, args):
        self.do_exit(args)


if __name__ == '__main__':
    ProgressBarCLI().start()
