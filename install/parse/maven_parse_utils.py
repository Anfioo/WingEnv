import requests
import sys
import xml.etree.ElementTree as ET

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


def fetch_maven_versions():
    print(f"正在获取 Maven 版本列表...")
    try:
        r = requests.get(MAVEN_METADATA_URL, headers=HEADERS, timeout=10)
        r.raise_for_status()

        # 解析 XML
        root = ET.fromstring(r.text)
        # 获取所有 version 标签下的文本
        versions = [v.text for v in root.findall(".//version")]
        # 倒序排列，让最新版本在前面
        return sorted(versions, reverse=True)
    except Exception as e:
        print(f"❌ 获取 Maven 数据失败: {e}")
        sys.exit(1)


def select(prompt, options):
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt}")
    while True:
        try:
            val = input("请选择编号: ").strip()
            idx = int(val)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except:
            pass
        print("输入无效，请重新输入")


def main():
    # 1. 获取所有版本
    all_versions = fetch_maven_versions()

    # 2. 过滤掉 alpha, beta, rc 等非正式版本 (可选)
    stable_versions = [v for v in all_versions if '-' not in v]

    # 3. 让用户选择版本 (展示前 15 个稳定版)
    target_version = select("选择 Maven 版本", stable_versions[:15])

    # 4. 构建下载链接
    # Maven 的规则比较简单：通常提供 bin.zip (Win) 和 bin.tar.gz (Linux)
    formats = ["bin.zip", "bin.tar.gz"]
    selected_format = select("选择压缩包格式", formats)

    # 拼接地址
    # 注意：Maven 3.x 存放在 maven-3 目录下
    filename = f"apache-maven-{target_version}-{selected_format}"
    download_url = f"{MAVEN_DOWNLOAD_BASE}/{target_version}/binaries/{filename}"

    print("\n✅ 解析成功")
    print("=" * 60)
    print(f"产品名称   : Apache Maven")
    print(f"选定版本   : {target_version}")
    print(f"文件名     : {filename}")
    print(f"下载链接   : {download_url}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已取消")