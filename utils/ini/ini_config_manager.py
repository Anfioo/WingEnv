import configparser
from pathlib import Path
from typing import Optional, Dict


class IniConfigManager:
    def __init__(self, filename: Optional[str] = None):
        self.config_dir = Path.home() / '.we'
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.filepath = Path(filename) if filename else (self.config_dir / 'we_config.ini')
        self.config = configparser.ConfigParser()

        if self.filepath.exists():
            self.config.read(self.filepath, encoding='utf-8')
        else:
            self.filepath.touch()
            self.save()

    def save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            self.config.write(f)

    # ----------- 查询操作 -----------

    def get_value(self, section: str, key: str, fallback: Optional[str] = None) -> Optional[str]:
        return self.config.get(section, key, fallback=fallback)

    def get_section_items(self, section: str) -> Dict[str, str]:
        if self.config.has_section(section):
            return dict(self.config.items(section))
        return {}

    def has_option(self, section: str, key: str) -> bool:
        return self.config.has_option(section, key)

    # ----------- 添加 / 修改 -----------

    def set_value(self, section: str, key: str, value: str):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        self.save()

    # ----------- 删除 -----------

    def remove_option(self, section: str, key: str):
        if self.config.has_section(section) and self.config.has_option(section, key):
            self.config.remove_option(section, key)
            self.save()

    def remove_section(self, section: str):
        if self.config.has_section(section):
            self.config.remove_section(section)
            self.save()

    # ----------- 全部配置 -----------

    def list_all(self) -> Dict[str, Dict[str, str]]:
        return {section: dict(self.config.items(section)) for section in self.config.sections()}
