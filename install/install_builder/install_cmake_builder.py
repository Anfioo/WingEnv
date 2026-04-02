from install import wing_dialog_selector, BaseConfigureFlowBuilder
from install.retrieval_flow_builder import Note, CMakeRetrievalFlowBuilder

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

BaseConfigureFlowBuilder.message()