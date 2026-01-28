import os
import gzip
import time
from typing import Optional
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, SpinnerColumn, DownloadColumn, TransferSpeedColumn

console = Console()


class PythonGzipUtils:
    """使用 Python 内置库将单个文件压缩为 .gz 格式"""

    @classmethod
    def compress_with_rich(cls, file_path: str, dest_path: Optional[str] = None, compress_level: int = 9) -> bool:
        """
        将文件压缩为 .gz，并显示进度条
        :param file_path: 源文件路径
        :param dest_path: 目标路径（默认为 源文件名.gz）
        :param compress_level: 压缩率 1-9，9为最高
        """
        if not os.path.exists(file_path):
            console.print(f"[bold red]错误:[/bold red] 文件不存在 {file_path}")
            return False

        # 1. 确定输出路径
        if dest_path is None:
            dest_path = file_path + ".gz"

        source_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)

        console.print(f"\n[bold cyan]准备 Gzip 压缩:[/bold cyan] [green]{file_name}[/green]")
        console.print(f"  [white]原始大小[/white] : [bold magenta]{source_size / 1024 / 1024:.2f} MiB[/bold magenta]")
        console.print(f"  [white]压缩级别[/white] : [bold yellow]{compress_level}[/bold yellow]")
        console.print(f"[dim]--[/dim]")

        # 2. 配置进度条 (以读取源文件的字节数为进度)
        progress = Progress(
            SpinnerColumn(),
            "[bold blue]{task.fields[status]}[/bold blue]",
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.0f}%",
            DownloadColumn(),  # 这里显示的是处理的原始字节数
            TransferSpeedColumn(),
        )

        task_id = progress.add_task("[cyan]正在压缩...[/cyan]", total=source_size, status="读取中")

        try:
            with open(file_path, 'rb') as f_in:
                # compresslevel 默认为 9 (最高压缩比)
                with gzip.open(dest_path, 'wb', compresslevel=compress_level) as f_out:
                    with Live(Panel(progress, title="[bold green]Gzip 压缩任务[/bold green]"),
                              console=console, refresh_per_second=10):

                        chunk_size = 1024 * 128  # 128KB 缓冲区
                        while True:
                            chunk = f_in.read(chunk_size)
                            if not chunk:
                                break
                            f_out.write(chunk)

                            # 更新进度
                            progress.update(task_id, advance=len(chunk))

                    progress.update(task_id, status="已完成", completed=source_size)

            # 获取压缩后的大小
            compressed_size = os.path.getsize(dest_path)
            ratio = (1 - (compressed_size / source_size)) * 100

            console.print(f"\n[bold green]✅ 压缩完成![/bold green]")
            console.print(f"  [white]输出路径[/white] : [yellow]{dest_path}[/yellow]")
            console.print(
                f"  [white]压缩后大小[/white]: [bold green]{compressed_size / 1024 / 1024:.2f} MiB[/bold green] (减少了 {ratio:.1f}%)")
            return True

        except Exception as e:
            console.print(f"\n[bold red]❌ 压缩失败: {e}[/bold red]")
            if os.path.exists(dest_path):
                os.remove(dest_path)
            return False


# --- 使用示例 ---
if __name__ == "__main__":
    # 压缩当前目录下的某个文件
    PythonGzipUtils.compress_with_rich("dd.py")
