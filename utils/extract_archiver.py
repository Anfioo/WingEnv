import os
import zipfile
import tarfile

from wing_ui.progress_bar import get_progress_bar_context


def get_top_level_dirs(members) -> set:
    """
    获取所有顶级路径元素（可能是文件或目录）
    """
    top_dirs = set()
    for member in members:
        name = member.filename if isinstance(member, zipfile.ZipInfo) else member.name
        name = name.lstrip("/")
        parts = name.split('/')
        if parts:
            top_dirs.add(parts[0])
    return top_dirs


def extract_archive_with_progress(
        archive_path: str,
        extract_to: str,
        use_true_color: bool = True,
) -> str:
    """
    解压 zip 或 tar.gz 文件，并显示进度条。
    根据归档结构智能判断解压目录。
    """
    print(f"📦 正在解压: {archive_path}")
    os.makedirs(extract_to, exist_ok=True)

    archive_name = os.path.splitext(os.path.basename(archive_path))[0]
    top_level_dir = ""
    final_extract_path = extract_to

    if archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            members = zip_ref.infolist()
            top_dirs = get_top_level_dirs(members)

            # 判断解压路径
            if len(top_dirs) == 1:
                top_level_dir = list(top_dirs)[0]
            else:
                # 多顶级目录或散文件 → 创建以压缩包名命名的目录
                final_extract_path = os.path.join(extract_to, archive_name)

            os.makedirs(final_extract_path, exist_ok=True)

            pb, iterator = get_progress_bar_context(
                iterable=members,
                task_description="📂 解压中 (.zip)",
                title="📦 ZIP 解压"
            )
            with pb:
                for member in iterator:
                    zip_ref.extract(member, path=final_extract_path)

    elif archive_path.endswith((".tar.gz", ".tgz")):
        with tarfile.open(archive_path, 'r:gz') as tar:
            members = tar.getmembers()
            top_dirs = get_top_level_dirs(members)

            if len(top_dirs) == 1:
                top_level_dir = list(top_dirs)[0]
            else:
                final_extract_path = os.path.join(extract_to, archive_name)

            os.makedirs(final_extract_path, exist_ok=True)

            pb, iterator = get_progress_bar_context(
                iterable=members,
                task_description="📂 解压中 (.tar.gz)",
                title="📦 TAR.GZ 解压"
            )
            with pb:
                for member in iterator:
                    tar.extract(member, path=final_extract_path)

    else:
        raise ValueError(f"❌ 不支持的压缩格式: {archive_path}")

    real_path = (
        os.path.join(final_extract_path, top_level_dir)
        if top_level_dir
        else final_extract_path
    )

    print(f"\n✅ 解压完成到: {real_path}")
    return real_path


extract_archive_with_progress(
    r"C:\Users\Anfioo\Downloads\XDownDownload\OBS-Studio-31.0.4-Windows.zip",
    r"C:\Users\Anfioo\Downloads\XDownDownload\out")
