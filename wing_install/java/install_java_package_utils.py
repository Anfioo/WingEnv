import os
from wing_env_ui.down_file_progress_bar_ui_util import download_with_progress
from wing_env_ui.extract_file_progress_bar_ui_util import extract_archive_with_progress


def install_java_package(download_url: str, install_dir: str, use_true_color: bool = True):
    """
    下载并解压一个 Java 安装包（带进度条 UI）。

    :param download_url: 安装包下载链接
    :param install_dir: 安装基础目录（压缩包将解压在此）
    :param use_true_color: 是否使用 24 位彩虹进度条（默认 True）
    """
    os.makedirs(install_dir, exist_ok=True)
    download_dir = os.path.join(install_dir, "Download")
    os.makedirs(download_dir, exist_ok=True)

    file_name = download_url.split("/")[-1]
    file_path = os.path.join(download_dir, file_name)

    print(f"目标文件路径：{file_path}")

    if os.path.exists(file_path):
        print(f"安装包文件已存在，跳过下载：{file_name}")
    else:
        # ✅ 使用封装好的进度条下载器
        download_with_progress(
            url=download_url,
            save_dir=download_dir,
            use_true_color=use_true_color
        )

    # ✅ 使用封装好的进度条解压器
    progress = extract_archive_with_progress(archive_path=file_path, extract_to=install_dir,
                                             use_true_color=use_true_color)

    return progress

