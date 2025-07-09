# wing_install/dispatcher.py

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import print_formatted_text as print_html

from wing_install.java.jdk.jdk_shell import JdkCLI


def dispatch_module(category_key: str, module_key: str):
    """
    根据模块分类和具体模块名称调度相应的 CLI 控制台或处理逻辑。
    """
    if category_key == "java":
        cli = JdkCLI()
        cli.start()

    elif category_key == "python":
        print_html(HTML("<ansiyellow>🚧 Python 模块尚未开发，敬请期待！</ansiyellow>"))

    elif category_key == "nodejs":
        print_html(HTML("<ansiyellow>🚧 Node.js 模块尚未开发，敬请期待！</ansiyellow>"))

    elif category_key == "go":
        print_html(HTML("<ansiyellow>🚧 Go 模块尚未开发，敬请期待！</ansiyellow>"))

    elif category_key == "rust":
        print_html(HTML("<ansiyellow>🚧 Rust 模块尚未开发，敬请期待！</ansiyellow>"))

    elif category_key == "database":
        print_html(HTML(f"<ansiyellow>🚧 数据库模块（{module_key}）尚未开发，敬请期待！</ansiyellow>"))

    elif category_key == "storage":
        print_html(HTML(f"<ansiyellow>🚧 存储模块（{module_key}）尚未开发，敬请期待！</ansiyellow>"))

    elif category_key == "middleware":
        print_html(HTML(f"<ansiyellow>🚧 中间件模块（{module_key}）尚未开发，敬请期待！</ansiyellow>"))

    elif category_key == "devops":
        print_html(HTML(f"<ansiyellow>🚧 DevOps 模块（{module_key}）尚未开发，敬请期待！</ansiyellow>"))

    else:
        print_html(HTML(f"<ansired>❌ 未知模块类型: {category_key}</ansired>"))
