from typing import Any, Callable, Optional, Dict, Self
import requests
import re
from bs4 import BeautifulSoup
from install.builder.builder_base import BaseFlowBuilder

# CMake 官方归档根目录
CMAKE_BASE_URL = "https://cmake.org/files/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


class CMakeFlowBuilder(BaseFlowBuilder):
    @classmethod
    def default(cls, selector: Callable = None) -> Self:
        """
        创建 CMake 构建流程实例
        :param selector: UI 选择器
        :return: CMakeFlowBuilder 实例
        """
        return cls(selector=selector)

    def fetch_main_data(self) -> Self:
        """
        解析主目录，寻找版本文件夹 (v3.0, v3.1...)
        :return: Self
        """
        if self._is_interrupted: return self
        try:
            r = requests.get(CMAKE_BASE_URL, headers=HEADERS, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # 提取所有以 'v' 开头的文件夹链接
            v_dirs = []
            for a in soup.find_all('a'):
                href = a.get('href', '')
                if re.match(r'^v\d+\.\d+/?$', href):
                    v_dirs.append(href.strip('/'))
            
            # 排序：让最新的版本在前面
            v_dirs.sort(key=lambda x: [int(d) for d in re.findall(r'\d+', x)], reverse=True)
            self._raw_data = v_dirs
        except Exception as e:
            print(f"❌ 访问主目录失败: {e}")
            self._is_interrupted = True
        return self

    def version_dir(self) -> Self:
        """
        选择 CMake 主版本目录
        :return: Self
        """
        if self._is_interrupted or not self._raw_data: return self
        
        self._current_options = self._raw_data[:20] # 展示前20个主版本目录
        self._last_prompt = "选择 CMake 主版本目录"
        return self

    def fetch_version_files(self) -> Self:
        """
        解析选定的版本目录下的具体文件
        :return: Self
        """
        if self._is_interrupted or not self._selected_value: return self
        
        target_dir = self._selected_value
        self._metadata["version_dir"] = target_dir
        version_url = f"{CMAKE_BASE_URL}{target_dir}/"
        self._metadata["version_url"] = version_url
        
        try:
            r = requests.get(version_url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            
            files_info = []
            for tr in soup.find_all('tr'):
                tds = tr.find_all('td')
                a_tag = tr.find('a')
                if a_tag:
                    filename = a_tag.text.strip()
                    if filename in ["Parent Directory", "Name", "Last modified", "Size", "Description"] or "/" in filename:
                        continue
                    if filename.endswith(('.sha256', '.asc', '.md5')):
                        continue
                    size = tds[3].text.strip() if len(tds) >= 4 else "N/A"
                    files_info.append({"name": filename, "size": size})
            
            self._files_info = files_info
        except Exception as e:
            print(f"❌ 访问版本目录失败: {e}")
            self._is_interrupted = True
        return self

    def file(self) -> Self:
        """
        选择具体的安装包
        :return: Self
        """
        if self._is_interrupted or not self._files_info: return self
        
        file_options = [f"{f['name']} ({f['size']})" for f in self._files_info]
        self._current_options = file_options
        self._last_prompt = "选择具体的安装包"
        return self

    def data(self) -> Optional[Dict[str, Any]]:
        """
        生成最终元数据
        :return: 元数据字典
        """
        if self._is_interrupted or not self._selected_value: return None
        
        # 还原文件名 (去掉括号里的 size)
        final_filename = self._selected_value.split(' (')[0]
        download_url = f"{self._metadata['version_url']}{final_filename}"
        
        return {
            "product": "CMake",
            "version": self._metadata["version_dir"],
            "filename": final_filename,
            "url": download_url
        }



