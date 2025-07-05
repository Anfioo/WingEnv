import os
import zipfile
import tarfile
from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.shortcuts.progress_bar import formatters


def get_top_level_dir(members):
    """
    从成员列表推断顶层目录（如果有）
    仅适用于同一级都在一个目录的情况
    """
    # 获取所有成员的第一部分路径
    top_dirs = set()
    for member in members:
        # 获取路径字符串
        name = member.filename if isinstance(member, zipfile.ZipInfo) else member.name
        parts = name.split('/')
        if parts:
            top_dirs.add(parts[0])
    # 如果所有文件都在同一个顶层目录下，返回它，否则返回空字符串
    if len(top_dirs) == 1:
        return top_dirs.pop()
    return ''


def extract_archive_with_progress(archive_path: str, extract_to: str, use_true_color: bool = True):
    print(f"📦 正在解压: {archive_path}")
    os.makedirs(extract_to, exist_ok=True)

    color_depth = ColorDepth.DEPTH_24_BIT if use_true_color else ColorDepth.DEPTH_8_BIT
    custom_formatters = [
        formatters.Label(),
        formatters.Text(" "),
        formatters.Rainbow(formatters.Bar()),
        formatters.Text(" 正在提取: "),
        formatters.Rainbow(formatters.Percentage()),
        formatters.Text(" 剩余时间: "),
        formatters.Rainbow(formatters.TimeLeft()),
    ]

    top_level_dir = ''
    if archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            members = zip_ref.infolist()
            total = len(members)
            with ProgressBar(
                    formatters=custom_formatters,
                    color_depth=color_depth,
            ) as pb:
                for member in pb(members, label="📂 解压中 (.zip)", total=total):
                    zip_ref.extract(member, path=extract_to)
            top_level_dir = get_top_level_dir(members)

    elif archive_path.endswith((".tar.gz", ".tgz")):
        with tarfile.open(archive_path, 'r:gz') as tar:
            members = tar.getmembers()
            total = len(members)
            with ProgressBar(
                    formatters=custom_formatters,
                    color_depth=color_depth,
            ) as pb:
                for member in pb(members, label="📂 解压中 (.tar.gz)", total=total):
                    tar.extract(member, path=extract_to)
            top_level_dir = get_top_level_dir(members)
    else:
        raise ValueError(f"❌ 不支持的文件格式: {archive_path}")

    if top_level_dir:
        real_path = os.path.join(extract_to, top_level_dir)
    else:
        real_path = extract_to

    print(f"\n✅ 解压完成到: {real_path}")
    return real_path
