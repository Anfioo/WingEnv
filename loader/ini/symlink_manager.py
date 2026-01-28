import os
from pathlib import Path
from typing import Dict, Optional, Literal
from wing_utils import IniConfigUtils
from wing_utils.system.sys_env_link_utils import create_dir_symlink, create_file_symlink, OnExistsPolicy


class SymlinkManager:
    def __init__(self):
        self.config = IniConfigUtils()
        self.section_symlink = "symlink"
        self.envs_dir = self.config.getConfigWorkingPath() / "envs"
        # 确保envs目录存在
        self.envs_dir.mkdir(parents=True, exist_ok=True)

    def add_symlink(self, name: str, path: str, link_type: Literal["dir", "file"] = "dir",
                    on_exists: OnExistsPolicy = "replace") -> bool:
        """添加新的软链接映射
        
        Args:
            name: 软链接名称
            path: 目标路径
            link_type: 链接类型，"dir"表示目录，"file"表示文件
            on_exists: 当链接已存在时的策略
            
        Returns:
            bool: 是否创建成功
        """
        # 检查目标路径是否存在
        if not os.path.exists(path):
            return False

        # 生成软链接名称
        link_name = f"{name}_env"
        # 生成软链接路径
        link_path = str(self.envs_dir / link_name)

        # 根据类型创建软链接
        if link_type == "dir":
            if not os.path.isdir(path):
                return False
            success = create_dir_symlink(path, link_path, on_exists)
        else:
            if not os.path.isfile(path):
                return False
            success = create_file_symlink(path, link_path, on_exists)

        # 如果创建成功，更新配置
        if success:
            self.config.set(self.section_symlink, link_name, path)

        return success

    def remove_symlink(self, name: str) -> bool:
        """删除软链接映射（不删除目标文件/目录）
        
        Args:
            name: 软链接名称
            
        Returns:
            bool: 是否删除成功
        """
        # 生成软链接名称
        link_name = f"{name}_env"
        # 生成软链接路径
        link_path = str(self.envs_dir / link_name)

        # 删除软链接
        try:
            if os.path.islink(link_path):
                os.unlink(link_path)
            elif os.path.exists(link_path):
                if os.path.isdir(link_path):
                    os.rmdir(link_path)
                else:
                    os.remove(link_path)
        except OSError:
            pass

        # 从配置中删除
        self.config.delete(self.section_symlink, link_name)
        return True

    def list_symlinks(self) -> Dict[str, str]:
        """列出所有软链接及其对应目标路径"""
        return self.config.get_section(self.section_symlink)

    def get_symlink(self, name: str) -> Optional[str]:
        """获取指定软链接的目标路径"""
        link_name = f"{name}_env"
        return self.config.get(self.section_symlink, link_name)

    def symlink_exists(self, name: str) -> bool:
        """是否存在指定软链接"""
        link_name = f"{name}_env"
        return self.config.has(self.section_symlink, link_name)

    def initialize_symlink(self):
        """初始化软链接目录"""
        # 确保envs目录存在
        self.envs_dir.mkdir(parents=True, exist_ok=True)
        print(f"软链接目录已初始化: {self.envs_dir.absolute()}")
