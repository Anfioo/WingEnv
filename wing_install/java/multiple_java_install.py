from collections import defaultdict
import re

from wing_env_install.java_install.analysis_java_utils import get_openjdk_archives
from wing_env_install.java_install.install_java_package_utils import install_java_package
from wing_env_install.java_install.java_config_utils import JavaConfigManager
from wing_env_install.java_install.java_set_env import set_user_java_env
from wing_env_ui.path_input_ui_util import input_install_path
from wing_env_ui.select_ui_util import select_from_list, multi_select_from_list
from prompt_toolkit.shortcuts import yes_no_dialog, message_dialog

from wing_env_ui.sure_ui_util import confirm_action_ui, show_message_ui


def confirm_action(title: str = "确认操作",
                   message: str = "你确定要执行此操作吗？",
                   yes_text: str = "确认",
                   no_text: str = "取消") -> bool:
    return yes_no_dialog(
        title=title,
        text=message,
        yes_text=yes_text,
        no_text=no_text
    ).run()


def show_message(title: str = "消息", message: str = "操作完成") -> None:
    message_dialog(
        title=title,
        text=message
    ).run()


def multi_select_java_download_links(versions):
    if not versions:
        print("❌ 无可用版本数据")
        return

    # Step 1: 按主版本分组
    grouped = defaultdict(list)
    for v in versions:
        match = re.search(r'(\d+)', v['version'])
        major = match.group(1) if match else 'Unknown'
        grouped[major].append(v)

    sorted_majors = sorted(grouped.keys(), key=int)

    # Step 2: 多选主版本
    major_selection = multi_select_from_list(
        options=[f"JAVA {v}" for v in sorted_majors],
        title="选择 Java 主版本",
        text="可多选需要安装的 Java 主版本"
    )

    if not major_selection:
        print("⚠️  用户取消了主版本选择。")
        return

    selected_majors = [sorted_majors[i] for i, _ in major_selection]

    # Step 3: 是否逐个配置
    individually = confirm_action(
        title="安装方式选择",
        message="是否逐个选择每个 Java 主版本的具体安装包？\n（推荐：逐一确认下载包）",
        yes_text="逐个选择",
        no_text="全部使用默认（最新）"
    )
    selected_links = []
    print("\n✅ 安装计划如下：\n")

    for major in selected_majors:
        selected_versions = grouped[major]

        # Windows 安装包过滤 + 排序（假设第一个是最新）
        available = []
        for v in selected_versions:
            for p in v.get('platforms', []):
                if 'windows' in p['os'].lower():
                    available.append((v, p))

        if not available:
            print(f"⚠️ JAVA {major} 没有可用的 Windows 安装包。")
            continue

        if individually:
            # 展示所有包给用户选一个
            combined_options = []
            for idx, (v, p) in enumerate(available):
                label = f"{v['version']} ({v['build']}) | {p['package']} | {p['os']} {p['architecture']} | {p['file_size_formatted']}"
                combined_options.append(label)

            result = select_from_list(
                options=combined_options,
                title=f"JAVA {major} 安装包选择",
                text="请选择一个安装包"
            )

            if result is None:
                print(f"⚠️ JAVA {major} 已跳过。")
                continue

            selected_version, selected_platform = available[result[0]]
        else:
            # 直接使用第一个可用项（假设最新）
            selected_version, selected_platform = available[0]

        # 输出安装包信息
        print(f"🔸 JAVA {major} 下载信息")
        print(f"版本: {selected_version['version']} ({selected_version['build']})")
        print(f"平台: {selected_platform['os']} {selected_platform['architecture']}")
        print(f"包类型: {selected_platform['package']}")
        print(f"文件大小: {selected_platform['file_size_formatted']}")
        print(f"🔗 下载链接: {selected_platform['download_link']}")
        print(f"🔐 SHA256 校验: {selected_platform['sha256_link']}\n")
        selected_links.append({selected_version['version'].split(".")[0]: selected_platform['download_link']})

    return selected_links


# 主调用
def java_multi_install():
    path = input_install_path(default_path="C:\\Apps\\Envs\\JDK", title="JAVA路径", text="请输入安装路径")
    url = "https://jdk.java.net/archive/"
    all_versions = get_openjdk_archives(url)
    configs = multi_select_java_download_links(all_versions)

    v_list = []
    p_list = []

    for item in configs:
        for version, url in item.items():
            print(f"Java版本: {version}，下载链接: {url}")

            file_path = install_java_package(url, path)
            # 保存配置文件
            mgr = JavaConfigManager()
            mgr.add_java_path(version, file_path)
            v_list.append(version)
            p_list.append(file_path)

    selection_index = select_from_list(
        options=[f"JAVA {v}" for v in v_list],
        title="选择环境变量 Java 版本",
        text="请选择一个 Java 版本号"
    )

    if selection_index and len(selection_index) > 0:
        selected_idx = selection_index[0]
        selected_path = p_list[selected_idx]
    else:
        selected_idx = None
        selected_path = None

    if selected_path is None:
        show_message_ui("错误", "未选择 Java 版本，无法更新系统变量")
        return  # 或者结束

    if confirm_action_ui("变量确认",
                         "已经安装新的java是否需要更新系统变量？（第一次安装建议更新，使用上面确认的Java版本）"):
        set_user_java_env(selected_path)
        show_message_ui("操作结果", "系统变量更新成功")
    else:
        show_message_ui("操作结果", "已取消更新系统变量")


if __name__ == '__main__':
    java_multi_install()
