import configparser
from pathlib import Path
from typing import Optional, Dict


class IniConfigUtils:
    """
    INI 配置文件工具类（带 mtime 智能缓存）

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
        self._last_mtime: Optional[float] = None

        self._load()

    def getConfigPath(self) -> Path:
        return self.filepath

    def getConfigWorkingPath(self) -> Path:
        return self.filepath.parent

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
        """强制加载配置文件"""
        self.config.clear()

        if self.filepath.exists():
            self.config.read(self.filepath, encoding="utf-8")
            self._last_mtime = self.filepath.stat().st_mtime
        else:
            self._last_mtime = None

    def _load_if_changed(self):
        """仅当文件发生变化时重新加载"""
        if not self.filepath.exists():
            return

        mtime = self.filepath.stat().st_mtime
        if self._last_mtime != mtime:
            self._load()

    def _write(self):
        """写入配置文件（并同步 mtime）"""
        with self.filepath.open("w", encoding="utf-8") as f:
            self.config.write(f)

        self._last_mtime = self.filepath.stat().st_mtime

    def _ensure_section(self, section: str):
        if not self.config.has_section(section):
            self.config.add_section(section)

    # =========================
    # 查询操作（自动热更新）
    # =========================

    def get(self, section: str, key: str, fallback: Optional[str] = None) -> Optional[str]:
        self._load_if_changed()
        return self.config.get(section, key, fallback=fallback)

    def get_section(self, section: str) -> Dict[str, str]:
        self._load_if_changed()
        if self.config.has_section(section):
            return dict(self.config.items(section))
        return {}

    def has(self, section: str, key: str) -> bool:
        self._load_if_changed()
        return self.config.has_option(section, key)

    # =========================
    # 写操作
    # =========================

    def set(self, section: str, key: str, value: str):
        self._load_if_changed()
        self._ensure_section(section)
        self.config.set(section, key, value)
        self._write()

    # =========================
    # 删除操作
    # =========================

    def delete(self, section: str, key: str):
        self._load_if_changed()
        if self.config.has_section(section) and self.config.has_option(section, key):
            self.config.remove_option(section, key)
            self._write()

    def delete_section(self, section: str):
        self._load_if_changed()
        if self.config.has_section(section):
            self.config.remove_section(section)
            self._write()

    # =========================
    # 全量导出
    # =========================

    def dump(self) -> Dict[str, Dict[str, str]]:
        self._load_if_changed()
        return {
            section: dict(self.config.items(section))
            for section in self.config.sections()
        }
