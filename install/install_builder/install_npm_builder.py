from install.retrieval_flow_builder import JDKRetrievalFlowBuilder, Note, MavenRetrievalFlowBuilder, Select, \
    MinicondaRetrievalFlowBuilder, NPMRetrievalFlowBuilder
from loader import StyleLoader
from wing_ui import WingUI
from install import wing_dialog_selector

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