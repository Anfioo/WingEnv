import requests
import sys
from bs4 import BeautifulSoup

# Miniconda 目录地址
CONDA_PAGE_URL = "https://repo.anaconda.com/miniconda/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def fetch_conda_html_data():
    print(f"正在抓取 Miniconda 目录页: {CONDA_PAGE_URL}")
    try:
        r = requests.get(CONDA_PAGE_URL, headers=HEADERS, timeout=15)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, 'html.parser')
        rows = soup.find_all('tr')

        file_list = []
        for row in rows:
            tds = row.find_all('td')
            # 根据你提供的 HTML 结构：第一列是文件名(含a标签)，第二列是Size，第四列是SHA256
            if len(tds) >= 4:
                a_tag = tds[0].find('a')
                if a_tag:
                    filename = a_tag.text.strip()
                    # 我们通常只需要最新的安装包 (包含 "-latest-")
                    if "-latest-" in filename:
                        file_list.append({
                            "filename": filename,
                            "size": tds[1].text.strip(),
                            "date": tds[2].text.strip(),
                            "sha256": tds[3].text.strip()
                        })
        return file_list
    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
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
    # 1. 抓取网页并解析出 latest 文件列表
    all_files = fetch_conda_html_data()
    if not all_files:
        print("未能解析到有效的 latest 文件列表")
        return

    # 2. 提取操作系统 (从文件名识别: Windows, Linux, MacOSX)
    os_list = sorted(list(set([f['filename'].split('-')[2] for f in all_files])))
    target_os = select("选择操作系统 (OS)", os_list)

    # 3. 提取对应的架构 (从文件名识别: x86_64, arm64 等)
    filtered_by_os = [f for f in all_files if f['filename'].split('-')[2] == target_os]
    # 架构通常在名字的后面部分，处理后缀
    arch_list = sorted(list(set([f['filename'].split('-')[3].split('.')[0] for f in filtered_by_os])))
    target_arch = select(f"选择 {target_os} 的架构", arch_list)

    # 4. 选择具体的文件格式 (如果是 MacOS 有 .sh 和 .pkg)
    final_candidates = [f for f in filtered_by_os if target_arch in f['filename']]

    if len(final_candidates) > 1:
        # 如果有多个文件，展示完整文件名供选择
        names = [f['filename'] for f in final_candidates]
        selected_name = select("选择具体的安装包格式", names)
        target_file = next(f for f in final_candidates if f['filename'] == selected_name)
    else:
        target_file = final_candidates[0]

    # 5. 输出结果
    download_url = f"{CONDA_PAGE_URL}{target_file['filename']}"

    print("\n✅ 解析成功")
    print("=" * 60)
    print(f"产品名称   : Miniconda3 (Latest)")
    print(f"操作系统   : {target_os}")
    print(f"硬件架构   : {target_arch}")
    print(f"文件名     : {target_file['filename']}")
    print(f"文件大小   : {target_file['size']}")
    print(f"发布日期   : {target_file['date']}")
    print(f"SHA256    : {target_file['sha256']}")
    print(f"下载链接   : {download_url}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已取消")