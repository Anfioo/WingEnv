import os
import gzip
import bz2
import lzma
import time
from typing import Optional, Callable
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, SpinnerColumn, DownloadColumn, TransferSpeedColumn

console = Console()


class PythonSingleFileUtils:
    """使用 Python 内置库处理单文件压缩 (.gz, .bz2, .xz)"""

    @classmethod
    def extract_with_rich(cls, file_path: str, dest_dir: Optional[str] = None) -> bool:
        """
        解压单文件压缩包，并实时显示写入进度
        """
        if not os.path.exists(file_path):
            console.print(f"[bold red]错误:[/bold red] 文件不存在 {file_path}")
            return False

        # 1. 自动识别类型与目标路径
        ext = os.path.splitext(file_path)[1].lower()
        opener_map = {'.gz': gzip.open, '.bz2': bz2.open, '.xz': lzma.open}
        type_name = {'.gz': 'GZIP', '.bz2': 'BZIP2', '.xz': 'LZMA'}.get(ext, 'Unknown')

        if ext not in opener_map:
            console.print(f"[bold red]错误:[/bold red] 不支持的后缀名 {ext}")
            return False

        # 推导解压后的文件名 (去掉最后一层后缀)
        default_name = os.path.basename(file_path)
        output_filename = default_name[:default_name.rfind(ext)] if ext in default_name else default_name + ".out"

        if dest_dir is None:
            dest_path = output_filename
        else:
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, output_filename)

        # 2. 获取原始文件大小 (用于进度条参考)
        # 注意：对于单文件压缩，通常只能获取压缩后的 Physical Size
        compressed_size = os.path.getsize(file_path)

        console.print(f"\n[bold cyan]开始解压单文件: [green]{type_name}[/green][/bold cyan]")
        console.print(f"  [white]Source[/white] : [bold yellow]{file_path}[/bold yellow]")
        console.print(f"  [white]Output[/white] : [bold green]{dest_path}[/bold green]")
        console.print(f"[dim]--[/dim]")

        # 3. 设置进度条 (以读取压缩流的大小为进度)
        progress = Progress(
            SpinnerColumn(),
            "[bold blue]{task.fields[status]}[/bold blue]",
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.0f}%",
            DownloadColumn(),
            TransferSpeedColumn(),
        )

        task_id = progress.add_task("[cyan]正在流式解压...[/cyan]", total=compressed_size, status="读取中")

        try:
            # 这里的思路是：监控压缩文件的读取位置来更新进度条
            with opener_map[ext](file_path, 'rb') as f_in:
                with open(dest_path, 'wb') as f_out:
                    with Live(Panel(progress, title=f"[bold green]{type_name} 实时解压[/bold green]"),
                              console=console, refresh_per_second=10):

                        chunk_size = 1024 * 64  # 64KB 缓冲区
                        while True:
                            chunk = f_in.read(chunk_size)
                            if not chunk:
                                break
                            f_out.write(chunk)

                            # 更新进度：由于 f_in 是压缩句柄，tell() 通常返回已读取的压缩字节数
                            # 这能非常准确地反映解压进度
                            try:
                                current_pos = f_in.tell()
                                progress.update(task_id, completed=current_pos)
                            except (AttributeError, io.UnsupportedOperation):
                                # 某些模式下 tell 可能不可用，则手动估算
                                progress.update(task_id, advance=len(chunk) / 2)  # 估算值

                    progress.update(task_id, status="已完成", completed=compressed_size)

            console.print(f"\n[bold green]✅ 解压成功![/bold green] 文件已保存至: {dest_path}")
            return True

        except Exception as e:
            console.print(f"\n[bold red]❌ 解压失败: {e}[/bold red]")
            if os.path.exists(dest_path):
                os.remove(dest_path)  # 出错时清理残余文件
            return False


# --- 使用示例 ---
if __name__ == "__main__":
    PythonSingleFileUtils.decompress_with_rich("dd.py.gz", "./aa")
    # 注意：如果是 .tar.gz，建议用之前的 TarUtils，因为那会处理归档逻辑
    # 这个 Utils 主要用于处理单纯的 .gz 或 .xz 数据文件
    pass
