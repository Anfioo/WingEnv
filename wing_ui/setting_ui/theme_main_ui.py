import shlex
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import print_formatted_text as print_html
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import patch_stdout

from loader.css_color_viewer import CssColorViewer
from loader.ini.theme_manager import ThemeManager
from loader.ui_test_utils import (
    button_choice_dialogs_test,
    input_dialogs_test,
    message_dialogs_test,
    test_single_select,
    test_multi_select,
    test_yes_no_dialog,
)


class ThemeCLI:
    def __init__(self):
        self.tm = ThemeManager()
        self.session = PromptSession(
            HTML('<prompt><b><ansiblue>ThemeManager &gt; </ansiblue></b></prompt>'),
            completer=self.build_completer(),
            style=Style.from_dict({
                'prompt': '#00ffff',
                'success': '#00ff00',
                'error': '#ff0066',
                'info': '#ffaa00'
            })
        )

    def build_completer(self):
        themes = list(self.tm.list_themes().keys())
        test_methods = [
            "button_choice_dialogs_test",
            "input_dialogs_test",
            "message_dialogs_test",
            "test_single_select",
            "test_multi_select",
            "test_yes_no_dialog",
            "all",
        ]
        return NestedCompleter.from_nested_dict({
            "ls": None,
            "add": None,
            "remove": {name: None for name in themes} if themes else None,
            "info": None,
            "set": {name: None for name in themes} if themes else None,
            "test": {method: None for method in test_methods},
            "help": None,
            "exit": None,
            "quit": None,
            "get": {"all": None, **{name: None for name in themes}} if themes else {"all": None},

        })

    def refresh_completer(self):
        self.session.completer = self.build_completer()

    def start(self):
        print_html(HTML('<ansigreen>🎨 欢迎使用 <b>主题管理控制台</b>！输入 <b>help</b> 查看命令。</ansigreen>'))
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

    def do_test(self, args):
        tests_map = {
            "button_choice_dialogs_test": button_choice_dialogs_test,
            "input_dialogs_test": input_dialogs_test,
            "message_dialogs_test": message_dialogs_test,
            "test_single_select": test_single_select,
            "test_multi_select": test_multi_select,
            "test_yes_no_dialog": test_yes_no_dialog,
        }

        if not args:
            print_html(HTML('<ansired>❌ 用法错误: test &lt;all|method_name&gt;</ansired>'))
            return

        if args[0] == "all":
            for name, func in tests_map.items():
                try:
                    print_html(HTML(f"<ansiyellow>开始执行测试: {name}</ansiyellow>"))
                    func()
                    print_html(HTML(f"<ansigreen>✅ 测试 {name} 完成</ansigreen>"))
                except Exception as e:
                    print_html(HTML(f"<ansired>❌ 测试 {name} 出错: {e}</ansired>"))
            print_html(HTML("<ansigreen>✅ 所有测试完成。</ansigreen>"))
        else:
            method_name = args[0]
            func = tests_map.get(method_name)
            if func is None:
                print_html(HTML(f"<ansired>❌ 未知测试方法: {method_name}</ansired>"))
                return
            try:
                print_html(HTML(f"<ansiyellow>开始执行测试: {method_name}</ansiyellow>"))
                func()
                print_html(HTML(f"<ansigreen>✅ 测试 {method_name} 完成</ansigreen>"))
            except Exception as e:
                print_html(HTML(f"<ansired>❌ 测试 {method_name} 出错: {e}</ansired>"))

    def do_get(self, args):
        themes = self.tm.list_themes()
        if not args:
            print_html(HTML('<ansired>❌ 用法错误: get &lt;all|主题名&gt;</ansired>'))
            return

        if args[0] == 'all':
            if not themes:
                print_html(HTML('<ansired>⚠️ 目前没有任何主题。</ansired>'))
                return
            for name, path in themes.items():
                try:
                    viewer = CssColorViewer(path)
                    viewer.show_colors()
                except Exception as e:
                    print_html(HTML(f"<ansired>❌ 读取主题 {name} 失败: {e}</ansired>"))
        else:
            name = args[0]
            if name not in themes:
                print_html(HTML(f"<ansired>❌ 主题 {name} 不存在。</ansired>"))
                return
            try:
                viewer = CssColorViewer(themes[name])
                viewer.show_colors()
            except Exception as e:
                print_html(HTML(f"<ansired>❌ 读取主题 {name} 失败: {e}</ansired>"))

    def do_help(self, _):
        print_html(HTML('''\
<u><b>命令列表：</b></u>
  <b>ls                    </b>\t列出所有主题及路径
  <b>add                   </b>\t添加新主题（交互输入名称和CSS路径）
  <b>remove &lt;name&gt;              </b>\t删除指定主题
  <b>get &lt;all|name&gt;              </b>\t展示指定或所有主题的颜色
  <b>info                      </b>\t显示当前主题及路径
  <b>set &lt;name&gt;              </b>\t设置当前主题
  <b>test &lt;all|method_name&gt;</b>\t执行测试方法
  <b>help                  </b>\t显示此帮助
  <b>exit / quit           </b>\t退出
'''))

    def do_ls(self, _):
        themes = self.tm.list_themes()
        if not themes:
            print_html(HTML('<ansired>⚠️ 目前没有任何主题。</ansired>'))
            return
        print_html(HTML("<u><b>📚 已配置主题：</b></u>"))
        for name, path in themes.items():
            print_html(HTML(f"  <b>{name}</b> → <ansicyan>{path}</ansicyan>"))

    def do_add(self, _):
        sub_session = PromptSession()
        name = sub_session.prompt("请输入主题名称: ").strip()
        if not name:
            print_html(HTML("<ansired>❌ 主题名不能为空。</ansired>"))
            return
        css_path = sub_session.prompt("请输入 CSS 文件路径: ").strip()
        if not css_path:
            print_html(HTML("<ansired>❌ CSS 路径不能为空。</ansired>"))
            return

        try:
            self.tm.add_theme(name, css_path)
            print_html(HTML(f"<ansigreen>✅ 主题 <b>{name}</b> 添加成功。</ansigreen>"))
            self.refresh_completer()
        except FileNotFoundError as e:
            print_html(HTML(f"<ansired>❌ 错误: {e}</ansired>"))
        except Exception as e:
            print_html(HTML(f"<ansired>❌ 添加主题失败: {e}</ansired>"))

    def do_remove(self, args):
        if not args:
            print_html(HTML('<ansired>❌ 用法错误: remove &lt;name&gt;</ansired>'))
            return
        name = args[0]
        if not self.tm.theme_exists(name):
            print_html(HTML(f"<ansired>❌ 主题 {name} 不存在。</ansired>"))
            return
        self.tm.remove_theme(name)
        print_html(HTML(f"<ansiyellow>✅ 已删除主题 <b>{name}</b>。（不删除 CSS 文件）</ansiyellow>"))
        self.refresh_completer()

    def do_info(self, _):
        name = self.tm.get_current_theme()
        path = self.tm.get_current_theme_path()
        print_html(HTML(f"当前主题: <b><ansigreen>{name}</ansigreen></b>"))
        print_html(HTML(f"CSS 路径: <ansicyan>{path or '未设置'}</ansicyan>"))

    def do_set(self, args):
        if not args:
            print_html(HTML('<ansired>❌ 用法错误: set &lt;name&gt;</ansired>'))
            return
        name = args[0]
        if not self.tm.theme_exists(name):
            print_html(HTML(f"<ansired>❌ 主题 {name} 不存在。</ansired>"))
            return
        try:
            self.tm.set_current_theme(name)
            print_html(HTML(f"<ansigreen>✅ 当前主题已切换为 <b>{name}</b></ansigreen>"))
        except Exception as e:
            print_html(HTML(f"<ansired>❌ 设置失败: {e}</ansired>"))

    def do_exit(self, _):
        print_html(HTML("<ansiblue>👋 再见！</ansiblue>"))
        exit(0)

    def do_quit(self, args):
        self.do_exit(args)


if __name__ == "__main__":
    ThemeCLI().start()
