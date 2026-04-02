from pathlib import Path
from typing import Optional, Dict

from conf.STYLE_CONFIG import STYLE_CONFIG
from loader import EnvsSymlinkManager
from loader.envs_enum import EnvsEnum
from wing_utils import IniConfigUtils
from wing_utils.common.gzip_utils import GzipUtils


class BaseInstallIniManager:
    def __init__(self, key: EnvsEnum):
        self.config = IniConfigUtils()
        self.envs_symlink_manager = EnvsSymlinkManager()
        self.key = key

    def add(self, key: str, value: str):
        """添加新的子配置映射"""
        path = Path(value).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        self.config.set(self.key.value, key, str(path))

    def remove(self, name: str):
        """删除子配置映射"""
        self.config.delete(self.key.value, name)

    def list(self) -> Dict[str, str]:
        """列出所有子配置项目及其对应 CSS 路径"""
        return self.config.get_section(self.key.value)

    def set_current_env(self, name: str) -> bool:
        """设置当前使用的项目，和创建对于的软连接"""
        # 先移除原有的
        return self.envs_symlink_manager.add_symlink(self.key, name, "dir", "replace")

    def get_current_env(self) -> str:
        """获取当前项目软连接环境名称，真实的配置部分"""
        return self.envs_symlink_manager.get_symlink(self.key)

    def get_current_env_path(self) -> Path:
        """获取当前软连接路径"""
        return self.envs_symlink_manager.get_symlink_path(self.key)

    def get_current_env_path_exists(self) -> bool:
        """获取当前软连接是否存在"""
        return self.envs_symlink_manager.symlink_exists(self.key)
