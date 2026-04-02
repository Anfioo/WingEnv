from install.retrieval_flow_builder import JDKRetrievalFlowBuilder, Note, MavenRetrievalFlowBuilder, Select, \
    GoRetrievalFlowBuilder
from loader import StyleLoader
from wing_ui import WingUI
from install import wing_dialog_selector



# 4. Maven 示例
print("\n" + "=" * 40)
print("[场景 3] Go 构建者模式")
go_result = (GoRetrievalFlowBuilder.default(selector=wing_dialog_selector)
             .fetch_data()
             .version().select_ui()
             .os().deal(default=Select.Option("windows"))
             .select_ui()
             .arch().deal(default=Select.Option("amd64"))
             .select_ui()
             .kind().deal(default=Select.Option("archive")).select_ui()
             .data()
             )
if go_result: print(f"✅ Go: {go_result}")
