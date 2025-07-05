import re
from collections import defaultdict

from wing_env_install.java_install.analysis_java_utils import get_openjdk_archives
from wing_env_install.java_install.install_java_package_utils import install_java_package
from wing_env_install.java_install.java_config_utils import JavaConfigManager
from wing_env_install.java_install.java_set_env import set_user_java_env
from wing_env_ui.path_input_ui_util import input_install_path
from wing_env_ui.select_ui_util import select_from_list
from wing_env_ui.sure_ui_util import confirm_action_ui, show_message_ui


def select_java_download_link(versions):
    """
    交互式选择 Java 主版本 -> 具体包（含版本号、构建号、平台包信息），直接输出下载链接。
    """

    if not versions:
        print("❌ 无可用版本数据")
        return

    # Step 1: 分组 Java 主版本
    grouped = defaultdict(list)
    for v in versions:
        match = re.search(r'(\d+)', v['version'])
        major = match.group(1) if match else 'Unknown'
        grouped[major].append(v)

    sorted_majors = sorted(grouped.keys(), key=int)

    # Step 2: 选择 Java 主版本
    major_index = select_from_list(
        options=[f"JAVA {v}" for v in sorted_majors],
        title="选择 Java 主版本",
        text="请选择一个 Java 主版本号"
    )

    if major_index is None:
        print("⚠️  已取消主版本选择。")
        return

    selected_major = sorted_majors[major_index[0]]
    selected_versions = grouped[selected_major]

    # Step 3: 整合该主版本下的所有 Windows 包展示项
    combined_options = []
    platform_map = []

    for v in selected_versions:
        version_info = f"{v['version']} (构建号: {v['build']})"
        for p in v.get('platforms', []):
            # 只保留 Windows 平台
            if 'windows' in p['os'].lower():
                label = f"{version_info}  |  {p['package']} | {p['os']} {p['architecture']} | {p['file_size_formatted']}"
                combined_options.append(label)
                platform_map.append((v, p))  # 记录对应的版本和平台信息

    if not combined_options:
        print(f"⚠️  JAVA {selected_major} 没有可用的 Windows 平台安装包。")
        return

    # Step 4: 选择具体包（版本+平台） -> 输出下载链接
    selected_index = select_from_list(
        options=combined_options,
        title=f"JAVA {selected_major} 安装包选择",
        text="请选择一个安装包以获取下载链接"
    )

    if selected_index is None:
        print("⚠️  已取消选择。")
        return

    selected_version, selected_platform = platform_map[selected_index[0]]

    print("\n✅ 下载信息如下：")
    print(f"版本: {selected_version['version']} ({selected_version['build']})")
    print(f"平台: {selected_platform['os']} {selected_platform['architecture']}")
    print(f"包类型: {selected_platform['package']}")
    print(f"文件大小: {selected_platform['file_size_formatted']}")
    print(f"🔗 下载链接: {selected_platform['download_link']}")
    print(f"🔐 SHA256 校验: {selected_platform['sha256_link']}")

    return selected_platform['download_link'], selected_version['version'].split(".")[0]


# 主函数
def java_install():
    # 解析并安装java 包
    path = input_install_path(default_path="C:\\Apps\\Envs\\JDK", title="JAVA路径", text="请输入安装路径")
    url = "https://jdk.java.net/archive/"
    all_versions = get_openjdk_archives(url)
    link, version = select_java_download_link(all_versions)
    file_path = install_java_package(link, path)

    # 保存配置文件
    mgr = JavaConfigManager()
    mgr.add_java_path(version, file_path)


    if confirm_action_ui("变量确认", "已经安装新的java是否需要更新系统变量？（第一次安装建议更新）"):
        set_user_java_env(file_path)
        show_message_ui("操作结果", "系统变量更新成功")
    else:
        show_message_ui("操作结果", "已取消更新系统变量")


if __name__ == "__main__":
    java_install()
