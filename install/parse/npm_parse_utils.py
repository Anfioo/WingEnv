import requests
import sys

# 镜像源字典
MIRRORS = {
    "阿里镜像 (npmmirror)": "https://npmmirror.com/mirrors/node",
    "清华大学镜像 (TUNA)": "https://mirrors.tuna.tsinghua.edu.cn/nodejs-release",
    "Node.js 官方": "https://nodejs.org/dist"
}

# 你提供的请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Connection": "keep-alive"
}


def fetch_node_versions(base_url):
    index_url = f"{base_url}/index.json"
    print(f"\n正在从 {base_url} 获取版本列表...")
    try:
        # 使用自定义 HEADERS 解决清华源等镜像的校验问题
        r = requests.get(index_url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
        sys.exit(1)


def select(prompt, options, is_version=False):
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        if is_version:
            lts_info = f" [LTS: {opt['lts']}]" if opt['lts'] else ""
            display = f"{opt['version']}{lts_info}"
        else:
            display = opt
        print(f"  [{i}] {display}")

    while True:
        try:
            val = input("请选择编号: ").strip()
            idx = int(val)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except Exception:
            pass
        print("输入无效，请重新输入")


def parse_download_url(base_url, version, file_type):
    """
    解析转换逻辑
    """
    ext = "tar.gz"
    platform_suffix = file_type

    if file_type.startswith("win-"):
        if "zip" in file_type:
            ext = "zip";
            platform_suffix = file_type.replace("-zip", "")
        elif "7z" in file_type:
            ext = "7z";
            platform_suffix = file_type.replace("-7z", "")
        elif "msi" in file_type:
            ext = "msi";
            platform_suffix = file_type.replace("-msi", "")
        elif "exe" in file_type:
            ext = "exe";
            platform_suffix = file_type.replace("-exe", "")
    elif file_type.startswith("osx-"):
        if "tar" in file_type:
            ext = "tar.gz";
            platform_suffix = file_type.replace("-tar", "")
        elif "pkg" in file_type:
            ext = "pkg";
            platform_suffix = file_type.replace("-pkg", "")

    filename = f"node-{version}-{platform_suffix}.{ext}"
    url = f"{base_url}/{version}/{filename}"
    return filename, url


def main():
    # 0. 选择镜像源
    mirror_names = list(MIRRORS.keys())
    selected_mirror_name = select("请选择下载源", mirror_names)
    base_url = MIRRORS[selected_mirror_name]

    # 1. 获取数据
    data = fetch_node_versions(base_url)

    # 2. 选择版本
    selected_item = select("选择 Node.js 版本", data[:20], is_version=True)
    target_version = selected_item['version']

    # 3. 选择架构
    available_files = [f for f in selected_item['files'] if f not in ['headers', 'src']]
    target_file_type = select(f"选择 {target_version} 的平台架构", available_files)

    # 4. 最终解析
    filename, download_url = parse_download_url(base_url, target_version, target_file_type)

    print(f"\n✅ 解析成功 (源: {selected_mirror_name})")
    print("=" * 60)
    print(f"Node 版本   : {target_version}")

    print(f"NPM 版本    : {selected_item.get('npm')}")
    print(f"LTS 代号    : {selected_item.get('lts') or 'None'}")
    print(f"发布日期    : {selected_item.get('date')}")
    print(f"V8 版本     : {selected_item.get('v8')}")
    print(f"libuv 版本  : {selected_item.get('uv')}")
    print(f"Zlib 版本   : {selected_item.get('zlib')}")
    print(f"OpenSSL 版本: {selected_item.get('openssl')}")
    print(f"Modules    : {selected_item.get('modules')}")
    print(f"Security Fix: {selected_item.get('security')}")
    print(f"可用平台    : {', '.join(selected_item.get('files', []))}")
    print(f"文件名      : {filename}")

    print(f"下载地址    : {download_url}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户取消操作")
        sys.exit(0)
