from pathlib import Path
from typing import Optional, Dict

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
            self.set_current_version("8")

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


# jm = JavaManager()
#
# # 添加 JDK 路径
# jm.add_java_version("17", "C:\Apps\Envs\JDK\jdk-13.0.2")
#
# # 设置当前 JDK
# jm.set_current_version("17")
#
# # 获取当前使用的 JDK 路径
# print(jm.get_current_java_path())
#
# # 列出所有 JDK
# print(jm.list_java_versions())
