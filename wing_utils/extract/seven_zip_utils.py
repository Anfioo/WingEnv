import os
import re
import sys
import shutil
import subprocess
from typing import Optional, List

from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, SpinnerColumn, TextColumn
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from wing_utils.ui import console


class SevenZipUtils:
    """7-Zip Windows 专用工具类"""

    _EXE_PATH: Optional[str] = None

    @classmethod
    def _find_7z(cls) -> str:
        """多维度定位 7z.exe 路径"""
        if cls._EXE_PATH:
            return cls._EXE_PATH

        # 1. 检查环境变量
        env_path = shutil.which("7z.exe")
        if env_path:
            cls._EXE_PATH = env_path
            return env_path

        # 2. 检查 Windows 注册表
        if sys.platform == "win32":
            import winreg
            reg_paths = [
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\7-Zip"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\7-Zip")
            ]
            for root, sub_key in reg_paths:
                try:
                    with winreg.OpenKey(root, sub_key) as key:
                        install_path, _ = winreg.QueryValueEx(key, "Path")
                        full_path = os.path.join(install_path, "7z.exe")
                        if os.path.exists(full_path):
                            cls._EXE_PATH = full_path
                            return full_path
                except (FileNotFoundError, OSError):
                    continue

        # 3. 常见默认安装路径兜底
        common_paths = [
            os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "7-Zip", "7z.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "7-Zip", "7z.exe")
        ]
        for path in common_paths:
            if os.path.exists(path):
                cls._EXE_PATH = path
                return path

        return ""

    @classmethod
    def is_installed(cls) -> bool:
        """检查系统是否安装了 7-Zip"""
        return cls._find_7z() != ""

    @classmethod
    def extract(cls, file_path: str, dest_dir: Optional[str] = None, password: Optional[str] = None):
        exe = cls._find_7z()
        if not exe:
            print("未找到 7-Zip")
            return False

        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return False

        if dest_dir is None:
            dest_dir = os.path.splitext(file_path)[0]
        os.makedirs(dest_dir, exist_ok=True)

        cmd = [exe, "x", file_path, f"-o{dest_dir}", "-y", "-bsp1"]
        if password:
            cmd.append(f"-p{password}")

        print(f"开始解压: {file_path}")
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
            for line in proc.stdout:
                line = line.strip()
                if line:
                    # 解析进度输出，7z 输出示例: " 10% 1234 KB 0:00:01"
                    if "%" in line:
                        print(line)  # 这里可以换成 Rich 或 GUI 控件显示
                    else:
                        print(line)

            proc.wait()
            if proc.returncode == 0:
                print("解压完成")
                return True
            else:
                print(f"解压失败，返回码 {proc.returncode}")
                return False

    @classmethod
    def _parse_7z_line(cls, line: str, progress: Progress, task_id: any):
        """解析 7z 输出行并更新进度条"""
        # 匹配进度行，例如:  10% 1234 - path/to/file
        # 7z 的输出可能包含多个空格和特殊格式
        progress_match = re.search(r"(\d+)%\s+(\d+)?\s*(?:-\s*(.*))?", line)

        if progress_match:
            percentage = int(progress_match.group(1))
            # count = progress_match.group(2) # 已处理项数
            current_file = progress_match.group(3)

            progress.update(task_id, completed=percentage)
            if current_file:
                # 截断过长的文件名以防止换行破坏 UI
                display_name = (current_file[:50] + '..') if len(current_file) > 52 else current_file
                progress.update(task_id, description=f"[cyan]正在解压:[/cyan] [yellow]{display_name}[/yellow]")
            return True
        return False

    @classmethod
    def extract_with_rich(cls, file_path: str, dest_dir: Optional[str] = None, password: Optional[str] = None) -> bool:
        exe = cls._find_7z()
        if not exe or not os.path.exists(file_path):
            console.print(f"[bold red]错误:[/bold red] 找不到 7-Zip 或文件 {file_path}")
            return False

        if dest_dir is None:
            dest_dir = os.path.splitext(file_path)[0]
        os.makedirs(dest_dir, exist_ok=True)

        # 核心命令：-bsp1 将进度推送到 stdout
        cmd = [exe, "x", file_path, f"-o{dest_dir}", "-y", "-bsp1"]
        if password:
            cmd.append(f"-p{password}")

        # 设置 Rich 进度条
        progress = Progress(
            SpinnerColumn(style="bold cyan"),
            "[bold blue]{task.fields[status]}[/bold blue]",
            "•",
            BarColumn(style="white", complete_style="green", finished_style="bold green", pulse_style="green"),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "[progress.description]{task.description}",
        )

        task_id = progress.add_task("[cyan]准备解压...[/cyan]", total=100, status="运行中")

        # 记录头部信息和配置信息
        info_table = Table(show_header=False, box=None, padding=(0, 1))

        is_header_section = True  # 是否在处理 -- 之前的头部信息
        alt_color = False  # 用于交替颜色

        try:
            with Live(Panel(progress, title="[bold green]7-Zip 解压任务[/bold green]", expand=True), console=console,
                      refresh_per_second=10) as live:
                with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                      bufsize=1) as proc:
                    for line in proc.stdout:
                        clean_line = line.strip()
                        if not clean_line:
                            continue

                        # 1. 处理进度更新 (包含 % 的行)
                        if "%" in clean_line:
                            cls._parse_7z_line(clean_line, progress, task_id)
                            continue

                        # 2. 处理分隔符 --
                        if clean_line == "--":
                            is_header_section = False
                            continue

                        # 3. 处理头部扫描信息
                        if is_header_section:
                            if "Scanning" in clean_line:
                                console.print(f"[bold blue]🔍 {clean_line}[/bold blue]")
                            elif "file" in clean_line and "bytes" in clean_line:
                                # 强化显示文件大小和数量
                                parts = re.split(r"(\d+ file|[\d\s\w]+\sMiB|[\d\s\w]+\sGiB|[\d\s\w]+\sKiB)", clean_line)
                                styled_line = ""
                                for p in parts:
                                    if "file" in p:
                                        styled_line += f"[bold magenta]{p}[/bold magenta]"
                                    elif "MiB" in p or "GiB" in p:
                                        styled_line += f"[bold green]{p}[/bold green]"
                                    else:
                                        styled_line += p
                                console.print(styled_line)
                            elif "7-Zip" in clean_line:
                                console.print(f"[dim white]{clean_line}[/dim white]")
                            else:
                                console.print(clean_line)

                        # 4. 处理档案元数据 (Path, Type, Size...)
                        else:
                            if "=" in clean_line:
                                key, value = [x.strip() for x in clean_line.split("=", 1)]
                                color = "bold cyan" if alt_color else "bold green"
                                console.print(f"  [white]{key:15}[/white] : [{color}]{value}[/{color}]")
                                alt_color = not alt_color
                            elif "ERROR" in clean_line:
                                console.print(f"[bold red]✘ {clean_line}[/bold red]")

                    proc.wait()

                if proc.returncode == 0:
                    progress.update(task_id, description="[bold green]解压成功[/bold green]", completed=100,
                                    status="已完成")
                    return True
                else:
                    progress.update(task_id, description=f"[bold red]解压失败 (Code {proc.returncode})[/bold red]",
                                    status="出错")
                    return False
        except Exception as e:
            console.print(f"[bold red]运行时异常: {e}[/bold red]")
            return False

    @classmethod
    def extract_with_rich_all(cls, file_path: str, dest_dir: Optional[str] = None,
                              password: Optional[str] = None) -> bool:
        """
        使用 Rich 美化输出的 7z 解压方法
        :param file_path: 7z 压缩包路径
        :param dest_dir: 解压目标目录
        :param password: 压缩包密码（可选）
        :return: 解压成功返回 True，失败返回 False
        """
        exe = cls._find_7z()
        if not exe:
            console.print("[bold red]未找到 7-Zip 程序，请确认已安装并配置环境变量！[/bold red]")
            return False

        if not os.path.exists(file_path):
            console.print(f"[bold red]文件不存在: [white]{file_path}[/white][/bold red]")
            return False

        # 处理默认解压目录
        if dest_dir is None:
            dest_dir = os.path.splitext(file_path)[0]
        os.makedirs(dest_dir, exist_ok=True)

        # 构建 7z 解压命令
        cmd = [exe, "x", file_path, f"-o{dest_dir}", "-y", "-bsp1"]
        if password:
            cmd.append(f"-p{password}")

        # 打印解压开始提示
        archive_name = os.path.basename(file_path)
        console.print(f"\n[bold cyan]开始解压: [green]{archive_name}[/green][/bold cyan]")

        # 状态跟踪变量
        stage = "initial"  # initial: 初始信息阶段 | archive_info: 归档信息阶段 | progress: 进度阶段
        alt_color_idx = 0  # 交替颜色计数器
        alt_colors = ["blue", "magenta"]  # 归档信息行的交替颜色
        # 编译正则表达式（提前编译提升性能）
        progress_re = re.compile(r"^(\d+)%(\s+\d+)?(\s+.+)?$")  # 匹配进度行：% 数字 文件路径
        archive_info_re = re.compile(r"^(\w+(\s+\w+)*)\s*=\s*(.+)$")  # 匹配归档信息行：Key = Value
        error_re = re.compile(r"^ERROR: (.+)$")  # 匹配错误行
        size_re = re.compile(r"(\d+\s+MiB|\d+\s+KiB|\d+\s+GiB|\d+\s+bytes)")  # 匹配文件大小
        file_count_re = re.compile(r"(\d+)\s+file[s]?")  # 匹配文件数量

        try:
            # 启动子进程执行解压命令
            with subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
            ) as proc:
                # 逐行读取输出
                for line in iter(proc.stdout.readline, ''):
                    line = line.strip()
                    if not line:
                        continue

                    # 阶段1：初始信息（到 -- 行之前）
                    if stage == "initial":
                        if line == "--":
                            # 切换到归档信息阶段
                            stage = "archive_info"
                            console.print(f"[dim]{line}[/dim]")
                            continue

                        # 高亮初始信息中的关键内容
                        colored_line = line
                        # 高亮文件数量
                        colored_line = file_count_re.sub(r"[bold green]\1[/bold green] file", colored_line)
                        # 高亮文件大小
                        colored_line = size_re.sub(r"[bold yellow]\1[/bold yellow]", colored_line)
                        # 高亮压缩包名称
                        colored_line = colored_line.replace(archive_name, f"[bold green]{archive_name}[/bold green]")
                        # 基础颜色：青色
                        console.print(f"[cyan]{colored_line}[/cyan]")

                    # 阶段2：归档信息行（Path=... 等）
                    elif stage == "archive_info":
                        # 检测是否进入进度阶段（包含 % 符号）
                        if "%" in line:
                            stage = "progress"
                        else:
                            # 匹配 Key = Value 格式的归档信息
                            info_match = archive_info_re.match(line)
                            if info_match:
                                key = info_match.group(1)
                                value = info_match.group(3)
                                # 交替颜色显示 Key，白色加粗显示 Value
                                current_color = alt_colors[alt_color_idx % len(alt_colors)]
                                alt_color_idx += 1
                                console.print(
                                    f"[{current_color}]{key} = [bold white]{value}[/bold white][/{current_color}]")
                            else:
                                # 非 Key=Value 格式的归档信息，灰色显示
                                console.print(f"[dim white]{line}[/dim white]")

                    # 阶段3：进度行（百分比、文件路径等）
                    elif stage == "progress":
                        # 处理错误行：红色加粗
                        error_match = error_re.match(line)
                        if error_match:
                            console.print(f"[bold red]{error_match.group(0)}[/bold red]")
                            continue

                        # 解析进度行的百分比、大小、文件路径
                        prog_match = progress_re.match(line)
                        if prog_match:
                            percent = prog_match.group(1)  # 百分比
                            size = prog_match.group(2) or ""  # 大小数字
                            file_part = prog_match.group(3) or ""  # 文件路径部分

                            # 组合进度行，不同部分不同颜色
                            progress_text = ""
                            progress_text += f"[bold yellow]{percent}%[/bold yellow]"  # 百分比：黄色加粗
                            if size:
                                progress_text += f"[bold cyan]{size}[/bold cyan]"  # 大小：青色加粗
                            if file_part:
                                progress_text += f"[white]{file_part}[/white]"  # 文件路径：白色
                            console.print(progress_text)
                        else:
                            # 其他进度相关行：浅灰色显示
                            console.print(f"[dim white]{line}[/dim white]")

                # 等待进程结束并检查返回码
                proc.wait()
                if proc.returncode == 0:
                    console.print("\n[bold green]✅ 解压完成！[/bold green]")
                    return True
                else:
                    console.print(f"\n[bold red]❌ 解压失败，返回码 {proc.returncode}[/bold red]")
                    return False

        except Exception as e:
            console.print(f"\n[bold red]解压过程中发生异常: [white]{str(e)}[/white][/bold red]")
            return False


# --- 使用示例 ---
if __name__ == "__main__":
    # 示例 1: 基础解压
    SevenZipUtils.extract_with_rich_all(r"环保数据监控中心_模板.7z", "./aa", password="123456")
