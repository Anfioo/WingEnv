from pathlib import Path
from typing import Optional, Dict

from utils.ini.ini_config_manager import IniConfigManager


class MavenManager:
    def __init__(self):
        self.config = IniConfigManager()
        self.section_user = "user"
        self.section_maven = "maven"

    def add_maven_version(self, version: str, path: str):
        """添加新的 Maven 版本及其路径"""
        resolved_path = Path(path).expanduser().resolve()
        if not resolved_path.exists():
            raise FileNotFoundError(f"Maven 路径不存在: {resolved_path}")
        self.config.set_value(self.section_maven, version, str(resolved_path))

    def remove_maven_version(self, version: str):
        """移除某个 Maven 版本（不删除本地文件）"""
        self.config.remove_option(self.section_maven, version)

        current = self.get_current_version()
        if current == version:
            versions = self.list_maven_versions()
            fallback_version = next(iter(versions), None)
            if fallback_version:
                self.set_current_version(fallback_version)
                print(f"⚠️ 当前 Maven 版本 <b>{version}</b> 被删除，自动切换为 <b>{fallback_version}</b>")
            else:
                self.config.remove_option(self.section_user, "maven_version")
                print(f"⚠️ 当前 Maven 版本 <b>{version}</b> 被删除，且无其他版本可用，已清除设置。")

    def list_maven_versions(self) -> Dict[str, str]:
        """列出所有已配置的 Maven 版本及其路径"""
        return self.config.get_section_items(self.section_maven)

    def set_current_version(self, version: str):
        """设置当前使用的 Maven 版本"""
        if not self.config.has_option(self.section_maven, version):
            raise ValueError(f"不存在的 Maven 版本: {version}")
        self.config.set_value(self.section_user, "maven_version", version)

    def get_current_version(self) -> str:
        """获取当前配置的 Maven 版本"""
        return self.config.get_value(self.section_user, "maven_version", fallback="3.9.10")

    def get_current_maven_path(self) -> Optional[str]:
        """获取当前使用 Maven 版本的路径"""
        version = self.get_current_version()
        return self.config.get_value(self.section_maven, version)

    def maven_version_exists(self, version: str) -> bool:
        """检查某个 Maven 版本是否已配置"""
        return self.config.has_option(self.section_maven, version)

    def get_maven_path(self, version: str) -> Optional[str]:
        """获取指定 Maven 版本的路径"""
        return self.config.get_value(self.section_maven, version)
