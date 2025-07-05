import os
import requests
from urllib.parse import urlparse
from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.shortcuts.progress_bar import formatters


def get_filename_from_url(url: str) -> str:
    """
    从 URL 中提取文件名。
    """
    path = urlparse(url).path
    return os.path.basename(path)


def download_with_progress(url: str, save_dir: str, use_true_color: bool = True) -> str:
    """
    使用带进度条的下载器下载文件，支持彩虹色进度条。

    :param url: 下载链接
    :param save_dir: 本地保存目录（非文件名）
    :param use_true_color: 是否使用 24 位颜色显示彩虹条
    :return: 下载完成后的完整路径
    """
    filename = get_filename_from_url(url)
    full_path = os.path.join(save_dir, filename)

    headers = {}
    with requests.get(url, stream=True, headers=headers) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('Content-Length', 0))

        os.makedirs(save_dir, exist_ok=True)

        if total_size == 0:
            print("⚠️ 无法获取文件大小，普通方式下载")
            with open(full_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return full_path

        color_depth = ColorDepth.DEPTH_24_BIT if use_true_color else ColorDepth.DEPTH_8_BIT
        custom_formatters = [
            formatters.Label(),
            formatters.Text(" "),
            formatters.Rainbow(formatters.Bar()),
            formatters.Text(" 已下载: "),
            formatters.Rainbow(formatters.Percentage()),
            formatters.Text(" 剩余时间: "),
            formatters.Rainbow(formatters.TimeLeft()),
        ]

        with ProgressBar(
                formatters=custom_formatters,
                color_depth=color_depth,
        ) as pb:
            with open(full_path, 'wb') as f:
                def generate_chunks():
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk

                for chunk in pb(
                        generate_chunks(),
                        label=f"⬇️ 下载中: {filename}",
                        total=total_size // 8192
                ):
                    f.write(chunk)

        print(f"\n✅ 下载完成: {full_path}")
        return full_path


if __name__ == '__main__':
    progress = download_with_progress(
        url="https://download.java.net/java/GA/jdk12.0.2/e482c34c86bd4bf8b56c0b35558996b9/10/GPL/openjdk-12.0.2_windows-x64_bin.zip",
        save_dir="C:\\Users\\Anfioo\\Downloads\\Demo", use_true_color=True)
