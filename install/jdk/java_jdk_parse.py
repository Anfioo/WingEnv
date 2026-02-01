from typing import Any, Callable, Optional, Dict, Self
import requests
from install.builder.builder_base import BaseFlowBuilder

JDK_FEED_URL = "https://download.jetbrains.com/jdk/feed/v1/jdks.json"

class JDKFlowBuilder(BaseFlowBuilder):
    @classmethod
    def default(cls, os: str = "windows", arch: str = "x86_64", selector: Callable = None) -> Self:
        """
        创建 JDK 构建流程实例
        :param os: 操作系统 (windows, linux, macos)
        :param arch: 架构 (x86_64, aarch64)
        :param selector: UI 选择器
        :return: JDKFlowBuilder 实例
        """
        instance = cls(selector=selector)
        instance._metadata["os"] = os
        instance._metadata["arch"] = arch
        return instance

    def fetch_data(self) -> Self:
        """
        异步/手动触发网络请求，获取 JDK 数据
        :return: Self
        """
        if self._is_interrupted: return self
        try:
            r = requests.get(JDK_FEED_URL, timeout=10)
            r.raise_for_status()
            self._raw_data = r.json().get("jdks", [])
        except Exception:
            self._is_interrupted = True
        return self

    def message_ui(self, title: str = "JDK 选择器", text: str = "开始配置您的 JDK") -> Self:
        """
        显示初始欢迎信息 (可选)
        :param title: 标题
        :param text: 内容
        :return: Self
        """
        # 可以在这里弹出一个初始消息
        return self

    def vendor(self) -> Self:
        """
        准备待选的 JDK 厂商列表
        :return: Self
        """
        if self._is_interrupted or not self._raw_data: return self
        
        # 过滤当前 OS/Arch 下可选的厂商
        os = self._metadata.get("os")
        arch = self._metadata.get("arch")
        
        vendors = set()
        for jdk in self._raw_data:
            for pkg in jdk.get("packages", []):
                if pkg["os"] == os and pkg["arch"] == arch:
                    vendors.add(jdk["vendor"])
        
        self._current_options = sorted(list(vendors))
        self._last_prompt = "选择 JDK 厂商"
        return self

    def version(self) -> Self:
        """
        准备待选的 JDK 版本列表
        :return: Self
        """
        if self._is_interrupted or not self._raw_data: return self
        
        # 过滤当前厂商下的版本
        vendor = self._selected_value
        self._metadata["vendor"] = vendor
        
        os = self._metadata.get("os")
        arch = self._metadata.get("arch")
        
        versions = set()
        for jdk in self._raw_data:
            if jdk["vendor"] == vendor:
                for pkg in jdk.get("packages", []):
                    if pkg["os"] == os and pkg["arch"] == arch:
                        versions.add(jdk["jdk_version"])
        
        self._current_options = sorted(list(versions), reverse=True)
        self._last_prompt = f"选择 {vendor} 的版本"
        return self

    def data(self) -> Optional[Dict[str, Any]]:
        """
        收集并返回最终的 JDK 元数据
        :return: 元数据字典
        """
        if self._is_interrupted or not self._raw_data: return None
        
        version = self._selected_value
        self._metadata["version"] = version
        
        vendor = self._metadata.get("vendor")
        os = self._metadata.get("os")
        arch = self._metadata.get("arch")
        
        for jdk in self._raw_data:
            if jdk["vendor"] == vendor and jdk["jdk_version"] == version:
                for pkg in jdk.get("packages", []):
                    if pkg["os"] == os and pkg["arch"] == arch:
                        self._metadata.update({
                            "product": jdk.get("product"),
                            "filename": pkg["archive_file_name"],
                            "url": pkg["url"]
                        })
                        return self._metadata
        return self._metadata

def selectMax(options):
    # 简单的示例：寻找最大的版本号
    return options[0] if options else None

