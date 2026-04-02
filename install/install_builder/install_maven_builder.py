from install.retrieval_flow_builder import JDKRetrievalFlowBuilder, Note, MavenRetrievalFlowBuilder, Select
from loader import StyleLoader
from wing_ui import WingUI
from install import wing_dialog_selector



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
if maven_result: print(f"✅ JDK: {maven_result}")
