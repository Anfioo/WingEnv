import os
import re
import time
import zipfile
from typing import Optional
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, SpinnerColumn, TextColumn
from rich.table import Table

from wing_utils.ui import console


class PythonZipUtils:
    """使用 Python 内置库实现的 Zip 解压工具，支持 Rich 美化输出"""

    @classmethod
    def extract_with_rich(cls, file_path: str, dest_dir: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        使用 Python zipfile 库解压，并提供类似 7z 的 Rich 界面
        """
        if not os.path.exists(file_path):
            console.print(f"[bold red]错误:[/bold red] 文件不存在 {file_path}")
            return False

        # 1. 准备目录
        if dest_dir is None:
            dest_dir = os.path.splitext(file_path)[0]
        os.makedirs(dest_dir, exist_ok=True)

        archive_name = os.path.basename(file_path)
        console.print(f"\n[bold cyan]开始解析 ZIP: [green]{archive_name}[/green][/bold cyan]")

        # 2. 设置 Rich 进度条 (保持与 7z 风格一致)
        progress = Progress(
            SpinnerColumn(style="bold cyan"),
            "[bold blue]{task.fields[status]}[/bold blue]",
            "•",
            BarColumn(style="white", complete_style="green", finished_style="bold green", pulse_style="green"),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "[progress.description]{task.description}",
        )

        task_id = progress.add_task("[cyan]准备解压...[/cyan]", total=100, status="运行中")

        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                # 打印档案基本信息
                info_list = zf.infolist()
                total_files = len(info_list)
                total_size = sum(info.file_size for info in info_list)

                # 模拟 7z 的元数据展示
                console.print(f"[white]Scanning the drive for archives:[/white]")
                console.print(
                    f"[bold magenta]{total_files} files[/bold magenta], [bold green]{total_size / 1024 / 1024:.2f} MiB[/bold green]")
                console.print(f"[dim]--[/dim]")

                # 打印 Path/Type 等信息 (复刻 7z 样式)
                meta_data = {
                    "Path": file_path,
                    "Type": "zip",
                    "Physical Size": f"{os.path.getsize(file_path)} bytes",
                    "Files": str(total_files)
                }

                alt_color = True
                for k, v in meta_data.items():
                    color = "bold cyan" if alt_color else "bold green"
                    console.print(f"  [white]{k:15}[/white] : [{color}]{v}[/{color}]")
                    alt_color = not alt_color

                # 3. 开始解压逻辑
                pwd_bytes = password.encode('utf-8') if password else None
                extracted_count = 0

                with Live(Panel(progress, title="[bold green]Python Zip 解压任务[/bold green]", expand=True),
                          console=console, refresh_per_second=10):

                    for member in info_list:
                        # 更新当前处理的文件名
                        display_name = (member.filename[:50] + '..') if len(member.filename) > 52 else member.filename
                        progress.update(task_id,
                                        description="[cyan]正在解压:[/cyan] [yellow]{display_name}[/yellow]".format(
                                            display_name=display_name))

                        # 执行解压
                        zf.extract(member, path=dest_dir, pwd=pwd_bytes)

                        # 更新进度百分比
                        extracted_count += 1
                        percentage = int((extracted_count / total_files) * 100)
                        progress.update(task_id, completed=percentage)

                    # 完成状态
                    progress.update(
                        task_id,
                        description="[bold green]解压完成[/bold green]",
                        completed=100,
                        status="已完成"
                    )
                    # 添加刷新和足够长的等待时间
                    progress.refresh()
                    time.sleep(1)  # 增加到 2 秒

                console.print("\n[bold green]✅ 解压完成！[/bold green]")
                return True

        except RuntimeError as e:
            if 'password' in str(e).lower():
                console.print(f"\n[bold red]❌ 需要密码或密码错误[/bold red]")
            else:
                console.print(f"\n[bold red]❌ 运行时错误: {e}[/bold red]")
            return False
        except Exception as e:
            console.print(f"\n[bold red]运行时异常: {e}[/bold red]")
            return False


# --- 使用示例 ---
if __name__ == "__main__":
    # 确保你有一个 test.zip 或者修改为你的文件名
    PythonZipUtils.extract_with_rich(r"JDK.zip", "./aa")
