from install.retrieval_flow_builder import JDKRetrievalFlowBuilder, Note, MavenRetrievalFlowBuilder, Select, \
    MinicondaRetrievalFlowBuilder
from loader import StyleLoader
from wing_ui import WingUI

from install import wing_dialog_selector


# 4. Maven 示例
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