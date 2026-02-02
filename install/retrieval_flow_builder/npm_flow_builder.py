from typing import Any, Callable, Optional, Dict, Self
import requests

from install.retrieval_flow_builder import BaseRetrievalFlowBuilder

# 镜像源字典
MIRRORS = {
    "阿里镜像 (npmmirror)": "https://npmmirror.com/mirrors/node",
    "清华大学镜像 (TUNA)": "https://mirrors.tuna.tsinghua.edu.cn/nodejs-release",
    "Node.js 官方": "https://nodejs.org/dist"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Connection": "keep-alive"
}

class NPMRetrievalFlowBuilder(BaseRetrievalFlowBuilder):
    @classmethod
    def default(cls, selector: Callable = None) -> Self:
        """
        创建 NPM 构建流程实例
        :param selector: UI 选择器
        :return: NPMFlowBuilder 实例
        """
        return cls(selector=selector)

    def mirror(self) -> Self:
        """
        准备待选的镜像源列表
        :return: Self
        """
        if self._is_interrupted: return self
        self._current_options = list(MIRRORS.keys())
        self._last_prompt = "选择 Node.js 下载源"
        return self

    def fetch_data(self) -> Self:
        """
        手动触发网络请求，获取 Node.js 版本数据
        :return: Self
        """
        if self._is_interrupted: return self
        mirror_name = self._selected_value
        self._metadata["mirror"] = mirror_name
        base_url = MIRRORS[mirror_name]
        self._metadata["base_url"] = base_url

        try:
            index_url = f"{base_url}/index.json"
            r = requests.get(index_url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            self._raw_data = r.json()
        except Exception:
            self._is_interrupted = True
        return self

    def version(self) -> Self:
        """
        准备待选的 Node.js 版本列表
        :return: Self
        """
        if self._is_interrupted or not self._raw_data: return self
        
        # 构造显示文本和元数据的映射
        self._version_map = {}
        options = []
        for opt in self._raw_data[:30]: # 取最近30个版本
            version = opt['version']
            lts_info = f" [LTS: {opt['lts']}]" if opt['lts'] else ""
            display = f"{version}{lts_info}"
            options.append(display)
            self._version_map[display] = opt
            
        self._current_options = options
        self._last_prompt = "选择 Node.js 版本"
        return self

    def arch(self) -> Self:
        """
        准备待选的平台架构列表
        :return: Self
        """
        if self._is_interrupted or not hasattr(self, "_version_map"): return self
        
        selected_display = self._selected_value
        version_info = self._version_map.get(selected_display)
        if not version_info:
            self._is_interrupted = True
            return self
        
        self._metadata["version"] = version_info['version']
        self._metadata["npm"] = version_info.get('npm')
        self._metadata["lts"] = version_info.get('lts')

        # 过滤出可用的文件类型
        available_files = [f for f in version_info['files'] if f not in ['headers', 'src']]
        self._current_options = available_files
        self._last_prompt = f"选择 {version_info['version']} 的平台架构"
        return self

    def data(self) -> Optional[Dict[str, Any]]:
        """
        收集并返回最终的 NPM 元数据
        :return: 元数据字典
        """
        if self._is_interrupted or not self._selected_value: return None
        
        target_arch = self._selected_value
        base_url = self._metadata["base_url"]
        version = self._metadata["version"]
        
        # 解析下载地址
        filename, url = self._parse_download_url(base_url, version, target_arch)
        
        self._metadata.update({
            "arch": target_arch,
            "filename": filename,
            "url": url
        })
        return self._metadata

    def _parse_download_url(self, base_url: str, version: str, file_type: str) -> tuple[str, str]:
        """
        解析 Node.js 下载链接
        :param base_url: 镜像基础地址
        :param version: 版本号
        :param file_type: 文件类型/架构
        :return: (文件名, 下载链接)
        """
        ext = "tar.gz"
        platform_suffix = file_type

        if file_type.startswith("win-"):
            if "zip" in file_type:
                ext = "zip"
                platform_suffix = file_type.replace("-zip", "")
            elif "7z" in file_type:
                ext = "7z"
                platform_suffix = file_type.replace("-7z", "")
            elif "msi" in file_type:
                ext = "msi"
                platform_suffix = file_type.replace("-msi", "")
            elif "exe" in file_type:
                ext = "exe"
                platform_suffix = file_type.replace("-exe", "")
        elif file_type.startswith("osx-"):
            if "tar" in file_type:
                ext = "tar.gz"
                platform_suffix = file_type.replace("-tar", "")
            elif "pkg" in file_type:
                ext = "pkg"
                platform_suffix = file_type.replace("-pkg", "")

        filename = f"node-{version}-{platform_suffix}.{ext}"
        url = f"{base_url}/{version}/{filename}"
        return filename, url

