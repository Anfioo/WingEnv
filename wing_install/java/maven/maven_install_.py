import os
import re
from pathlib import Path
from utils.downloader import download_with_progress
from utils.extract_archiver import extract_archive_with_progress
from utils.env_variable_manager import WinEnvManager
from wing_install.java.maven.maven_analysis_utils import get_maven_windows_links
from wing_install.java.maven.maven_config import config_ui_main
from wing_ui.button_choice_dialogs import button_ui
from wing_ui.input_dialogs import input_text_ui
from wing_ui.selection_dialogs import select_single_option_ui
from prompt_toolkit import HTML

from utils.ini.maven_manager import MavenManager


def select_maven_package():
    packages = get_maven_windows_links()
    if not packages:
        print("❌ 无可用的 Maven 下载包。")
        return None, None

    # 1. 安装路径输入
    install_path = input_text_ui(
        title="Maven 安装路径输入",
        text="请输入 Maven 安装目录",
        default="C:\\Apps\\Envs\\Maven"
    )
    if not install_path:
        print("⚠️ 用户取消路径输入。")
        return None, None

    # 2. 版本选择
    config = {
        p['version']: (f"Maven {p['version']} - {p['filename']}", "normal")
        for p in packages
    }

    selected = select_single_option_ui(
        title="选择 Maven 版本",
        text="请选择一个要安装的 Maven 版本",
        config=config
    )
    if selected is None:
        print("⚠️ 用户取消版本选择。")
        return None, None

    selected_package = next(p for p in packages if p['version'] == selected)

    return install_path, selected_package


def download_and_extract_maven(path: str, package: dict, mm: MavenManager):
    version = package['version']
    url = package['download_link']
    filename = os.path.basename(url)

    download_dir = os.path.join(path, "Download")
    os.makedirs(download_dir, exist_ok=True)
    download_path = os.path.join(download_dir, filename)

    # 下载
    if os.path.exists(download_path):
        print(f"📂 已存在，跳过下载：{download_path}")
    else:
        print(f"⬇️ 开始下载：{url}")
        download_with_progress(url=url, save_dir=download_dir, use_true_color=True)

    # 解压
    print(f"📦 解压到目录：{path}")
    extracted_path = extract_archive_with_progress(download_path, path)

    # 添加至 MavenManager
    mm.add_maven_version(version, extracted_path)
    return version, extracted_path


def confirm_set_maven_env() -> str:
    return button_ui(
        title="设置 Maven 环境变量？",
        text=HTML(
            "<b>是否将当前 Maven 设置为默认版本（写入用户环境变量）？\n</b>"
            '<style fg="#3e2723">Y(用户)：使用用户变量</style>'
        ),
        buttons=[
            ("Y(用户)", "sure-user"),
            ("N(取消)", "cancel"),
        ]
    )


def set_env_variables(choice: str, maven_path: str):
    if choice == "sure-user":
        print("🔧 正在设置 MAVEN 用户环境变量...")
        user_env = WinEnvManager()
        user_env.set_variable("MAVEN_HOME", maven_path) \
            .add_path(r"%MAVEN_HOME%\bin") \
            .execute()
        print("✅ MAVEN_HOME 已设置。")


def maven_install_main():
    path, package = select_maven_package()
    if not path or not package:
        print("❌ 安装流程被中止。")
        return

    print("📁 安装路径：", path)
    mm = MavenManager()

    version, maven_path = download_and_extract_maven(path, package, mm)

    # 设置默认版本
    mm.set_current_version(version)
    print(f"✅ 当前 Maven 版本设为：{version}")
    print(f"📌 安装路径：{maven_path}")

    # 设置环境变量
    choice = confirm_set_maven_env()
    if choice == "sure-user":
        set_env_variables(choice, maven_path)
    else:
        print("⚠️ 未设置 MAVEN_HOME 环境变量。")


    #设置配置文件路径
    config_ui_main(maven_path+"\conf\settings.xml")







if __name__ == "__main__":
    maven_install_main()
