from typing import Any, Callable, Optional, Dict, Self
import requests

from install.retrieval_flow_builder import BaseRetrievalFlowBuilder

# Go 官方 JSON 接口
GO_API_URL = "https://go.dev/dl/?mode=json&include=all"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


class GoRetrievalFlowBuilder(BaseRetrievalFlowBuilder):
    @classmethod
    def default(cls, selector: Callable = None) -> Self:
        """
        创建 Go 构建流程实例
        :param selector: UI 选择器
        :return: GoFlowBuilder 实例
        """
        return cls(selector=selector)

    def fetch_data(self) -> Self:
        """
        手动触发网络请求，获取 Go 版本数据
        :return: Self
        """
        if self._is_interrupted: return self
        try:
            r = requests.get(GO_API_URL, headers=HEADERS, timeout=10)
            r.raise_for_status()
            self._raw_data = r.json()
        except Exception as e:
            print(f"❌ 获取 Go 数据失败: {e}")
            self._is_interrupted = True
        return self

    def version(self) -> Self:
        """
        准备待选的 Go 版本列表
        :return: Self
        """
        if self._is_interrupted or not self._raw_data: return self
        
        # 提取版本列表 (只展示稳定版)
        stable_versions = [v['version'] for v in self._raw_data if v.get('stable')]
        self._current_options = stable_versions[:20] # 取前20个版本
        self._last_prompt = "选择 Go 语言版本"
        return self

    def os(self) -> Self:
        """
        准备待选的操作系统列表
        :return: Self
        """
        if self._is_interrupted or not self._raw_data: return self
        
        target_version_str = self._selected_value
        self._metadata["version"] = target_version_str
        
        # 找到选定版本的详细数据
        version_data = next(item for item in self._raw_data if item['version'] == target_version_str)
        self._version_data = version_data # 暂存以便下一步使用
        
        os_list = sorted(list(set(f['os'] for f in version_data['files'] if f['os'])))
        self._current_options = os_list
        self._last_prompt = "选择操作系统 (OS)"
        return self

    def arch(self) -> Self:
        """
        准备待选的处理器架构列表
        :return: Self
        """
        if self._is_interrupted or not hasattr(self, "_version_data"): return self
        
        target_os = self._selected_value
        self._metadata["os"] = target_os
        
        arch_list = sorted(list(set(f['arch'] for f in self._version_data['files'] if f['os'] == target_os and f['arch'])))
        self._current_options = arch_list
        self._last_prompt = "选择处理器架构 (Arch)"
        return self

    def kind(self) -> Self:
        """
        准备待选的安装包格式列表
        :return: Self
        """
        if self._is_interrupted or not hasattr(self, "_version_data"): return self
        
        target_arch = self._selected_value
        self._metadata["arch"] = target_arch
        
        target_os = self._metadata["os"]
        files = [f for f in self._version_data['files'] if f['os'] == target_os and f['arch'] == target_arch]
        self._files = files # 暂存
        
        file_options = [f"{f['kind']} ({f['filename'].split('.')[-1]})" for f in files]
        self._current_options = file_options
        self._last_prompt = "选择安装包格式"
        return self

    def data(self) -> Optional[Dict[str, Any]]:
        """
        收集并返回最终的 Go 元数据
        :return: 元数据字典
        """
        if self._is_interrupted or not hasattr(self, "_files"): return None
        
        selected_option = self._selected_value
        file_options = [f"{f['kind']} ({f['filename'].split('.')[-1]})" for f in self._files]
        
        try:
            target_file = self._files[file_options.index(selected_option)]
            download_url = f"https://go.dev/dl/{target_file['filename']}"
            
            return {
                "product": "Go Language",
                "version": self._metadata["version"],
                "os": self._metadata["os"],
                "arch": self._metadata["arch"],
                "filename": target_file['filename'],
                "sha256": target_file['sha256'],
                "url": download_url
            }
        except (ValueError, IndexError):
            return None

