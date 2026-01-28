#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------Project Information------------------
@Project : WingShake->WingEnv
@File : download_manager.py
@Path : loader/ini
@Author : Anfioo
@Date : 2026/1/29 18:44
------------------------Contact------------------------
@Github : https://github.com/Anfioo
@Gmail : anfioozys@gmail.com
@QQ Email : 3485977506@qq.com
"""
from pathlib import Path
from typing import Optional, Dict

from wing_utils import IniConfigUtils


class DownloadsManager:
    def __init__(self):
        self.config = IniConfigUtils()
        self.section_user = "user"
        self.section_download = "download"

    def add_download(self, name: str, file_path: str):
        """添加新的下载文件映射"""
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        self.config.set(self.section_download, name, str(path))

    def remove_download(self, name: str):
        """删除下载文件映射（不删除实际文件）"""
        self.config.delete(self.section_download, name)

    def list_downloads(self) -> Dict[str, str]:
        """列出所有下载文件及其对应路径"""
        return self.config.get_section(self.section_download)

    def get_download_path(self, name: str) -> Optional[str]:
        """获取指定下载文件的路径"""
        return self.config.get(self.section_download, name)

    def download_exists(self, name: str) -> bool:
        """是否存在指定下载文件"""
        return self.config.has(self.section_download, name)

    def get_current_downloads_dir(self) -> Path:
        """获取下载目录路径"""
        # 首先尝试从配置中获取
        downloads_path = self.config.get(self.section_user, "downloads_path")
        if downloads_path:
            return Path(downloads_path).expanduser().resolve()
        # 默认下载目录：配置路径下的downloads
        config_path = self.config.getConfigWorkingPath()
        return config_path / "downloads"

    def set_downloads_dir(self, path: str):
        """设置下载目录路径"""
        downloads_path = Path(path).expanduser().resolve()
        # 确保目录存在
        downloads_path.mkdir(parents=True, exist_ok=True)
        self.config.set(self.section_user, "downloads_path", str(downloads_path))

    def initialize_downloads(self):
        """初始化下载目录"""
        # 确保下载目录存在
        downloads_dir = self.get_downloads_dir()
        downloads_dir.mkdir(parents=True, exist_ok=True)
        print(f"下载目录已初始化: {downloads_dir.absolute()}")