import os
from typing import Optional

from rich.panel import Panel

from wing_utils.extract.python_single_file_utils import PythonSingleFileUtils
from wing_utils.extract.python_tar_utils import PythonTarUtils
from wing_utils.extract.python_zip_utils import PythonZipUtils
from wing_utils.extract.seven_zip_utils import SevenZipUtils

from wing_utils.ui import console


class UniversalExtractor:
    PYTHON_SUPPORTED = ('.zip', '.tar', '.tgz', '.tar.gz', '.tar.bz2', '.tar.xz', '.gz', '.bz2', '.xz')
    EXTERNAL_TOOLS = ('.7z', '.rar')

    @staticmethod
    def extract(file_path: str, dest_dir: Optional[str] = None) -> Optional[str]:
        """万能解压入口"""
        if not os.path.exists(file_path):
            print(f"❌ 错误: 文件不存在 -> {file_path}")
            return None

        # 1. 自动计算目标目录 (防止解压后文件散落)
        if dest_dir is None:
            # 去掉后缀作为文件夹名 e.g., "data.7z" -> "data"
            dest_dir = os.path.abspath(os.path.splitext(file_path)[0])

        os.makedirs(dest_dir, exist_ok=True)
        ext = os.path.splitext(file_path)[1].lower()

        # 2. 核心逻辑策略
        # 策略 A: 只要有 7z，优先用 7z 处理一切（支持密码，支持 rar/7z/zip 等）
        console.print(
            Panel(
                "尝试使用系统7z：",
                title="提示",
                border_style="cyan",
            )
        )
        if SevenZipUtils.is_installed():
            success = SevenZipUtils.extract_with_rich(file_path, dest_dir)
            if success:
                return dest_dir
        console.print(
            Panel(
                "可以尝试安装7z以获得更好的体验 https://www.7-zip.org/",
                title="建议",
                border_style="cyan",
            )
        )

        console.print(
            Panel(
                "尝试使用自带解压器：",
                title="提示",
                border_style="cyan",
            )
        )

        # 策略 B: 7z 不可用或 7z 失败，尝试 Python 工具类 (根据文件类型选择对应工具)
        if ext in UniversalExtractor.PYTHON_SUPPORTED:
            try:
                if ext == '.zip':
                    if PythonZipUtils.extract_with_rich(file_path, dest_dir):
                        return dest_dir
                elif ext in ('.tar', '.tgz', '.tar.gz', '.tar.bz2', '.tar.xz'):
                    if PythonTarUtils.extract_with_rich(file_path, dest_dir):
                        return dest_dir
                elif ext in ('.gz', '.bz2', '.xz'):
                    if PythonSingleFileUtils.extract_with_rich(file_path, dest_dir):
                        return dest_dir
            except Exception as e:
                print(f"❌ Python 工具解压失败: {e}")

        print(f"⚠️ 无法处理该格式: {ext} (建议安装 7-Zip)")
        return None

    @staticmethod
    def extract_dir(directory: str) -> None:
        """递归解压目录下所有压缩包"""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(UniversalExtractor.PYTHON_SUPPORTED + UniversalExtractor.EXTERNAL_TOOLS):
                    UniversalExtractor.extract(os.path.join(root, file))


if __name__ == "__main__":
    # 调用示例
    # 它会先检查 7z，如果有 7z 就用 7z 解压 rar/7z/zip
    # 如果解压失败会问你要密码
    # 默认解压到同名的文件夹下
    UniversalExtractor.extract("nacos_config_export_20251223162803.zip", "./aa")
