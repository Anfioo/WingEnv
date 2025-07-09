from prompt_toolkit import HTML

from wing_ui.selection_dialogs import select_single_option_ui

# 示例 1：使用标签 + 模式
config = {
    "eggs": ("鸡蛋", "important"),
    "potatoes": ("土豆", "ignore"),
    "coffee": ("咖啡", "normal")
}
result = select_single_option_ui(config, "早餐选择", "请选择您的早餐：")
print(result)
# 示例 2：使用 HTML
config = {
    "apple": HTML('<style fg="red">苹果</style>'),
    "banana": HTML('<b><style fg="yellow">香蕉</style></b>')
}
result = select_single_option_ui(config, HTML("🍓 水果选择"), HTML("请选择您喜欢的水果："))
print(result)
# 示例 3：使用纯字符串
config = {
    "milk": "牛奶",
    "tea": "茶",
    "juice": "果汁"
}
result = select_single_option_ui(config, "饮品选择", HTML('<b>请选择饮品：</b>\n<i>aaa</i>'))
print(result)
