import configparser
import os
from pathlib import Path

class JavaConfigManager:
    def __init__(self):
        # 获取用户主目录
        home = Path.home()
        # 配置目录和文件路径
        config_dir = home / '.we'
        config_dir.mkdir(parents=True, exist_ok=True)  # 确保目录存在

        self.filepath = config_dir / 'we_java.ini'
        self.config = configparser.ConfigParser()
        if self.filepath.exists():
            self.config.read(self.filepath, encoding='utf-8')
        else:
            # 创建空文件
            self.filepath.touch()
        # 确保[java]节存在
        if not self.config.has_section('java'):
            self.config.add_section('java')
            self._save()

    def add_java_path(self, version: str, path: str):
        key = f'java_{version}_path'
        self.config.set('java', key, path)
        self._save()

    def get_java_path(self):
        if not self.config.has_section('java'):
            return {}
        all_items = dict(self.config.items('java'))
        return {k: v for k, v in all_items.items() if k.startswith('java_') and k.endswith('_path')}

    def _save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            self.config.write(f)
