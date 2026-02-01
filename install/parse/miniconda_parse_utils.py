from typing import Any, Callable, Optional, Dict, Self
import requests
from bs4 import BeautifulSoup
from install.builder.builder_base import BaseFlowBuilder

# Miniconda 目录地址
CONDA_PAGE_URL = "https://repo.anaconda.com/miniconda/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


class MinicondaFlowBuilder(BaseFlowBuilder):
    @classmethod
    def default(cls, selector: Callable = None) -> Self:
        """
        创建 Miniconda 构建流程实例
        :param selector: UI 选择器
        :return: MinicondaFlowBuilder 实例
        """
        return cls(selector=selector)

    def fetch_data(self) -> Self:
        """
        抓取网页并解析出 latest 文件列表
        :return: Self
        """
        if self._is_interrupted: return self
        try:
            r = requests.get(CONDA_PAGE_URL, headers=HEADERS, timeout=15)
            r.raise_for_status()

            soup = BeautifulSoup(r.text, 'html.parser')
            rows = soup.find_all('tr')

            file_list = []
            for row in rows:
                tds = row.find_all('td')
                if len(tds) >= 4:
                    a_tag = tds[0].find('a')
                    if a_tag:
                        filename = a_tag.text.strip()
                        if "-latest-" in filename:
                            file_list.append({
                                "filename": filename,
                                "size": tds[1].text.strip(),
                                "date": tds[2].text.strip(),
                                "sha256": tds[3].text.strip()
                            })
            self._raw_data = file_list
        except Exception as e:
            print(f"❌ 获取 Miniconda 数据失败: {e}")
            self._is_interrupted = True
        return self

    def os(self) -> Self:
        """
        选择操作系统 (OS)
        :return: Self
        """
        if self._is_interrupted or not self._raw_data: return self
        
        os_list = sorted(list(set([f['filename'].split('-')[2] for f in self._raw_data])))
        self._current_options = os_list
        self._last_prompt = "选择操作系统 (OS)"
        return self

    def arch(self) -> Self:
        """
        选择处理器架构 (Arch)
        :return: Self
        """
        if self._is_interrupted or not self._selected_value: return self
        
        target_os = self._selected_value
        self._metadata["os"] = target_os
        
        filtered_by_os = [f for f in self._raw_data if f['filename'].split('-')[2] == target_os]
        self._filtered_by_os = filtered_by_os # 暂存
        
        arch_list = sorted(list(set([f['filename'].split('-')[3].split('.')[0] for f in filtered_by_os])))
        self._current_options = arch_list
        self._last_prompt = f"选择 {target_os} 的架构"
        return self

    def format(self) -> Self:
        """
        选择具体的安装包格式
        :return: Self
        """
        if self._is_interrupted or not self._selected_value: return self
        
        target_arch = self._selected_value
        self._metadata["arch"] = target_arch
        
        final_candidates = [f for f in self._filtered_by_os if target_arch in f['filename']]
        self._final_candidates = final_candidates # 暂存
        
        if len(final_candidates) > 1:
            names = [f['filename'] for f in final_candidates]
            self._current_options = names
            self._last_prompt = "选择具体的安装包格式"
        else:
            # 只有一个选项，标记为自动跳过 UI
            self._selected_value = final_candidates[0]['filename']
            self._skip_ui = True
            
        return self

    def data(self) -> Optional[Dict[str, Any]]:
        """
        生成最终元数据
        :return: 元数据字典
        """
        if self._is_interrupted or not self._selected_value: return None
        
        selected_name = self._selected_value
        try:
            target_file = next(f for f in self._final_candidates if f['filename'] == selected_name)
            
            return {
                "product": "Miniconda",
                "os": self._metadata["os"],
                "arch": self._metadata["arch"],
                "filename": target_file['filename'],
                "size": target_file['size'],
                "sha256": target_file['sha256'],
                "url": f"{CONDA_PAGE_URL}{target_file['filename']}"
            }
        except (StopIteration, KeyError):
            return None

