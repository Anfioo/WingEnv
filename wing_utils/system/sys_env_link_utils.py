import os


def create_symlink(target: str, link_name: str) -> bool:
    # 如果是目录，需要指定 target_is_directory=True
    is_dir = os.path.isdir(target)
    try:
        os.symlink(target, link_name, target_is_directory=is_dir)
        return True
    except OSError:
        return False
