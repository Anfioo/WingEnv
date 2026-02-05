from sys import path
from pathlib import Path

# 设置项目根目录到 sys.path
project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.dialog_ui import WingUI
from loader.style_loader import StyleLoader
from install.configure_flow_builder.base_builder import BaseConfigureFlowBuilder

# 创建样式加载器和 WingUI 实例
style_loader = StyleLoader()
wing_ui = WingUI(style_loader)

# 初始化构建者
builder = BaseConfigureFlowBuilder(wing_ui)

# 测试数据
versions = {
    "jdk8": "JDK 8 (LTS)",
    "jdk11": ("JDK 11 (LTS)", "recommend"),
    "jdk17": ("JDK 17 (LTS)", "important"),
}

options = {
    "opt1": "安装组件 A",
    "opt2": "安装组件 B",
    "opt3": "安装组件 C",
}

print("=== 开始测试 BaseConfigureFlowBuilder 构建者模式 (标准参数版) ===")


def mycustom(x):
    print("aaa")
    print(x.data())


# 链式构建流程
config_data = (
    builder
    .pause()
    .message(
        title="安装向导",
        text="欢迎使用 WingEnv 安装程序。我们将通过一系列步骤收集您的安装配置。"
    )
    .input_text(
        key="jdk_path",
        title="JDK 路径",
        text="请输入 JDK 安装路径：",
        default="C:\\Java\\jdk-17",
        ok_text="下一步"
    )
    .select_single_option(
        key="version",
        config=versions,
        title="选择 JDK 版本",
        text="请选择您要安装的 JDK 版本：",
        ok_text="下一步",
        cancel_text="返回"
    )
    .select_multiple_options(
        key="components",
        config=options,
        title="选择组件",
        text="请选择需要额外安装的组件：",
        ok_text="下一步"
    )
    .yes_no(
        key="agree",
        title="协议确认",
        text="您同意 WingEnv 用户许可协议吗？",
        yes_text="同意",
        no_text="拒绝"
    )
    .custom(lambda b: print(f"[中间数据校验]: 当前已收集 {len(b.data())} 项配置"))
    .button(
        key="install_mode",
        title="安装模式",
        text="请选择安装模式：",
        buttons=[("标准安装", "standard"), ("最小安装", "minimal"), ("自定义", "custom")]
    ).custom( callback=mycustom)

    .data()  # 最终生成配置字典
)

print("\n=== 最终收集到的配置数据 ===")
import json

print(json.dumps(config_data, indent=4, ensure_ascii=False))

print("\n测试完成！")
