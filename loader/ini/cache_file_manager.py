import json
from pathlib import Path
from typing import Optional, Dict, Any

from wing_utils import IniConfigUtils


class CacheFileManager:
    def __init__(self):
        self.config = IniConfigUtils()
        self.section_user = "user"
        self._cache_dir = None
        self._cache_dir_key = "cache_dir"


    def get_cache_dir(self) -> Path:
        """获取缓存目录路径"""
        if self._cache_dir:
            return self._cache_dir
        
        # 首先尝试从配置文件中读取缓存目录
        cache_path_str = self.config.get(self.section_user, self._cache_dir_key)
        if cache_path_str:
            cache_path = Path(cache_path_str).expanduser().resolve()
            self._cache_dir = cache_path
            return cache_path
        
        # 如果没有配置，使用默认路径
        config_path = self.config.getConfigWorkingPath()
        default_path = config_path / "data" / "cache"
        self._cache_dir = default_path
        return default_path

    def set_cache_dir(self, path: str):
        """设置缓存目录路径"""
        cache_path = Path(path).expanduser().resolve()
        cache_path.mkdir(parents=True, exist_ok=True)

        # 保存到配置文件
        self.config.set(self.section_user, self._cache_dir_key, str(cache_path))
        
        self._cache_dir = cache_path

    def get_cache(self, file_name: str) -> str:
        """读取缓存文件内容"""
        cache_file = self.get_cache_dir() / file_name
        if not cache_file.exists():
            raise FileNotFoundError(f"缓存文件不存在: {cache_file}")
        with open(cache_file, 'r', encoding='utf-8') as f:
            return f.read()

    def set_cache(self, file_name: str, content: str):
        """保存内容到缓存文件"""
        cache_dir = self.get_cache_dir()
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / file_name
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def cache_exists(self, file_name: str) -> bool:
        """检查缓存文件是否存在"""
        cache_file = self.get_cache_dir() / file_name
        return cache_file.exists()

    def delete_cache(self, file_name: str):
        """删除缓存文件"""
        cache_file = self.get_cache_dir() / file_name
        if cache_file.exists():
            cache_file.unlink()

    def initialize_cache(self):
        """初始化缓存目录"""
        cache_dir = self.get_cache_dir()
        cache_dir.mkdir(parents=True, exist_ok=True)
        print(f"缓存目录已初始化: {cache_dir.absolute()}")

    def get_cache_to_json(self, file_name: str) -> Dict[str, Any]:
        """
        读取缓存文件内容并转换为JSON字典

        Args:
            file_name: 缓存文件名

        Returns:
            解析后的JSON字典

        Raises:
            FileNotFoundError: 缓存文件不存在
            json.JSONDecodeError: 文件内容不是有效的JSON格式
        """
        # 先读取文件内容
        content = self.get_cache(file_name)

        # 尝试解析JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"缓存文件 {file_name} 内容不是有效的JSON格式: {str(e)}",
                doc=e.doc,
                pos=e.pos
            )

    # 可选扩展：新增 fromjson 方法，用于将字典保存为JSON格式的缓存文件
    def set_cache_from_json(self, file_name: str, data: Dict[str, Any], indent: int = 4):
        """
        将字典数据以JSON格式保存到缓存文件

        Args:
            file_name: 缓存文件名
            data: 要保存的字典数据
            indent: JSON格式化缩进，默认4个空格
        """
        # 将字典转换为格式化的JSON字符串
        json_content = json.dumps(data, ensure_ascii=False, indent=indent)
        # 调用已有的setCache方法保存
        self.set_cache(file_name, json_content)

