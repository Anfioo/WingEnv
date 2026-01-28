from dataclasses import dataclass
from typing import Dict, Callable

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import print_formatted_text as print_html

from loader.style_loader import StyleLoader
from wing_ui.dialog_ui import WingUI
from wing_utils.ui.css_color_viewer_utils import CssColorViewer
from loader.ini.theme_manager import ThemeManager
from wing_utils.ui.ui_test_utils import TestUiUtils
from wing_client import BaseCLI, BaseCommand


@dataclass
class ThemeCLIData:
    tm: "ThemeManager"
    sl: "StyleLoader"
    ui_test_utils: "TestUiUtils"


class ThemeCLI(BaseCLI[ThemeCLIData]):
    def init_business_logic(self):
        loader = StyleLoader()

        self.data = ThemeCLIData(
            tm=ThemeManager(),
            sl=loader,
            ui_test_utils=TestUiUtils(WingUI(loader))
        )

    def get_action_map(self):
        mapping = super().get_action_map()
        mapping.update(
            {
                "do_ls": self.do_ls,
                "do_set": self.do_set,
                "do_add": self.do_add,
                "do_remove": self.do_remove,
                "do_info": self.do_info,
                "do_get": self.do_get,
                "do_test": self.do_test,

            }
        )
        self._auto_actions = self.auto_register_static_actions({
            "button_choice_dialogs_test": self.data.ui_test_utils.button_choice_dialogs_test,
            "input_dialogs_test": self.data.ui_test_utils.input_dialogs_test,
            "message_dialogs_test": self.data.ui_test_utils.message_dialogs_test,
            "test_single_select": self.data.ui_test_utils.test_single_select,
            "test_multi_select": self.data.ui_test_utils.test_multi_select,
            "test_yes_no_dialog": self.data.ui_test_utils.test_yes_no_dialog
        })
        mapping.update(self._auto_actions)

        return mapping

    def get_cmd_tree(self):
        tree = super().get_cmd_tree()
        tree.append(BaseCommand("ls", "ls", "列出主题", "do_ls"))
        tree.append(BaseCommand("add", "add", "添加新主题", "do_add"))
        tree.append(BaseCommand("remove", "remove <name>", "删除指定主题", "do_remove",
                                dynamic_completer=lambda: list(self.data.tm.list_themes().keys())))
        tree.append(BaseCommand("info", "info", "显示当前主题及路径", "do_info"))
        tree.append(BaseCommand("set", "set <name>", "设置当前主题", "do_set",
                                dynamic_completer=lambda: list(self.data.tm.list_themes().keys())))
        tree.append(BaseCommand("get", "get <all|name>", "展示指定或所有主题的颜色", "do_get", dynamic_completer=lambda: list(self.data.tm.list_themes().keys())+["all"]))
        tree.append(BaseCommand("test", "test <name>", "测试主题ui组件", "do_test", [
            BaseCommand("button_choice", "button_choice_dialogs_test", "选择测试对话框", "button_choice_dialogs_test"),
            BaseCommand("input", "input_dialogs_test", "输入测试对话框", "input_dialogs_test"),
            BaseCommand("message", "message_dialogs_test", "消息测试对话框", "message_dialogs_test"),
            BaseCommand("single_select", "test_single_select", "单选测试对话框", "test_single_select"),
            BaseCommand("multi_select", "test_multi_select", "多选测试对话框", "test_multi_select"),
            BaseCommand("yes_no", "test_yes_no_dialog", "确认测试对话框", "test_yes_no_dialog"),

        ], dynamic_completer=lambda: ["all"]))
        return tree

    def do_test(self, args):
        tests_map = {
            "button_choice_dialogs_test": self.data.ui_test_utils.button_choice_dialogs_test,
            "input_dialogs_test": self.data.ui_test_utils.input_dialogs_test,
            "message_dialogs_test": self.data.ui_test_utils.message_dialogs_test,
            "test_single_select": self.data.ui_test_utils.test_single_select,
            "test_multi_select": self.data.ui_test_utils.test_multi_select,
            "test_yes_no_dialog": self.data.ui_test_utils.test_yes_no_dialog,
        }
        if not args:
            self._print_message("❌ 用法错误: test <all|method_name>", "error")
            return

        if args[0] == "all":
            for name, func in tests_map.items():
                try:
                    self._print_message(f"开始执行测试: {name}", "warning")
                    func()
                    self._print_message(f"✅ 测试 {name} 完成", "success")
                except Exception as e:
                    self._print_message(f"❌ 测试 {name} 出错: {e}", "error")
            self._print_message("✅ 所有测试完成。", "success")
        else:
            method_name = args[0]
            func = tests_map.get(method_name)
            if func is None:
                self._print_message(f"❌ 未知测试方法: {method_name}", "error")
                return
            try:
                self._print_message(f"开始执行测试: {method_name}", "warning")
                func()
                self._print_message(f"✅ 测试 {method_name} 完成", "success")
            except Exception as e:
                self._print_message(f"❌ 测试 {method_name} 出错: {e}", "error")

    def do_get(self, args):
        themes = self.data.tm.list_themes()
        if not args:
            self._print_message("❌ 用法错误: get <all|主题名>", "error")
            return

        if args[0] == 'all':
            if not themes:
                self._print_message("⚠️ 目前没有任何主题。", "warning")
                return
            for name, path in themes.items():
                try:
                    viewer = CssColorViewer(path)
                    viewer.show_colors()
                except Exception as e:
                    self._print_message(f"❌ 读取主题 {name} 失败: {e}", "error")
        else:
            name = args[0]
            if name not in themes:
                self._print_message(f"❌ 主题 {name} 不存在。", "error")
                return
            try:
                viewer = CssColorViewer(themes[name])
                viewer.show_colors()
            except Exception as e:
                self._print_message(f"❌ 读取主题 {name} 失败: {e}", "error")

    def do_ls(self, _):
        themes = self.data.tm.list_themes()
        if not themes:
            self._print_message("⚠️ 目前没有任何主题。", "warning")
            return
        self._print_message("📚 已配置主题：", "info")
        for name, path in themes.items():
            self._print_message(f"  {name} → {path}", "cyan")

    def do_add(self, _):
        sub_session = PromptSession()
        name = sub_session.prompt("请输入主题名称: ").strip()
        if not name:
            self._print_message("❌ 主题名不能为空。", "error")
            return
        css_path = sub_session.prompt("请输入 CSS 文件路径: ").strip()
        if not css_path:
            self._print_message("❌ CSS 路径不能为空。", "error")
            return

        try:
            self.data.tm.add_theme(name, css_path)
            self._print_message(f"✅ 主题 {name} 添加成功。", "success")
            # 父类会自动刷新补全
        except FileNotFoundError as e:
            self._print_message(f"❌ 错误: {e}", "error")
        except Exception as e:
            self._print_message(f"❌ 添加主题失败: {e}", "error")

    def do_remove(self, args):
        if not args:
            self._print_message("❌ 用法错误: remove <name>", "error")
            return
        name = args[0]
        if not self.data.tm.theme_exists(name):
            self._print_message(f"❌ 主题 {name} 不存在。", "error")
            return
        self.data.tm.remove_theme(name)
        self._print_message(f"✅ 已删除主题 {name}。（不删除 CSS 文件）", "warning")
        # 父类会自动刷新补全

    def do_info(self, _):
        name = self.data.tm.get_current_theme()
        path = self.data.tm.get_current_theme_path()
        self._print_message(f"当前主题: {name}", "success")
        self._print_message(f"CSS 路径: {path or '未设置'}", "cyan")

    def do_set(self, args):
        if not args:
            self._print_message("❌ 用法错误: set <name>", "error")
            return
        name = args[0]
        if not self.data.tm.theme_exists(name):
            self._print_message(f"❌ 主题 {name} 不存在。", "error")
            return
        try:
            self.data.tm.set_current_theme(name)
            # 更新 WingUI 实例的样式，确保测试使用最新主题
            self.data.ui_test_utils.wing_ui.flash()
            self._print_message(f"✅ 当前主题已切换为 {name}", "success")

        except Exception as e:
            self._print_message(f"❌ 设置失败: {e}", "error")

    def do_exit(self, _):
        self._print_message("👋 再见！", 'info')
        exit(0)

    def do_quit(self, args):
        self.do_exit(args)


if __name__ == "__main__":
    ThemeCLI(prompt_text="ThemeManager > ").run()
