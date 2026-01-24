import requests
import sys

# Go 官方 JSON 接口
GO_API_URL = "https://go.dev/dl/?mode=json&include=all"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def fetch_go_data():
    """获取所有 Go 版本的 JSON 数据"""
    print("正在从 go.dev 获取版本信息...")
    try:
        r = requests.get(GO_API_URL, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ 获取 Go 数据失败: {e}")
        sys.exit(1)


def select(prompt, options):
    """通用的命令行交互选择器"""
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
    # 1. 获取所有数据
    data = fetch_go_data()

    # 2. 提取版本列表 (只展示稳定版)
    stable_versions = [v['version'] for v in data if v.get('stable')]
    target_version_str = select("选择 Go 语言版本", stable_versions[:15])

    # 找到选定版本的详细数据
    version_data = next(item for item in data if item['version'] == target_version_str)

    # 3. 让用户选择操作系统 (OS)
    # 提取该版本支持的所有 OS，并去重
    os_list = sorted(list(set(f['os'] for f in version_data['files'] if f['os'])))
    target_os = select("选择操作系统 (OS)", os_list)

    # 4. 让用户选择架构 (Arch)
    # 筛选出符合 OS 的架构
    arch_list = sorted(list(set(f['arch'] for f in version_data['files'] if f['os'] == target_os and f['arch'])))
    target_arch = select("选择处理器架构 (Arch)", arch_list)

    # 5. 让用户选择安装包格式 (Kind/Extension)
    # 比如 msi, pkg, tar.gz, zip
    files = [f for f in version_data['files'] if f['os'] == target_os and f['arch'] == target_arch]

    # 格式化选项用于展示
    file_options = [f"{f['kind']} ({f['filename'].split('.')[-1]})" for f in files]
    selected_option = select("选择安装包格式", file_options)

    # 获取对应的文件对象
    target_file = files[file_options.index(selected_option)]

    # 6. 输出结果
    download_url = f"https://go.dev/dl/{target_file['filename']}"

    print("\n✅ 解析成功")
    print("=" * 60)
    print(f"产品名称   : Go Language")
    print(f"选定版本   : {target_version_str}")
    print(f"操作系统   : {target_os}")
    print(f"架构      : {target_arch}")
    print(f"文件名     : {target_file['filename']}")
    print(f"SHA256    : {target_file['sha256']}")
    print(f"下载链接   : {download_url}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已取消")