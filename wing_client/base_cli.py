import shlex
import sys
from typing import List, Dict, Callable, Union, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import print_formatted_text as print_html
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import clear as clear_screen
from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from wing_client.base_command import BaseCommand, CommandRegistry
from wing_utils.ui import console
from typing import TypeVar, Generic, Dict, Any

# 这里声明为泛型类型
T = TypeVar("T")  # 泛型，表示子类自定义的 _data 类型


# ==========================================
# 2. 基础 CLI 类 (增加了刷新机制)
# ==========================================

class BaseCLI(Generic[T]):
    def __init__(self, prompt_text: str = "CLI > "):
        self.prompt_text = prompt_text
        # ---- 全局数据上下文 ----
        self.data: Optional[T] = None
        self._auto_actions: Optional[Dict[str, Callable]] = None

        self.init_business_logic()
        self.cmd_tree = self.get_cmd_tree()
        self.action_map = self.get_action_map()
        self.registry = CommandRegistry(self.cmd_tree, self.action_map)
        self.console = console

        # 初次构建 Session
        self.session = PromptSession(
            HTML(f'<prompt><b><ansicyan>{self.prompt_text}</ansicyan></b></prompt>'),
            completer=self.build_completer()
        )

    def auto_register_static_actions(self, static_action_map: Dict[str, Callable]) -> Dict[str, Callable]:
        """
        注册无参方法，同时暴露 CLI 兼容 action（同名）
        test_yes_no_dialog -> _auto_test_yes_no_dialog
        """
        auto_action_map = {}

        cli = self

        for name, func in static_action_map.items():
            auto_name = f"_auto_{name}"

            def _auto_action(_cli, args, _func=func):
                return _func()

            bound = _auto_action.__get__(cli, cli.__class__)
            setattr(cli, auto_name, bound)

            # 👇 关键：同名 action，指向 CLI 包装后的方法
            auto_action_map[name] = bound

        return auto_action_map

    def init_business_logic(self):
        pass

    def build_completer(self) -> NestedCompleter:
        """核心：每次调用都会重新生成完整的补全树"""
        comp_dict = {}
        for cmd in self.cmd_tree:
            for identity in cmd.identities:
                comp_dict[identity] = cmd.get_completer_dict()
        return NestedCompleter.from_nested_dict(comp_dict)

    def refresh_completer(self):
        """将最新的补全树注入到当前 Session"""
        self.session.completer = self.build_completer()

    def get_action_map(self) -> Dict[str, Callable]:
        return {"do_help": self.do_help, "do_exit": self.do_exit, "do_clear": self.do_clear, }

    def get_cmd_tree(self) -> List[BaseCommand]:
        return [
            BaseCommand("help", "help", "显示帮助", "do_help"),
            BaseCommand(["exit", "quit"], "exit", "退出", "do_exit"),
            BaseCommand("clear", "clear", "清空控制台", "do_clear"),
        ]

    def do_help(self, args: List[str]):
        # ---------- help ----------
        if not args:
            table = Table(show_header=True, header_style="bold cyan", expand=True)
            table.add_column("命令", style="bold green")
            table.add_column("描述", style="yellow")

            for cmd in self.cmd_tree:
                table.add_row("/".join(cmd.identities), cmd.help_text)

            self.console.print(Panel(table, title="📚 CLI 命令总览", border_style="cyan"))
            return

        # ---------- help <命令路径> ----------
        cmd = self._find_command_path(args, self.cmd_tree)
        if not cmd:
            self.console.print(f"[bold red]❌ 未知命令路径:[/bold red] {' '.join(args)}")
            return

        usage = getattr(cmd, "usage", "")
        help_text = cmd.help_text
        cmd_info = (
            f"[cyan]命令:[/cyan] {' '.join(args)}\n"
            f"[cyan]用法:[/cyan] {usage}\n"
            f"[cyan]说明:[/cyan] {help_text}"
        )

        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("子命令", style="bold")
        table.add_column("说明", style="bold")

        has_rows = False

        if getattr(cmd, "sub_commands", None):
            self._render_sub_commands(table, cmd.sub_commands)
            has_rows = True

        if getattr(cmd, "dynamic_completer", None):
            for item in cmd.dynamic_completer() or []:
                table.add_row(f"[yellow]{item}[/yellow]", "[yellow](动态参数)[/yellow]")
                has_rows = True

        panels = [Panel(cmd_info, title="📘 命令说明", border_style="cyan")]
        if has_rows:
            panels.append(table)

        self.console.print(
            Panel(Group(*panels), title="help", border_style="green")
        )

    def _find_command_path(
            self,
            names: List[str],
            commands: List[BaseCommand]
    ) -> Optional[BaseCommand]:
        if not names:
            return None

        current = None
        for cmd in commands:
            if names[0] in cmd.identities:
                current = cmd
                break

        if not current:
            return None

        if len(names) == 1:
            return current

        if getattr(current, "sub_commands", None):
            return self._find_command_path(names[1:], current.sub_commands)

        return None

    def _render_sub_commands(self, table, commands, level=0):
        indent = "  " * level

        for cmd in commands:
            # 1️⃣ 命令本身
            table.add_row(
                f"{indent}[green]{cmd.identities[0]}[/green]",
                cmd.help_text
            )

            # 2️⃣ 该命令自己的 dynamic 参数（⭐关键）
            if getattr(cmd, "dynamic_completer", None):
                try:
                    items = cmd.dynamic_completer() or []
                except Exception:
                    items = []

                for item in items:
                    table.add_row(
                        f"{indent}  [yellow]{item}[/yellow]",
                        "[yellow](动态参数)[/yellow]"
                    )

            # 3️⃣ 递归子命令
            if getattr(cmd, "sub_commands", None):
                self._render_sub_commands(
                    table,
                    cmd.sub_commands,
                    level + 1
                )

    def do_exit(self, _: List[str]):
        sys.exit(0)

    def do_clear(self, _: List[str]):
        clear_screen()

    def run(self):
        if len(sys.argv) > 1:
            self.registry.execute(sys.argv[1:])
        else:
            self.start_interactive()

    def start_interactive(self):
        print_html(HTML("<ansigreen>🚀 CLI 已启动。</ansigreen>"))
        with patch_stdout():
            while True:
                try:
                    text = self.session.prompt()
                    if not text.strip(): continue

                    self.registry.execute(shlex.split(text))

                    # --- 关键改进：执行完任何命令后，自动刷新补全器 ---
                    self.refresh_completer()

                except (EOFError, KeyboardInterrupt):
                    self.do_exit([])
                except Exception as e:
                    print_html(HTML(f"<ansired>❌ 错误: {e}</ansired>"))

    def execute_argv(self, argv: List[str]):
        """
        对外命令执行接口
        - argv: List[str]（不包含 python / 脚本名）
        """
        if not argv:
            return

        try:
            self.registry.execute(argv)
            self.refresh_completer()
        except Exception as e:
            print_html(HTML(f"<ansired>❌ 错误: {e}</ansired>"))

    def _print_message(self, message, message_type="info", **kwargs):
        """打印格式化消息"""
        color_map = {
            "success": "ansigreen",
            "error": "ansired",
            "warning": "ansiyellow",
            "info": "ansiblue",
            "cyan": "ansicyan"
        }
        from html import escape
        color = color_map.get(message_type, "ansiblue")
        print_html(HTML(f"<{color}>{escape(message)}</{color}>"))
