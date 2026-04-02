from dataclasses import dataclass
from typing import List
from pathlib import Path

from prompt_toolkit import PromptSession

from install.client.ini.jdk_ini_manager import JdksManager
from install.client.install_base_cli import BaseInstallCLIData

from loader import DownloadsManager
from loader.ini.extract_manager import ExtractManager
from wing_ui.file_browser_ui import RichFileBrowser

from wing_utils.extract import UniversalExtractor
from loader.ini.theme_manager import ThemeManager
from wing_client import BaseCLI, BaseCommand
from install.retrieval_flow_builder import JDKRetrievalFlowBuilder, Note
from loader import StyleLoader
from wing_ui import WingUI
from wing_ui.rich_wing_ui import RichWingUI
from install import wing_dialog_selector
from wing_utils.download.download_utils import DownloadUtils
from wing_utils.system import UserEnvRunner, EnvManager
from wing_utils.system.env.path_env_utils import PathEnvUtils


#
@dataclass
class JdkCLIData(BaseInstallCLIData):
    env_manager: "JdksManager"


#
#
class JdkCLI(BaseCLI[JdkCLIData]):
    def init_business_logic(self):
        loader = StyleLoader()
        self.data = JdkCLIData(
            tm=ThemeManager(),
            sl=loader,
            downloadsManager=DownloadsManager(),
            wingUi=WingUI(styleLoader=loader),
            universalExtractor=UniversalExtractor(),
            env_manager=JdksManager(),
            richUi=RichWingUI(styleLoader=loader),
            extractManager=ExtractManager(),
        )

        """JDK环境管理CLI
        提供类似theme_cli.py的界面，用于管理多个JDK版本和环境变量。
        """

    def get_action_map(self):
        """获取动作映射"""
        mapping = super().get_action_map()
        mapping.update(
            {
                "do_ls": self.do_ls,
                "do_set": self.do_set,
                "do_add": self.do_add,
                "do_remove": self.do_remove,
                "do_info": self.do_info,
            }
        )

        # 自动注册静态动作
        self._auto_actions = self.auto_register_static_actions({
            "do_init": self.do_init,
            "do_install": self.do_install
        })
        mapping.update(self._auto_actions)
        return mapping

    def get_cmd_tree(self):
        """获取命令树"""
        tree = super().get_cmd_tree()

        # 获取JDK版本列表用于自动补全
        def get_jdk_versions() -> List[str]:
            return list(self.data.env_manager.list().keys())

        tree.append(BaseCommand("ls", "ls", "列出所有JDK版本", "do_ls"))
        tree.append(BaseCommand("add", "add", "手动添加新的JDK版本", "do_add"))
        tree.append(BaseCommand("remove", "remove <version>", "删除指定JDK版本", "do_remove",
                                dynamic_completer=get_jdk_versions))
        tree.append(BaseCommand("info", "info", "显示JDK详细信息", "do_info", ))
        tree.append(BaseCommand("install", "install", "安装JDK", "do_install", ))
        tree.append(BaseCommand("init", "init", "安装JDK", "do_init", ))
        tree.append(BaseCommand("set", "set <version>", "设置当前使用的JDK版本", "do_set",
                                dynamic_completer=get_jdk_versions))

        return tree

    def do_install(self):
        try:
            downloads_dir = self.data.downloadsManager.get_current_downloads_dir() / self.data.env_manager.key.value
            extract_dir = self.data.extractManager.get_current_extract_dir() / self.data.env_manager.key.value

            # 获取JDK信息
            jdk_result = (JDKRetrievalFlowBuilder.default(os="windows", arch="x86_64", selector=wing_dialog_selector)
                          .fetch_data()
                          .vendor().deal(
                note=[
                    Note("Alibaba", "recommend")
                ]
            )
                          .select_ui()
                          .version().deal()
                          .select_ui()
                          .data()
                          )

            # 打印标题
            self.data.richUi.print_rule("JDK安装信息")

            # 使用表格形式打印字典数据
            self.data.richUi.print_dict_as_table(
                jdk_result,
                title="JDK详细信息",
                key_column="属性",
                value_column="值",
                show_index=True
            )

            # 打印下载URL的特别提示
            if 'url' in jdk_result:
                self.data.richUi.print_info(f"下载URL: {jdk_result['url']}", title="下载链接")

            # 获取版本和URL
            version = jdk_result["version"]
            url = jdk_result["url"]

            # 询问是否下载
            yes_or_no_download = self.data.richUi.yes_or_no(f"是否直接下载JDK {version}?")
            if yes_or_no_download:
                # 直接下载
                self._print_message(f"开始下载JDK {version}...", "info")
                saved_file_ok = DownloadUtils.download(url, str(downloads_dir))
                self._print_message(f"✅ 下载完成: {saved_file_ok}", "success")
            else:
                # 提示可以放入的下载目录
                self.data.wingUi.message_ui(
                    f"温馨提示",
                    text=f"下载地址:{downloads_dir}\n你可以将下载的文件放入该文件夹中\n没有放入会导致安装失败")
                self._print_message(f"请将JDK文件放入: {downloads_dir}", "warning")

            # 解压部分
            self._print_message(f"开始解压JDK {version}...", "info")
            extracted_path = self.data.universalExtractor.extract(str(downloads_dir), f"{str(extract_dir)}/{version}")
            self._print_message(f"✅ 提取完成，路径: {extracted_path}", "success")

            # 选择真实的JDK路径
            browser = RichFileBrowser(self.data.sl, extracted_path, "dir", title="请选择真实的Jdk路径",
                                      select_regex=None,
                                      regex_match_fullpath=False)
            jdk_path = browser.run()

            # 确认JDK路径
            confirm_path = self.data.wingUi.yes_no_ui(f"是否确认Jdk是该文件夹路径", f"Jdk路径{jdk_path}")

            if not confirm_path:
                self._print_message("❌ 安装已取消", "error")
                return

            # 初始化环境变量
            if not self.do_init():
                self._print_message("❌ 初始化环境变量失败", "error")
                return

            # 添加JDK到管理器
            try:
                self.data.env_manager.add(version, jdk_path)
                self._print_message(f"✅ JDK版本 {version} 添加成功", "success")

                # 设置为当前JDK
                if self.data.env_manager.set_current_env(self.data.env_manager.list()[version]):
                    self._print_message(f"✅ 已将 {version} 设置为当前JDK", "success")

                    # # 更新环境变量
                    # if self.update_java_env():
                    #     self._print_message("✅ Java环境变量已更新", "success")
                    # else:
                    #     self._print_message("⚠️ Java环境变量更新失败，可能需要手动设置", "warning")
                else:
                    self._print_message(f"❌ 设置 {version} 为当前JDK失败", "error")

            except FileNotFoundError as e:
                self._print_message(f"❌ 错误: {e}", "error")
            except Exception as e:
                self._print_message(f"❌ 添加JDK失败: {e}", "error")

        except Exception as e:
            self._print_message(f"❌ 安装过程出错: {e}", "error")

    def do_add(self, _):
        sub_session = PromptSession()
        version = sub_session.prompt("请输入JDK版本号: ").strip()
        if not version:
            self._print_message("❌ JDK版本号不能为空。", "error")
            return

        # 检查版本是否已存在
        jdks = self.data.env_manager.list()
        if version in jdks:
            self._print_message(f"❌ JDK版本 {version} 已存在。", "error")
            return

        path = sub_session.prompt("请输入JDK安装路径: ").strip()
        if not path:
            self._print_message("❌ 路径不能为空。", "error")
            return

        try:
            self.data.env_manager.add(version, path)
            self._print_message(f"✅ JDK版本 {version} 添加成功。", "success")

            # 询问是否设置为当前
            set_current = sub_session.prompt(f"是否将 {version} 设置为当前JDK? (y/N): ").strip().lower()
            if set_current == 'y':
                if self.data.env_manager.set_current_env(self.data.env_manager.list()[version]):
                    self._print_message(f"✅ 已将 {version} 设置为当前JDK。", "success")
                else:
                    self._print_message(f"❌ 设置 {version} 为当前JDK失败。", "error")
        except FileNotFoundError as e:
            self._print_message(f"❌ 错误: {e}", "error")
        except Exception as e:
            self._print_message(f"❌ 添加JDK失败: {e}", "error")

    def do_set(self, args):
        if not args:
            self._print_message("❌ 用法错误: set <version>", "error")
            return

        version = args[0]
        jdks = self.data.env_manager.list()

        if version not in jdks:
            self._print_message(f"❌ JDK版本 {version} 不存在。", "error")
            return

        try:
            # 设置当前JDK
            if self.data.env_manager.set_current_env(self.data.env_manager.list()[version]):
                self._print_message(f"✅ 已将 {version} 设置为当前JDK。", "success")

                # 更新环境变量
                # if self.update_java_env():
                #     self._print_message("✅ Java环境变量已更新。", "success")
                # else:
                #     self._print_message("⚠️ Java环境变量更新失败，可能需要手动设置。", "warning")
            else:
                self._print_message(f"❌ 设置 {version} 为当前JDK失败。", "error")
        except Exception as e:
            self._print_message(f"❌ 设置失败: {e}", "error")

    def do_remove(self, args):
        if not args:
            self._print_message("❌ 用法错误: remove <version>", "error")
            return

        version = args[0]
        jdks = self.data.env_manager.list()

        if version not in jdks:
            self._print_message(f"❌ JDK版本 {version} 不存在。", "error")
            return

        # 获取当前JDK
        current_jdk = self.data.env_manager.get_current_env()

        # 确认删除
        sub_session = PromptSession()
        confirm = sub_session.prompt(f"确认删除JDK版本 {version}? (y/N): ").strip().lower()

        if confirm != 'y':
            self._print_message("❌ 删除操作已取消。", "warning")
            return

        try:
            self.data.env_manager.remove(version)
            self._print_message(f"✅ 已删除JDK版本 {version}。", "success")

            # 如果删除的是当前JDK，需要重新设置
            if current_jdk == version:
                self._print_message(f"⚠️ 已删除当前JDK版本 {version}，请使用'set'命令重新设置其他版本。", "warning")
        except Exception as e:
            self._print_message(f"❌ 删除JDK失败: {e}", "error")

    def do_ls(self, _):
        jdks = self.data.env_manager.list()
        if not jdks:
            self._print_message("⚠️ 目前没有任何JDK版本。", "warning")
            return
        self._print_message("📚 已配置JDK版本：", "info")
        for version, path in jdks.items():
            self._print_message(f"  {version} → {path}", "cyan")

    def do_info(self, _):
        # 获取所有JDK
        jdks = self.data.env_manager.list()

        # 获取当前JDK信息
        current_jdk = self.data.env_manager.get_current_env()
        current_path = self.data.env_manager.get_current_env_path()
        path_exists = self.data.env_manager.get_current_env_path_exists()

        self._print_message("🔍 JDK环境信息", "info")

        # 显示当前JDK
        if current_jdk:
            self._print_message(f"当前JDK版本: {current_jdk}", "success")
            self._print_message(f"当前JDK路径: {current_path}", "cyan")

            if path_exists:
                self._print_message("路径状态: ✅ 存在", "success")
            else:
                self._print_message("路径状态: ❌ 不存在", "error")
        else:
            self._print_message("当前JDK: 未设置", "warning")

        # 显示所有JDK数量
        if jdks:
            self._print_message(f"已配置JDK数量: {len(jdks)}", "info")
        else:
            self._print_message("已配置JDK数量: 0", "warning")

    def do_init(self) -> bool:
        # 初始化jdk环境变量,直接指向C:\Windows即可，后续做改变
        # 创建成功
        if self.data.env_manager.get_current_env_path_exists():
            # 若是存在代表初始过了
            return True
        if self.data.env_manager.set_current_env("C:/Windows"):
            return self.update_java_env()
        else:
            self._print_message("初始化环境变量失败", "error")
            return False

    def update_java_env(self) -> bool:
        """更新Java环境变量"""
        try:
            # 启动用户环境变量工具
            user_manager = EnvManager(UserEnvRunner())

            # 获取当前JDK路径
            current_path = self.data.env_manager.get_current_env_path()
            if not current_path or not current_path.exists():
                self._print_message("❌ 当前JDK路径不存在", "error")
                return False

            # 设置JAVA_HOME环境变量
            user_manager.add("JAVA_HOME", str(current_path))

            # 获取当前PATH
            path_result = user_manager.get("PATH")
            if path_result and "value" in path_result:
                current_path_str = path_result["value"]

                # 将%JAVA_HOME%\bin添加到PATH最前面
                new_path_list = PathEnvUtils.insert_path_at_index(
                    PathEnvUtils.path_str_to_list(current_path_str),
                    "%JAVA_HOME%\\bin",
                    0
                )

                # 更新PATH环境变量
                user_manager.add("PATH", PathEnvUtils.list_to_path_str(new_path_list))
                self._print_message("✅ Java环境变量已更新", "success")
                return True
            else:
                self._print_message("❌ 无法获取PATH环境变量", "error")
                return False

        except Exception as e:
            self._print_message(f"❌ 更新环境变量失败: {e}", "error")
            return False


if __name__ == "__main__":
    # JdkCLI(prompt_text="JDKManager > ").run()
    JdkCLI(prompt_text="JDKManager > ").execute_argv(["help"])
