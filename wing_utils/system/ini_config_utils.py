import configparser
from pathlib import Path
from typing import Optional, Dict


class IniConfigUtils:
    """
    INI 配置文件工具类

    加载优先级：
    1. 当前目录 ./\.we/
    2. 用户目录 ~/.we/
    """

    DIR_NAME = ".we"
    DEFAULT_FILE_NAME = "we_config.ini"

    def __init__(self, filename: Optional[str] = None):
        self.base_dir = self._resolve_base_dir()
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.filepath = (
            Path(filename)
            if filename
            else self.base_dir / self.DEFAULT_FILE_NAME
        )

        self.config = configparser.ConfigParser()
        self._load()

    # =========================
    # 路径解析
    # =========================

    def _resolve_base_dir(self) -> Path:
        """
        决定配置目录：
        - 如果当前目录存在 .we，则使用当前目录
        - 否则使用 ~/.we
        """
        cwd_dir = Path.cwd() / self.DIR_NAME
        if cwd_dir.exists() and cwd_dir.is_dir():
            return cwd_dir

        return Path.home() / self.DIR_NAME

    # =========================
    # 内部方法
    # =========================

    def _load(self):
        """加载配置文件"""
        if self.filepath.exists():
            self.config.read(self.filepath, encoding="utf-8")

    def _write(self):
        """写入配置文件"""
        with self.filepath.open("w", encoding="utf-8") as f:
            self.config.write(f)

    def _ensure_section(self, section: str):
        if not self.config.has_section(section):
            self.config.add_section(section)

    # =========================
    # 查询操作
    # =========================

    def get(self, section: str, key: str, fallback: Optional[str] = None) -> Optional[str]:
        return self.config.get(section, key, fallback=fallback)

    def get_section(self, section: str) -> Dict[str, str]:
        if self.config.has_section(section):
            return dict(self.config.items(section))
        return {}

    def has(self, section: str, key: str) -> bool:
        return self.config.has_option(section, key)

    # =========================
    # 写操作
    # =========================

    def set(self, section: str, key: str, value: str):
        self._ensure_section(section)
        self.config.set(section, key, value)
        self._write()

    # =========================
    # 删除操作
    # =========================

    def delete(self, section: str, key: str):
        if self.config.has_section(section) and self.config.has_option(section, key):
            self.config.remove_option(section, key)
            self._write()

    def delete_section(self, section: str):
        if self.config.has_section(section):
            self.config.remove_section(section)
            self._write()

    # =========================
    # 全量导出
    # =========================

    def dump(self) -> Dict[str, Dict[str, str]]:
        return {
            section: dict(self.config.items(section))
            for section in self.config.sections()
        }
