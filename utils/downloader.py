import os
import requests
from urllib.parse import urlparse
from prompt_toolkit.output import ColorDepth

from utils.progress_bar_config import ProgressBarConfig
from wing_ui.progress_bar import get_progress_bar_context  # 你现有的统一进度条包装器


def get_filename_from_url(url: str) -> str:
    """
    从 URL 中提取文件名。
    """
    path = urlparse(url).path
    return os.path.basename(path)


def download_with_progress(url: str, save_dir: str, use_true_color: bool = True) -> str:
    """
    下载文件并显示统一风格的进度条。
    :param url: 下载链接
    :param save_dir: 本地保存目录
    :param use_true_color: 是否使用 TrueColor 彩虹进度条
    :return: 下载后的完整路径
    """
    filename = get_filename_from_url(url)
    full_path = os.path.join(save_dir, filename)

    print(f"⬇️ 正在下载: {filename}")
    os.makedirs(save_dir, exist_ok=True)

    headers = {}
    with requests.get(url, stream=True, headers=headers) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('Content-Length', 0))

        if total_size == 0:
            print("⚠️ 无法获取文件大小，切换普通下载...")
            with open(full_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"\n✅ 下载完成: {full_path}")
            return full_path

        chunk_size = 8192
        total_chunks = total_size // chunk_size

        def chunk_generator():
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    yield chunk

        pb, iterator = get_progress_bar_context(
            iterable=chunk_generator(),
            task_description=f"⬇️ 下载中 ({filename})",
            title="📥 文件下载",
            total=total_chunks,
            use_true_color=use_true_color
        )

        with pb:
            with open(full_path, 'wb') as f:
                for chunk in iterator:
                    f.write(chunk)

    print(f"\n✅ 下载完成: {full_path}")
    return full_path


if __name__ == '__main__':
    download_with_progress(
        url="https://download.java.net/java/GA/jdk12.0.2/e482c34c86bd4bf8b56c0b35558996b9/10/GPL/openjdk-12.0.2_windows-x64_bin.zip",
        save_dir="C:\\Users\\Anfioo\\Downloads\\Demo",
        use_true_color=True
    )
