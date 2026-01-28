from dataclasses import dataclass
from typing import Dict, Callable
import time

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import print_formatted_text as print_html

from loader.ini.progress_bar_manager import ProgressBarManager
from loader.style_loader import StyleLoader
from wing_ui.dialog_ui import WingUI
from wing_client import BaseCLI, BaseCommand


@dataclass
class ProgressBarCLIData:
    pbm: "ProgressBarManager"
    sl: "StyleLoader"
    wu: "WingUI"


class ProgressBarCLI(BaseCLI[ProgressBarCLIData]):
    def init_business_logic(self):
        loader = StyleLoader()

        self.data = ProgressBarCLIData(
            pbm=ProgressBarManager(),
            sl=loader,
            wu=WingUI(loader)
        )

    def get_action_map(self):
        mapping = super().get_action_map()
        mapping.update(
            {
                "do_ls": self.do_ls,
                "do_info": self.do_info,
                "do_set": self.do_set,
                "do_get": self.do_get,
                "do_test": self.do_test,
            }
        )
        return mapping

    def get_cmd_tree(self):
        tree = super().get_cmd_tree()
        tree.append(BaseCommand("ls", "ls", "列出所有支持的进度条主题", "do_ls"))
        tree.append(BaseCommand("info", "info", "显示当前设置的进度条主题", "do_info"))
        tree.append(BaseCommand("set", "set <name>", "设置当前进度条主题", "do_set",
                                dynamic_completer=lambda: list(self.data.pbm.get_available_themes())))
        tree.append(BaseCommand("get", "get <all|name>", "展示指定或所有进度条的颜色", "do_get",
                                dynamic_completer=lambda: list(self.data.pbm.get_available_themes()) + ["all"]))
        tree.append(BaseCommand("test", "test <name>", "测试指定主题的进度条效果", "do_test",
                                dynamic_completer=lambda: list(self.data.pbm.get_available_themes())))
        return tree

    def run_test_progress_bar(self, test_bar_name, fast_mode=False):
        pb, task = self.data.wu.get_progress_bar_context(
            iterable=range(50),
            task_description="任务进行中",
            title=f"测试进度条 - {test_bar_name}",
            total=50,
            use_true_color=True,
            use_style_name=test_bar_name
        )

        with pb:
            for _ in task:
                if not fast_mode:
                    time.sleep(0.05)  # 原始速度

    def do_ls(self, _):
        themes = sorted(self.data.pbm.get_available_themes())
        if not themes:
            self._print_message("⚠️ 没有可用主题", "error")
        else:
            self._print_message("支持的进度条主题列表：", "info")
            for t in themes:
                self._print_message(f"  {t}", "info")

    def do_info(self, _):
        current = self.data.pbm.get_progress_bar_theme()
        self._print_message(f"当前进度条主题：{current}", "success")

    def do_set(self, args):
        if not args:
            self._print_message("❌ 用法错误: set <主题名>", "error")
            return
        name = args[0]
        try:
            self.data.pbm.set_progress_bar_theme(name)
            self._print_message(f"✅ 主题已设置为 {name}", "success")
        except ValueError as e:
            self._print_message(f"❌ {e}", "error")

    def do_get(self, args):
        themes = self.data.pbm.get_available_themes()
        if not themes:
            self._print_message("⚠️ 没有可用主题", "error")
            return

        if not args:
            self._print_message("❌ 用法错误: get all 或 get <主题名>", "error")
            return

        target = args[0].lower()

        if target == 'all':
            self._print_message("📦 正在展示所有进度条主题（快速模式）...", "info")
            for theme in themes:
                self._print_message(f"▶ 主题：{theme}", "info")
                self.run_test_progress_bar(theme, fast_mode=True)
            self._print_message("✅ 所有主题展示完毕！", "success")
        elif target in themes:
            self._print_message(f"▶ 正在展示主题：{target}（快速模式）", "info")
            self.run_test_progress_bar(target, fast_mode=True)
            self._print_message("✅ 展示完毕！", "success")
        else:
            self._print_message(f"❌ 未知主题: {target}", "error")

    def do_test(self, args):
        if not args:
            self._print_message("❌ 用法错误: test <主题名>", "error")
            return
        name = args[0]
        try:
            self.run_test_progress_bar(name)
            self._print_message(f"✅ 测试完成！", "success")
        except ValueError as e:
            self._print_message(f"❌ {e}", "error")


if __name__ == "__main__":
    ProgressBarCLI(prompt_text="ProgressBarManager > ").run()
