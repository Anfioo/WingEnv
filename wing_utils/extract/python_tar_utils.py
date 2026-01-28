import os
import tarfile
import time
from typing import Optional
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, SpinnerColumn, TextColumn

console = Console()


class PythonTarUtils:
    """使用 Python 内置库实现的 Tar 解压工具，支持 Rich 美化输出"""

    @classmethod
    def extract_with_rich(cls, file_path: str, dest_dir: Optional[str] = None) -> bool:
        """
        使用 Python tarfile 库解压，提供类似 7z 的 Rich 界面
        注：tar 格式通常不直接支持密码加密
        """
        if not os.path.exists(file_path):
            console.print(f"[bold red]错误:[/bold red] 文件不存在 {file_path}")
            return False

        # 1. 准备目录
        if dest_dir is None:
            # 自动去掉 .tar.gz, .tar, .tgz 等后缀
            dest_dir = re.sub(r'\.tar(\..*)?$', '', file_path)
        os.makedirs(dest_dir, exist_ok=True)

        archive_name = os.path.basename(file_path)
        console.print(f"\n[bold cyan]开始解析 TAR: [green]{archive_name}[/green][/bold cyan]")

        # 2. 设置 Rich 进度条
        progress = Progress(
            SpinnerColumn(style="bold cyan"),
            "[bold blue]{task.fields[status]}[/bold blue]",
            "•",
            BarColumn(style="white", complete_style="green", finished_style="bold green", pulse_style="green"),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "[progress.description]{task.description}",
        )

        task_id = progress.add_task("[cyan]扫描档案中...[/cyan]", total=100, status="运行中")

        try:
            # 使用 errorlevel=1 确保遇到损坏的 tar 会抛出异常
            with tarfile.open(file_path, 'r:*', errorlevel=1) as tf:
                # 打印档案基本信息
                # 注意：对于巨大的 tar 文件，getmembers() 可能会有轻微延迟
                members = tf.getmembers()
                total_files = len(members)
                total_size = sum(m.size for m in members)

                # 模拟 7z 的元数据展示
                console.print(f"[white]Scanning the archive for entries:[/white]")
                console.print(
                    f"[bold magenta]{total_files} items[/bold magenta], [bold green]{total_size / 1024 / 1024:.2f} MiB[/bold green]")
                console.print(f"[dim]--[/dim]")

                meta_data = {
                    "Path": file_path,
                    "Type": "tar (posix)",
                    "Physical Size": f"{os.path.getsize(file_path)} bytes",
                    "Total Items": str(total_files)
                }

                alt_color = True
                for k, v in meta_data.items():
                    color = "bold cyan" if alt_color else "bold green"
                    console.print(f"  [white]{k:15}[/white] : [{color}]{v}[/{color}]")
                    alt_color = not alt_color

                # 3. 开始解压逻辑
                extracted_count = 0

                with Live(Panel(progress, title="[bold green]Python Tar 解压任务[/bold green]", expand=True),
                          console=console, refresh_per_second=10):

                    for member in members:
                        # 格式化显示路径
                        display_name = (member.name[:50] + '..') if len(member.name) > 52 else member.name
                        progress.update(task_id,
                                        description="[cyan]正在提取:[/cyan] [yellow]{name}[/yellow]".format(
                                            name=display_name))

                        # 执行解压
                        tf.extract(member, path=dest_dir, filter='fully_trusted')

                        # 更新进度
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
                    progress.refresh()
                    time.sleep(0.5)

                console.print("\n[bold green]✅ Tar 解压完成！[/bold green]")
                return True

        except tarfile.ReadError:
            console.print(f"\n[bold red]❌ 错误: 无法读取或损坏的 Tar 文件[/bold red]")
            return False
        except Exception as e:
            console.print(f"\n[bold red]运行时异常: {e}[/bold red]")
            return False


# --- 使用示例 ---
if __name__ == "__main__":
    import re  # 补齐正则依赖

    # 替换为你实际的 tar 文件名，如 test.tar.gz
    PythonTarUtils.extract_with_rich("seven_zip_utils.tar", "./output")
