from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.text_diff_viewer_ui import TextDiffViewerApp

text1 = """Hello world
This is a test
Another line
Line 4 here
Line 5 here
Line 6 here
Line 7 here
Line 8 here
Line 9 here
Line 10 here
"""

text2 = """Hello Python
This is a test
Another line changed
Line 4 here changed
Line 5 here changed
Line 6 here changed
Line 7 here changed
Line 8 here changed
Line 9 here
Line 10 here
"""

diffs = [((1, 2), (1, 2)), ((4, 8), (4, 10))]

viewer = TextDiffViewerApp(text1, text2, diffs)
print("文本对比查看器测试启动")
print("快捷键：Ctrl-N 下一差异 | Tab 切换焦点 | Ctrl-P 状态栏 | Esc 退出")
viewer.run()