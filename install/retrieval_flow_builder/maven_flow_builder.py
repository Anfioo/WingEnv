from typing import Any, Callable, Optional, Dict, Self
import requests
import xml.etree.ElementTree as ET

from install.retrieval_flow_builder import BaseRetrievalFlowBuilder

# Maven 元数据地址 (阿里云镜像，同步快且稳定)
MAVEN_METADATA_URL = "https://maven.aliyun.com/repository/public/org/apache/maven/apache-maven/maven-metadata.xml"
# 官方下载基础路径
MAVEN_DOWNLOAD_BASE = "https://archive.apache.org/dist/maven/maven-3"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "application/xml, text/xml, */*; q=0.01",
    "Connection": "keep-alive"
}


class MavenRetrievalFlowBuilder(BaseRetrievalFlowBuilder):
    @classmethod
    def default(cls, selector: Callable = None) -> Self:
        """
        创建 Maven 构建流程实例
        :param selector: UI 选择器
        :return: MavenFlowBuilder 实例
        """
        return cls(selector=selector)

    def fetch_data(self) -> Self:
        """
        手动触发网络请求，获取 Maven 版本列表 (从阿里云元数据)
        :return: Self
        """
        if self._is_interrupted: return self
        try:
            r = requests.get(MAVEN_METADATA_URL, headers=HEADERS, timeout=10)
            r.raise_for_status()
            
            # 解析 XML
            root = ET.fromstring(r.text)
            # 获取所有 version 标签下的文本
            versions = [v.text for v in root.findall(".//version")]
            # 倒序排列，让最新版本在前面
            self._raw_data = sorted(versions, reverse=True)
        except Exception as e:
            print(f"❌ 获取 Maven 数据失败: {e}")
            self._is_interrupted = True
        return self

    def version(self) -> Self:
        """
        准备待选的 Maven 版本列表
        :return: Self
        """
        if self._is_interrupted or not self._raw_data: return self
        
        # 过滤掉 alpha, beta, rc 等非正式版本
        stable_versions = [v for v in self._raw_data if '-' not in v]
        self._current_options = stable_versions[:20] # 取前20个稳定版本
        self._last_prompt = "选择 Maven 版本"
        return self

    def format(self) -> Self:
        """
        准备待选的安装包格式列表
        :return: Self
        """
        if self._is_interrupted: return self
        
        target_version = self._selected_value
        self._metadata["version"] = target_version
        
        self._current_options = ["bin.zip", "bin.tar.gz"]
        self._last_prompt = "选择压缩包格式"
        return self

    def data(self) -> Optional[Dict[str, Any]]:
        """
        收集并返回最终的 Maven 元数据
        :return: 元数据字典
        """
        if self._is_interrupted or not self._selected_value: return None
        
        target_version = self._metadata["version"]
        selected_format = self._selected_value
        
        # 拼接地址
        filename = f"apache-maven-{target_version}-{selected_format}"
        download_url = f"{MAVEN_DOWNLOAD_BASE}/{target_version}/binaries/{filename}"
        
        return {
            "product": "Apache Maven",
            "version": target_version,
            "filename": filename,
            "url": download_url
        }


