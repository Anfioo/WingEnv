import requests
import sys
from collections import defaultdict

JDK_FEED_URL = "https://download.jetbrains.com/jdk/feed/v1/jdks.json"


def fetch_jdks():
    r = requests.get(JDK_FEED_URL, timeout=10)
    r.raise_for_status()
    return r.json().get("jdks", [])


def select(prompt, options):
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt}")
    while True:
        try:
            idx = int(input("请选择编号: ").strip())
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except Exception:
            pass
        print("输入无效，请重新输入")


def main():
    jdks = fetch_jdks()

    # --------------------------------
    # 1️⃣ 从真实数据中提取 OS / arch
    # --------------------------------
    os_arch_map = defaultdict(set)

    for jdk in jdks:
        for pkg in jdk.get("packages", []):
            os_arch_map[pkg["os"]].add(pkg["arch"])

    if not os_arch_map:
        print("❌ 未解析到任何 package")
        return

    # -------- OS 选择 --------
    os_list = sorted(os_arch_map.keys())
    target_os = select("选择平台", os_list)

    # -------- Arch 选择 --------
    arch_list = sorted(os_arch_map[target_os])
    target_arch = select("选择架构", arch_list)

    # --------------------------------
    # 2️⃣ 过滤“真实存在的 JDK”
    # --------------------------------
    valid_jdks = []
    for jdk in jdks:
        for pkg in jdk.get("packages", []):
            if pkg["os"] == target_os and pkg["arch"] == target_arch:
                valid_jdks.append(jdk)
                break

    if not valid_jdks:
        print("❌ 当前 OS + 架构下没有 JDK（理论上不该发生）")
        return

    # -------- Vendor --------
    vendors = sorted({j["vendor"] for j in valid_jdks})
    vendor = select("选择 JDK 厂商", vendors)

    vendor_jdks = [j for j in valid_jdks if j["vendor"] == vendor]

    # -------- Version --------
    versions = sorted(
        {j["jdk_version"] for j in vendor_jdks},
        reverse=True
    )
    version = select("选择 JDK 版本", versions)

    # -------- Package（必定存在）--------
    for jdk in vendor_jdks:
        if jdk["jdk_version"] != version:
            continue
        for pkg in jdk["packages"]:
            if pkg["os"] == target_os and pkg["arch"] == target_arch:
                print("\n✅ 最终选择结果")
                print("=" * 45)
                print(f"厂商     : {jdk['vendor']}")
                print(f"产品     : {jdk.get('product')}")
                print(f"版本     : {jdk['jdk_version']}")
                print(f"平台     : {pkg['os']}")
                print(f"架构     : {pkg['arch']}")
                print(f"文件名   : {pkg['archive_file_name']}")
                print(f"下载地址 : {pkg['url']}")
                print("=" * 45)
                return

    print("❌ 未找到 package（逻辑异常）")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已取消")
        sys.exit(0)
