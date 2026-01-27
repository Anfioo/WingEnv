from pathlib import Path
from typing import Optional, Dict

from conf.STYLE_CONFIG import STYLE_CONFIG
from wing_utils import IniConfigUtils
from wing_utils.common.gzip_utils import GzipUtils


class ThemeManager:
    def __init__(self):
        self.config = IniConfigUtils()
        self.section_user = "user"
        self.section_theme = "theme"

    def add_theme(self, name: str, css_path: str):
        """添加新的主题映射"""
        path = Path(css_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"样式文件不存在: {path}")
        self.config.set(self.section_theme, name, str(path))

    def remove_theme(self, name: str):
        """删除主题映射（不删除 CSS 文件）"""
        self.config.delete(self.section_theme, name)
        current = self.get_current_theme()
        if current == name:
            self.set_current_theme("default")

    def list_themes(self) -> Dict[str, str]:
        """列出所有主题及其对应 CSS 路径"""
        return self.config.get_section(self.section_theme)

    def set_current_theme(self, name: str):
        """设置当前使用的主题"""
        if not self.config.has(self.section_theme, name):
            raise ValueError(f"不存在主题: {name}")
        self.config.set(self.section_user, "style", name)

    def get_current_theme(self) -> str:
        """获取当前主题名"""
        return self.config.get(self.section_user, "style", fallback="default")

    def get_current_theme_path(self) -> Optional[str]:
        """获取当前主题对应的 CSS 文件路径"""
        theme = self.get_current_theme()
        return self.config.get(self.section_theme, theme)

    def theme_exists(self, name: str) -> bool:
        """是否存在指定主题"""
        return self.config.has(self.section_theme, name)

    def initialize_theme(self):
        # 获取配置路径（Path对象）
        path = self.config.getConfigWorkingPath()

        # 1. 定义目标目录：path/data/style，自动创建不存在的目录
        target_dir = path / "data" / "style"
        target_dir.mkdir(parents=True, exist_ok=True)  # 递归创建目录，已存在不报错

        # 2. 遍历每个样式配置项
        for style in STYLE_CONFIG:
            try:
                # 获取文件名和解压后的字符串内容
                file_name = style["name"]
                decompress_content = GzipUtils.decompress(style["data"])  # 直接得到str

                print(f"正在处理样式文件: {file_name}")

                # 3. 拼接目标文件路径（自动处理子目录）
                target_file_path = target_dir / file_name
                # 确保文件所在的子目录存在（比如name是"subdir/blue.css"时创建subdir）
                target_file_path.parent.mkdir(parents=True, exist_ok=True)

                # 4. 直接写入解压后的字符串内容（UTF-8编码）
                with open(target_file_path, 'w', encoding='utf-8') as f:
                    f.write(decompress_content)
                self.add_theme(file_name.split(".")[0],str(target_file_path.absolute()))

                print(f"成功保存: {target_file_path.absolute()}")

            except Exception as e:
                # 捕获单个文件异常，不中断整体流程
                print(f"处理样式 {style.get('name', '未知文件')} 失败: {str(e)}")
                continue

        print(f"\n所有样式文件已保存到: {target_dir.absolute()}")
