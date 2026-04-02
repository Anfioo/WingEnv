#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------Project Information------------------
@Project : WingShake->WingEnv
@File : env_manager.py
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


class ExtractManager:
    def __init__(self):
        self.config = IniConfigUtils()
        self.section_user = "user"
        self.section_extract_key = "extract_path"

    def get_current_extract_dir(self) -> Path:
        """获取下载目录路径"""
        # 首先尝试从配置中获取
        downloads_path = self.config.get(self.section_user, self.section_extract_key)
        if downloads_path:
            return Path(downloads_path).expanduser().resolve()
        # 默认下载目录：配置路径下的downloads
        config_path = self.config.getConfigWorkingPath()
        return config_path / "data" / "extract"

    def set_extract_dir(self, path: str):
        """设置下载目录路径"""
        downloads_path = Path(path).expanduser().resolve()
        # 确保目录存在
        downloads_path.mkdir(parents=True, exist_ok=True)
        self.config.set(self.section_user, self.section_extract_key, str(downloads_path))

    def initialize_extract(self):
        """初始化下载目录"""
        # 确保下载目录存在
        downloads_dir = self.get_current_extract_dir()
        downloads_dir.mkdir(parents=True, exist_ok=True)
        print(f"解压目录已初始化: {downloads_dir.absolute()}")
