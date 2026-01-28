import os
from urllib.parse import urlparse
from pathlib import Path
import requests
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, DownloadColumn, \
    TransferSpeedColumn, TimeElapsedColumn, TimeRemainingColumn


class DownloadUtils:
    @staticmethod
    def get_filename_from_url(download_url: str) -> str:
        """从 URL 中提取文件名"""
        path = urlparse(download_url).path
        return os.path.basename(path)

    @staticmethod
    def download(download_url: str, save_dir: str) -> str:
        """下载文件到指定目录，使用 rich 显示进度条"""
        save_dir_path = Path(save_dir)
        save_dir_path.mkdir(parents=True, exist_ok=True)

        filename = DownloadUtils.get_filename_from_url(download_url)
        full_path = save_dir_path / filename

        # 发起请求
        r = requests.get(download_url, stream=True, timeout=30)
        r.raise_for_status()
        total_size = int(r.headers.get("Content-Length", 0))

        # Rich 进度条
        progress = Progress(
            SpinnerColumn(style="bold cyan"),
            TextColumn("[bold]{task.description}"),
            BarColumn(style="white", complete_style="green", finished_style="bold green", pulse_style="green"),
            TaskProgressColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TextColumn("|"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        )

        with progress:
            task_id = progress.add_task(f"下载 {filename}", total=total_size)
            with open(full_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress.update(task_id, advance=len(chunk))

        return str(full_path)


# ==================== 使用示例 ====================
if __name__ == "__main__":
    url = "https://download.oracle.com/graalvm/24/archive/graalvm-jdk-24.0.2_windows-x64_bin.zip"
    saved_file = DownloadUtils.download(url, "./jdks")
    print("下载完成:", saved_file)
