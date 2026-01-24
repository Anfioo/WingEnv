import requests
import sys
import re
from bs4 import BeautifulSoup

# CMake 官方归档根目录
CMAKE_BASE_URL = "https://cmake.org/files/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def get_soup(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        print(f"❌ 访问失败: {url}\n错误信息: {e}")
        sys.exit(1)


def select(prompt, options):
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt}")
    while True:
        val = input("\n请选择编号: ").strip()
        try:
            idx = int(val)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except ValueError:
            pass
        print("输入无效，请重新输入")


def main():
    # 1. 解析主目录，寻找版本文件夹 (v3.0, v3.1...)
    print(f"正在读取 CMake 版本索引...")
    soup_main = get_soup(CMAKE_BASE_URL)

    # 提取所有以 'v' 开头的文件夹链接
    v_dirs = []
    for a in soup_main.find_all('a'):
        href = a.get('href', '')
        if re.match(r'^v\d+\.\d+/?$', href):
            v_dirs.append(href.strip('/'))

    # 排序：让最新的版本在前面 (例如 v3.31 在 v3.1 前面)
    v_dirs.sort(key=lambda x: [int(d) for d in re.findall(r'\d+', x)], reverse=True)

    # 2. 让用户选择主版本目录 (展示前15个)
    target_dir = select("选择 CMake 主版本目录", v_dirs[:15])
    version_url = f"{CMAKE_BASE_URL}{target_dir}/"

    # 3. 解析选定的版本目录
    print(f"正在读取 {target_dir} 下的文件列表...")
    soup_ver = get_soup(version_url)

    files_info = []
    for tr in soup_ver.find_all('tr'):
        tds = tr.find_all('td')
        # 典型的 Apache 目录结构，文件名在第2个 td 或 a 标签中
        a_tag = tr.find('a')
        if a_tag:
            filename = a_tag.text.strip()
            # 过滤掉 "Parent Directory" 和 校验文件
            if filename in ["Parent Directory", "Name", "Last modified", "Size", "Description"] or "/" in filename:
                continue
            if filename.endswith(('.sha256', '.asc', '.md5')):
                continue

            # 获取大小 (通常在第4个 td)
            size = tds[3].text.strip() if len(tds) >= 4 else "N/A"
            files_info.append({"name": filename, "size": size})

    if not files_info:
        print("⚠️ 该目录下未找到有效的安装包文件。")
        return

    # 4. 让用户选择具体文件
    # 过滤出用户可能感兴趣的 (例如 windows, linux, macos)
    search_key = input("\n输入关键词过滤文件 (直接回车查看全部): ").strip().lower()
    filtered_files = [f for f in files_info if search_key in f['name'].lower()]

    if not filtered_files:
        print("未找到匹配关键词的文件。")
        filtered_files = files_info

    selected_file = select("选择具体的安装包", [f"{f['name']} ({f['size']})" for f in filtered_files])

    # 还原文件名 (去掉括号里的 size)
    final_filename = selected_file.split(' (')[0]
    download_url = f"{version_url}{final_filename}"

    # 5. 输出结果
    print("\n✅ 解析成功")
    print("=" * 60)
    print(f"产品名称   : CMake")
    print(f"目录层级   : {target_dir}")
    print(f"文件名     : {final_filename}")
    print(f"下载链接   : {download_url}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已取消")