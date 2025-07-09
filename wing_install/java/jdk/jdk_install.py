from utils.downloader import download_with_progress
from utils.env_variable_manager import WinEnvManager
from utils.extract_archiver import extract_archive_with_progress
from utils.ini.java_manager import JavaManager
from wing_install.java.jdk.jdk_analysis_utils import get_openjdk_archives
from wing_ui.button_choice_dialogs import button_ui
from wing_ui.input_dialogs import input_text_ui
from wing_ui.selection_dialogs import select_single_option_ui, select_multiple_options_ui
from collections import defaultdict
from prompt_toolkit import HTML


def select_java_packages():
    # 0. 获取 OpenJDK 归档页面数据
    url = "https://jdk.java.net/archive/"
    archives = get_openjdk_archives(url)

    if not archives:
        print("❌ 无可用版本数据，退出。")
        return None, []

    # 1. 选择安装路径
    install_path = input_text_ui(
        title="JAVA 路径选择",
        text="请输入 JAVA 安装路径",
        default="C:\\Apps\\Envs\\JDK"
    )



    if install_path is None:
        print("⚠️ 用户取消安装路径输入。")
        return None, []

    # 2. 安装模式：单个 / 多个
    install_mode = select_single_option_ui(
        title="安装模式选择",
        text="请选择安装模式",
        config={
            "single": ("单个安装", "normal"),
            "multi": ("批量安装（多版本）", "normal")
        }
    )
    if install_mode is None:
        print("⚠️ 用户取消安装模式选择。")
        return None, []

    # 3. 按主版本号分组
    grouped = defaultdict(list)
    for v in archives:
        m = re.search(r'(\d+)', v['version'])
        major = m.group(1) if m else 'Unknown'
        grouped[major].append(v)

    sorted_majors = sorted(grouped.keys(), key=int)

    # 4. 主版本选择
    if install_mode == "single":
        sel_major = select_single_option_ui(
            title="选择 Java 主版本",
            text="请选择一个 Java 主版本号",
            config={v: (f"JAVA {v}", "normal") for v in sorted_majors}
        )
        if sel_major is None:
            print("⚠️ 用户取消主版本选择。")
            return None, []
        chosen_majors = [sel_major]
    else:
        chosen_majors = select_multiple_options_ui(
            title="批量选择 Java 主版本",
            text="请选择一个或多个 Java 主版本号",
            config={v: (f"JAVA {v}", "normal") for v in sorted_majors}
        )
        if not chosen_majors:
            print("⚠️ 用户未选择任何主版本或已取消。")
            return None, []

    # 5. 是否默认安装所有版本
    use_default = False
    if install_mode == "multi":
        default_choice = select_single_option_ui(
            title="批量安装默认选择",
            text="是否对所有选中的主版本都使用默认（最后一个 Windows 包）？",
            config={
                "yes": ("是，全部默认（使用最新包）", "normal"),
                "no": ("否，逐一手动选择", "normal")
            }
        )
        if default_choice is None:
            print("⚠️ 用户取消默认选择操作。")
            return None, []
        use_default = (default_choice == "yes")

    # 6. 每个主版本分别处理
    selected_packages = []
    for major in chosen_majors:
        versions = grouped[major]
        options = []
        map_vp = []
        for v in versions:
            info = f"{v['version']} (构建: {v['build']})"
            for p in v.get("platforms", []):
                if "windows" in p['os'].lower():
                    label = f"{info} | {p['package']} | {p['os']} {p['architecture']} | {p['file_size_formatted']}"
                    options.append(label)
                    map_vp.append((v, p))

        if not options:
            print(f"⚠️ JAVA {major} 没有 Windows 安装包，跳过。")
            continue

        if install_mode == "single" or use_default:
            sel_label = options[-1]
        else:
            sel_label = select_single_option_ui(
                title=f"JAVA {major} 安装包选择",
                text=f"请选择 JAVA {major} 的安装包",
                config={label: (label, "normal") for label in options}
            )
            if sel_label is None:
                print(f"⚠️ 用户取消 JAVA {major} 的安装包选择。")
                return None, []

        idx = options.index(sel_label)
        version, platform = map_vp[idx]

        selected_packages.append({
            "version": version['version'],
            "build": version['build'],
            "os": platform['os'],
            "arch": platform['architecture'],
            "package": platform['package'],
            "file_size": platform['file_size_formatted'],
            "download_link": platform['download_link'],
            "sha256_link": platform.get("sha256_link")
        })

    return install_path, selected_packages


import os
import re


def download_and_extract_packages(path, packages, jm):
    """
    下载并解压所有 JDK 包，添加到 JavaManager。
    返回安装的版本信息列表。
    """
    installed_versions = []

    for item in packages:
        print(f"📦 Java {item['version']} (构建: {item['build']})")
        print(f"平台: {item['os']} {item['arch']} | 包类型: {item['package']}")
        print(f"文件大小: {item['file_size']}")
        print(f"下载链接: {item['download_link']}")
        if item['sha256_link']:
            print(f"校验文件: {item['sha256_link']}")
        print("-" * 60)

        save_dir = os.path.join(path, "Download")
        os.makedirs(save_dir, exist_ok=True)

        filename = os.path.basename(item['download_link'])
        download_path = os.path.join(save_dir, filename)

        if os.path.exists(download_path):
            print(f"📂 文件已存在，跳过下载：{download_path}")
        else:
            print(f"⬇️ 开始下载：{item['download_link']}")
            download_with_progress(
                url=item['download_link'],
                save_dir=save_dir,
                use_true_color=True
            )

        print(f"📦 解压到目录：{item['version']}")
        java_path = extract_archive_with_progress(download_path, path)

        # 提取主版本号，比如 "17.0.12" -> "17"
        major_version_match = re.match(r"(\d+)", item['version'])
        major_version = major_version_match.group(1) if major_version_match else item['version']

        installed_versions.append({
            "major_version": major_version,
            "full_version": item['version'],
            "build": item['build'],
            "path": java_path
        })

        jm.add_java_version(major_version, java_path)

    return installed_versions


def get_unique_versions(installed_versions):
    """
    去重主版本号，保持安装顺序。
    """
    seen = set()
    unique_versions = []
    for v in installed_versions:
        if v["major_version"] not in seen:
            seen.add(v["major_version"])
            unique_versions.append(v)
    return unique_versions


def select_jdk_version(unique_versions):
    """
    通过 UI 让用户选择 JDK 主版本，最后一个选项为重要样式。
    返回选中的主版本号字符串。
    """
    config = {}
    for i, v in enumerate(unique_versions):
        label = f"{v['major_version']} (对应完整版本: {v['full_version']}, 构建: {v['build']})"
        style = "important" if i == len(unique_versions) - 1 else "normal"
        config[label] = (label, style)

    selected_label = select_single_option_ui(
        title="选择当前使用的 JDK 主版本",
        text="请选择一个主版本作为当前 JDK",
        config=config
    )

    for v in unique_versions:
        label = f"{v['major_version']} (对应完整版本: {v['full_version']}, 构建: {v['build']})"
        if label == selected_label:
            return v['major_version']

    return None


def confirm_update_java_version() -> str:
    """弹出确认是否更新 Java 版本的按钮对话框，返回选择值。"""
    return button_ui(
        title="更新 Java 版本确认",
        text=HTML(
            '<b>是否需要设置 / 更新当前使用的Java版本？</b>\n'
            '<style fg="#3e2723">Y(用户)：使用用户变量</style>\n'
            '<style fg="#b71c1c">'
            '<style bg="#b71c1c" fg="#3e2723">注：</style>'
            '使用用户变量时，需确保与系统变量无冲突；若存在冲突，系统变量优先级更高\n'
            '可能导致失效的问题</style>'
        ),
        buttons=[
            ("Y(用户)", "sure-user"),
            ("N(取消)", "cancel"),
        ]
    )


def set_env_variables(choice: str, java_path: str):
    """根据用户选择设置环境变量."""
    if choice == "sure-user":
        print("🔧 设置用户环境变量...")
        user_env = WinEnvManager()
        user_env.set_variable("JAVA_HOME", java_path) \
            .add_path(r"%JAVA_HOME%\bin") \
            .add_path(r"%JAVA_HOME%\jre\bin") \
            .execute()
        print("✅ 用户环境变量已更新。")


def java_install_main():
    path, packages = select_java_packages()

    jm = JavaManager()

    if path is None:
        print("❌ 安装流程已被用户中止。")
        return

    print("\n✅ 安装路径：", path)

    installed_versions = download_and_extract_packages(path, packages, jm)
    unique_versions = get_unique_versions(installed_versions)

    choice = confirm_update_java_version()

    if choice in ("sure-user", "sure-admin"):
        selected_major_version = select_jdk_version(unique_versions)

        if selected_major_version:
            jm.set_current_version(selected_major_version)
            java_path = jm.get_current_java_path()
            print(f"✅ 已设置当前主版本为: {selected_major_version}")
            print(f"当前 JDK 路径: {java_path}")

            set_env_variables(choice, java_path)
            return
        else:
            print("⚠️ 未设置当前版本。")
            return

    elif choice == "cancel":
        print("❌ 用户取消了更新操作。")
        return


if __name__ == "__main__":
    java_install_main()
