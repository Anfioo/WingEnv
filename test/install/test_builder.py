import sys
import os

from install.retrieval_flow_builder import Note, Select
from install.retrieval_flow_builder import CMakeRetrievalFlowBuilder
from install.retrieval_flow_builder import JDKRetrievalFlowBuilder
from install.retrieval_flow_builder import GoRetrievalFlowBuilder
from install.retrieval_flow_builder import MavenRetrievalFlowBuilder
from install.retrieval_flow_builder import MinicondaRetrievalFlowBuilder
from install.retrieval_flow_builder import NPMRetrievalFlowBuilder

# 将当前目录添加到路径，确保可以导入 install 模块
sys.path.append(os.getcwd())

from wing_ui.dialog_ui import WingUI
from loader.style_loader import StyleLoader

# 初始化真实的 WingUI
style_loader = StyleLoader()
wing_ui = WingUI(style_loader)


def wing_dialog_selector(prompt, config):
    """
    使用 WingUI 的单选对话框作为选择器
    """
    return wing_ui.select_single_option_ui(
        config=config,
        title=prompt,
        text="请从下方列表中选择一项："
    )


def run_demo():
    print("🚀 启动全能构建者模式 Demo (使用 WingUI)...")
    #
    # 1. JDK 示例
    print("\n" + "=" * 40)
    print("[场景 1] JDK 构建者模式")
    jdk_result = (JDKRetrievalFlowBuilder.default(os="windows", arch="x86_64", selector=wing_dialog_selector)
                  .fetch_data()
                  .vendor().deal(
        block=["IBM*", "SAP*"],
        note=[
            Note("Alibaba", "recommend"),
            Note("JetBrains", "important"),
            Note("Oracle", "warn")
        ]
    )
                  .select_ui()
                  .version().deal(
        block=["1.8*", "11*"]
    )
                  .select_ui()
                  .data()
                  )
    if jdk_result: print(f"✅ JDK: {jdk_result}")

    # 2. NPM 示例
    print("\n" + "=" * 40)
    print("[场景 2] NPM 构建者模式")
    npm_result = (NPMRetrievalFlowBuilder.default(selector=wing_dialog_selector)
                  .mirror().deal(default=Select.Option("阿里镜像 (npmmirror)"))
                  .select_ui()
                  .fetch_data()
                  .version().deal(note=[Note("LTS", "recommend")])
                  .select_ui()
                  .arch().deal(default=Select.Option("win-x64-zip"))
                  .select_ui()
                  .data()
                  )
    if npm_result: print(f"✅ NPM: {npm_result.get('filename')}")

    # 3. Go 示例
    print("\n" + "=" * 40)
    print("[场景 3] Go 构建者模式")
    go_result = (GoRetrievalFlowBuilder.default(selector=wing_dialog_selector)
                 .fetch_data()
                 .version().select_ui()
                 .os().deal(default=Select.Option("windows"))
                 .select_ui()
                 .arch().deal(default=Select.Option("amd64"))
                 .select_ui()
                 .kind().select_ui()
                 .data()
                 )
    if go_result: print(f"✅ Go: {go_result.get('filename')}")

    # 4. Maven 示例
    print("\n" + "=" * 40)
    print("[场景 4] Maven 构建者模式")
    maven_result = (MavenRetrievalFlowBuilder.default(selector=wing_dialog_selector)
                    .fetch_data()
                    .version().select_ui()
                    .format().deal(default=Select.Option("bin.zip"))
                    .select_ui()
                    .data()
                    )
    if maven_result: print(f"✅ Maven: {maven_result.get('filename')}")

    # 5. CMake 示例
    print("\n" + "=" * 40)
    print("[场景 5] CMake 构建者模式")
    cmake_result = (CMakeRetrievalFlowBuilder.default(selector=wing_dialog_selector)
                    .fetch_main_data()
                    .version_dir().select_ui()
                    .fetch_version_files()
                    .file().deal(
        block=["*linux*", "*Darwin*", "*macos*", "*win32*", "*Linux*", "*files*", "*SHA-256*", "*rc*", "*msi*"],
        note=[Note("windows-x86_64.zip", "recommend")])
                    .select_ui()
                    .data()
                    )
    if cmake_result: print(f"✅ CMake: {cmake_result.get('filename')}")

    # 6. Miniconda 示例
    print("\n" + "=" * 40)
    print("[场景 6] Miniconda 构建者模式")
    conda_result = (MinicondaRetrievalFlowBuilder.default(selector=wing_dialog_selector)
                    .fetch_data()
                    .os().deal(default=Select.Option("Windows"))
                    .select_ui()
                    .arch().deal(default=Select.Option("x86_64"))
                    .select_ui()
                    .format().select_ui()
                    .data()
                    )
    if conda_result: print(f"✅ Miniconda: {conda_result.get('filename')}")


if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        import traceback

        traceback.print_exc()
    except KeyboardInterrupt:
        print("\n👋 已退出")
