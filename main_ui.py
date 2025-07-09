from config.wing_modules_config import WING_MODULES_CONFIG
from wing_ui.selection_dialogs import select_single_option_ui
from prompt_toolkit.formatted_text import HTML


def main_menu():
    main_options = {
        key: val["label"] for key, val in WING_MODULES_CONFIG.items()
    }

    selected_main = select_single_option_ui(
        config=main_options,
        title=HTML("<ansiblue><b>🧠 Wing 环境管理器</b></ansiblue>"),
        text="请选择一个模块进入："
    )

    if not selected_main:
        print("👋 已取消选择。")
        return

    category = WING_MODULES_CONFIG.get(selected_main)
    module_options = category["modules"]

    selected_module = select_single_option_ui(
        config=module_options,
        title=HTML(f"<ansigreen><b>{category['label']}</b></ansigreen>"),
        text="请选择要安装或管理的组件："
    )

    if not selected_module:
        print("👋 已取消选择。")
        return

    # 示例调用模块处理逻辑（需你在每类 CLI 入口实现处理）
    from wing_install.dispatcher import dispatch_module
    dispatch_module(category_key=selected_main, module_key=selected_module)


if __name__ == "__main__":
    main_menu()
