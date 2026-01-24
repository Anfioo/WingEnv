import os
from pathlib import Path
from typing import Optional, Union


class RootPathUtils:
    """
    项目根目录控制工具

    功能：
    - 统一项目根目录
    - 支持绝对 / 相对路径
    - 支持自动推断
    - 显式初始化，避免 import 副作用
    """

    _root_path: Optional[Path] = None
    _initialized: bool = False

    @classmethod
    def init(
        cls,
        path: Optional[Union[str, Path]] = None,
        *,
        chdir: bool = True
    ) -> Path:
        """
        初始化项目根目录

        :param path:
            - None：自动推断（当前文件向上两级）
            - 绝对路径
            - 相对路径（相对于调用文件）
        :param chdir: 是否切换 os.getcwd()
        """
        if cls._initialized:
            return cls._root_path

        root = cls._resolve_path(path)
        cls._root_path = root
        cls._initialized = True

        if chdir:
            os.chdir(root)

        return root

    @classmethod
    def _resolve_path(cls, path: Optional[Union[str, Path]]) -> Path:
        if path is None:
            # 默认：调用该方法的文件向上两级
            caller_file = Path(__file__).resolve()
            return caller_file.parent.parent

        path = Path(path)

        if path.is_absolute():
            return path.resolve()

        # 相对路径：相对于调用者文件
        caller_dir = Path(__file__).resolve().parent
        return (caller_dir / path).resolve()

    # =========================
    # 对外只读接口
    # =========================

    @classmethod
    def root(cls) -> Path:
        if not cls._initialized:
            raise RuntimeError("RootPathUtils 未初始化，请先调用 RootPathUtils.init()")
        return cls._root_path

    @classmethod
    def cwd(cls) -> Path:
        """语义化获取当前工作目录"""
        return Path.cwd()
