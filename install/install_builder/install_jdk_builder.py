from install.retrieval_flow_builder import JDKRetrievalFlowBuilder, Note
from loader import StyleLoader
from wing_ui import WingUI
from install import wing_dialog_selector
from wing_utils.download.download_utils import DownloadUtils

jdk_result = (JDKRetrievalFlowBuilder.default(os="windows", arch="x86_64", selector=wing_dialog_selector)
              .fetch_data()
              .vendor().deal(
    note=[
        Note("Alibaba", "recommend"),
        Note("JetBrains", "important"),
    ]
)
              .select_ui()
              .version().deal()
              .select_ui()
              .data()
              )


if __name__ == "__main__":


    url = "https://download.oracle.com/graalvm/24/archive/graalvm-jdk-24.0.2_windows-x64_bin.zip"
    saved_file = DownloadUtils.download(url, "./jdks")
    print("下载完成:", saved_file)

# if jdk_result: print(f"✅ JDK: {jdk_result}")
