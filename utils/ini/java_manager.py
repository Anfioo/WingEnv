from pathlib import Path
from typing import Optional, Dict

from prompt_toolkit import HTML

from utils.ini.ini_config_manager import IniConfigManager


class JavaManager:
    def __init__(self):
        self.config = IniConfigManager()
        self.section_user = "user"
        self.section_java = "java"

    def add_java_version(self, version: str, path: str):
        """添加新的 JDK 版本及其路径"""
        resolved_path = Path(path).expanduser().resolve()
        if not resolved_path.exists():
            raise FileNotFoundError(f"JDK 路径不存在: {resolved_path}")
        self.config.set_value(self.section_java, version, str(resolved_path))

    def remove_java_version(self, version: str):
        """移除某个 JDK 版本（不删除 JDK 本地文件）"""
        self.config.remove_option(self.section_java, version)

        current = self.get_current_version()
        if current == version:
            # 当前使用的版本被删除了，尝试设置其他可用版本
            versions = self.list_java_versions()
            fallback_version = next(iter(versions), None)
            if fallback_version:
                self.set_current_version(fallback_version)
                print(f"⚠️ 当前版本 <b>{version}</b> 被删除，自动切换为 <b>{fallback_version}")
            else:
                # 没有其他版本了，清除配置并提示
                self.config.remove_option(self.section_user, "java_version")
                print("⚠️ 当前版本 <b>{version}</b> 被删除，且没有其他可用 JDK，已清除当前设置。")

    def list_java_versions(self) -> Dict[str, str]:
        """列出所有已配置的 JDK 版本及其路径"""
        return self.config.get_section_items(self.section_java)

    def set_current_version(self, version: str):
        """设置当前使用的 JDK 版本"""
        if not self.config.has_option(self.section_java, version):
            raise ValueError(f"不存在的 JDK 版本: {version}")
        self.config.set_value(self.section_user, "java_version", version)

    def get_current_version(self) -> str:
        """获取当前配置的 JDK 版本"""
        return self.config.get_value(self.section_user, "java_version", fallback="8")

    def get_current_java_path(self) -> Optional[str]:
        """获取当前使用 JDK 版本的路径"""
        version = self.get_current_version()
        return self.config.get_value(self.section_java, version)

    def java_version_exists(self, version: str) -> bool:
        """检查某个 JDK 版本是否已配置"""
        return self.config.has_option(self.section_java, version)

    def get_java_path(self, version: str) -> Optional[str]:
        """获取指定 JDK 版本的路径"""
        return self.config.get_value(self.section_java, version)
