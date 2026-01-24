import wcwidth

# 1. 计算单个字符的显示宽度
print(wcwidth.wcwidth('a'))   # 输出 1（窄字符）
print(wcwidth.wcwidth('中'))  # 输出 2（宽字符）
print(wcwidth.wcwidth('🍎'))  # 输出 2（Emoji）
print(wcwidth.wcwidth('\n'))  # 输出 0（控制字符）

# 2. 计算字符串的总显示宽度
def get_display_width(text):
    """计算字符串的实际显示宽度"""
    return sum(wcwidth.wcwidth(c) for c in text)

# 测试字符串宽度
text1 = "Python 编程"
print(len(text1))             # 输出 7（字符数）
print(get_display_width(text1))  # 输出 9（Python占6 + 编程占4？不对：Python是6个窄字符=6，编程是2个宽字符=4，总计10，修正：
# 正确测试：
text2 = "abc中文123"
print(len(text2))             # 输出 7（字符数）
print(get_display_width(text2))  # 输出 11（abc=3 + 中文=4 + 123=3）

# 3. 实际应用：对齐输出（避免宽字符导致的排版乱）
items = [
    ("文件", "file.txt"),
    ("文档", "报告.pdf"),
    ("图片", "风景🍎.jpg")
]

# 用 wcwidth 计算宽度，实现对齐
for name, path in items:
    # 计算名称的显示宽度，补空格到 8 格
    name_width = get_display_width(name)
    padding = " " * (8 - name_width)
    print(f"{name}{padding} -> {path}")


import wcwidth

# 定义纯中英文混合字符串
mix_text = "Python中文123🍎"
# 1. 内置len()：只算字符个数（不管宽度）
print(f"字符个数（len）：{len(mix_text)}")  # 输出：9（P y t h o n 中 文 1 2 3 🍎？不，数一下：P(1)y(2)t(3)h(4)o(5)n(6)中(7)文(8)1(9)2(10)3(11)🍎(12) → 改：mix_text = "Py中文1"
mix_text = "Py中文1"
print(f"字符个数（len）：{len(mix_text)}")  # 输出：5（P y 中 文 1）
# 2. wcwidth计算显示宽度
total_width = sum(wcwidth.wcwidth(c) for c in mix_text)
print(f"显示宽度（wcwidth）：{total_width}")  # 输出：1+1+2+2+1=7 ✔️