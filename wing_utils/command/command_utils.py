import subprocess
from typing import Dict, Callable, List, Any
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.text import Text

from command_resolver_utils import CommandType, CommandMatch


# =========================
# 类型定义
# =========================


@dataclass
class CommandResult:
    type: CommandType
    desc: str
    command: str
    output: Any
    success: bool


# =========================
# RUN 函数映射表
# =========================

def conda_info(arg1: str, arg2: str) -> str:
    if arg1 == "-fail":
        raise ValueError("模拟失败")
    return f"conda_info 执行成功: arg1={arg1}, arg2={arg2}"


RUN_FUNCTIONS: Dict[str, Callable[..., str]] = {
    "conda-info": conda_info,
}


# =========================
# 命令执行器
# =========================

class CommandExecutor:

    @classmethod
    def execute(cls, cmd_match: CommandMatch) -> List[CommandResult]:
        """
        执行命令列表，返回每条命令结果列表
        """
        results: List[CommandResult] = []
        overall_success = False

        for cmd in cmd_match.commands:
            try:
                success = False
                output: Any = ""

                if cmd_match.type in (CommandType.RAW, CommandType.REWRITE):
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    output = (result.stdout + result.stderr).strip()
                    success = result.returncode == 0

                elif cmd_match.type == CommandType.RUN:
                    parts = cmd.split()
                    func_name = parts[0]
                    args = parts[1:]

                    func = RUN_FUNCTIONS.get(func_name)
                    if not func:
                        output = f"未找到函数: {func_name}"
                        success = False
                    else:
                        try:
                            output = func(*args)
                            success = True
                        except Exception as e:
                            output = f"执行失败: {e}"
                            success = False

                else:
                    output = f"未知命令类型: {cmd_match.type}"
                    success = False

            except Exception as e:
                output = f"执行失败: {e}"
                success = False

            results.append(CommandResult(
                type=cmd_match.type,
                desc=cmd_match.desc,
                command=cmd,
                output=output,
                success=success
            ))

            if success:
                overall_success = True
                break  # 遇到第一个成功就可以停止执行后续命令

        # 如果全部失败，overall_success=False
        return results


# =========================
# 展示器
# =========================

class CommandResultPrinter:
    console = Console()

    @classmethod
    def print_groups(cls, groups: List[List[CommandResult]]):
        """
        groups: 每组是一组命令的执行结果
        展示每组整体状态 + 每条命令详情
        """
        for idx, results in enumerate(groups, start=1):
            # 检测整体成功
            group_success = any(r.success for r in results)
            group_status = "[bold green]成功[/]" if group_success else "[bold red]失败[/]"

            cls.console.print(f"\n=== 命令组 {idx}: {results[0].desc} ===  整体状态: {group_status}")

            # 构建表格展示每条命令
            table = Table(show_lines=True, expand=True)
            table.add_column("类型", style="cyan", no_wrap=True)
            table.add_column("命令", style="yellow")
            table.add_column("成功", style="green")
            table.add_column("输出", style="white")

            for r in results:
                out_text = Text(str(r.output))
                out_text.stylize("bold green" if r.success else "bold red")

                table.add_row(
                    r.type.value,
                    r.command,
                    str(r.success),
                    out_text
                )

            cls.console.print(table)

    @classmethod
    def print_plain_groups(cls, groups: List[List[CommandResult]]):
        """
        原样输出，每组显示整体状态
        """
        for idx, results in enumerate(groups, start=1):
            group_success = any(r.success for r in results)
            print(f"\n=== 命令组 {idx}: {results[0].desc} ===  整体状态: {'成功' if group_success else '失败'}")
            for r in results:
                print(f"  [{r.type.value}] 命令: {r.command}")
                print(f"      成功: {r.success}")
                print(f"      输出: {r.output}")
            print("-" * 60)


# =========================
# 示例使用
# =========================

if __name__ == "__main__":
    raw_cmd = CommandMatch(
        type=CommandType.RAW,
        desc="Python 版本查看",
        commands=["java -versadsion", "python -V"]
    )

    run_cmd = CommandMatch(
        type=CommandType.RUN,
        desc="conda信息美化输出",
        commands=["conda-info -fail -18", "conda-info -blue -18"]
    )

    executor = CommandExecutor()
    group_results = [
        executor.execute(raw_cmd),
        executor.execute(run_cmd)
    ]

    # Rich 表格展示
    CommandResultPrinter.print_groups(group_results)

    # 原样输出
    CommandResultPrinter.print_plain_groups(group_results)
