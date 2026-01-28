import os
import shutil
from typing import Literal
from datetime import datetime

OnExistsPolicy = Literal["skip", "replace", "backup"]


def _gen_backup_name(path: str) -> str:
    """
    生成备份文件名：xxx.YYYY.MM.DD.HH.MM.SS.bak（含时分秒，避免重复）
    """
    # 格式化字符串增加时分秒：%H(24小时制时)、%M(分)、%S(秒)，用.分隔保持风格统一
    datetime_str = datetime.now().strftime("%Y.%m.%d.%H.%M.%S")
    return f"{path}.{datetime_str}.bak"



def _handle_existing(link_name: str, on_exists: OnExistsPolicy) -> bool:
    """
    处理已存在的软链接 / 文件 / 目录
    返回 False 表示应终止创建
    """
    if not os.path.lexists(link_name):
        return True

    # 直接跳过
    if on_exists == "skip":
        return False

    # 直接替换
    if on_exists == "replace":
        try:
            if os.path.islink(link_name) or os.path.isfile(link_name):
                os.remove(link_name)
            elif os.path.isdir(link_name):
                os.rmdir(link_name)
            return True
        except OSError:
            return False

    # 备份再创建
    if on_exists == "backup":
        try:
            backup_name = _gen_backup_name(link_name)
            shutil.move(link_name, backup_name)
            return True
        except OSError:
            return False

    return False


def create_dir_symlink(
        target_dir: str,
        link_name: str,
        on_exists: OnExistsPolicy = "skip",
) -> bool:
    """
      创建目录软链接
    :param target_dir: 目标目录
    :param link_name: 软连接名称
    :param on_exists: 目录存在的时候的操作，默认为skip
    :return: 是否执行成功
    """
    if not _handle_existing(link_name, on_exists):
        return on_exists == "skip"

    try:
        os.symlink(target_dir, link_name, target_is_directory=True)
        return True
    except OSError:
        return False


def create_file_symlink(
        target_file: str,
        link_name: str,
        on_exists: OnExistsPolicy = "skip",
) -> bool:
    """
      创建文件软链接
    :param target_file: 目标文件
    :param link_name: 软连接名称
    :param on_exists: 文件存在的时候的操作，默认为skip
    :return: 是否执行成功
    """
    if not _handle_existing(link_name, on_exists):
        return on_exists == "skip"

    try:
        os.symlink(target_file, link_name, target_is_directory=False)
        return True
    except OSError:
        return False
