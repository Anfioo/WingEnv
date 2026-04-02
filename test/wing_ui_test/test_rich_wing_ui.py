from sys import path
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
path.insert(0, str(project_root))

from wing_ui.rich_wing_ui import RichWingUI
from loader.style_loader import StyleLoader
from rich.text import Text
import time

# # 创建样式加载器和RichWingUI实例
style_loader = StyleLoader()
rich_ui = RichWingUI(style_loader)

# print("=== RichWingUI 测试开始 ===\n")
#
# # 测试1: print_dict_as_table
# print("测试1: 字典转表格")
# rich_ui.print_dict_as_table(
#     data={
#         "姓名": "张三",
#         "年龄": 25,
#         "城市": "北京",
#         "职业": "工程师"
#     },
#     title="用户信息",
#     show_index=True
# )
# print()
#
# # 测试2: print_list_as_table
# print("测试2: 列表转表格")
# rich_ui.print_list_as_table(
#     data=["项目A", "项目B", "项目C", "项目D", "项目E"],
#     title="项目列表",
#     show_index=True
# )
# print()
#
# # 测试3: print_table (字典列表)
# print("测试3: 字典列表表格")
# rich_ui.print_table(
#     data=[
#         {"姓名": "张三", "年龄": 25, "城市": "北京"},
#         {"姓名": "李四", "年龄": 30, "城市": "上海"},
#         {"姓名": "王五", "年龄": 28, "城市": "广州"},
#         {"姓名": "赵六", "年龄": 35, "城市": "深圳"}
#     ],
#     columns=["姓名", "年龄", "城市"],
#     title="用户列表",
#     show_index=True
# )
# print()
#
# # 测试4: print_table (二维列表)
# print("测试4: 二维列表表格")
# rich_ui.print_table(
#     data=[
#         ["产品A", 100, 200],
#         ["产品B", 150, 300],
#         ["产品C", 200, 400]
#     ],
#     columns=["产品名称", "价格", "库存"],
#     title="产品信息",
#     show_index=True
# )
# print()
#
# # 测试5: print_panel
# print("测试5: 面板展示")
# rich_ui.print_panel(
#     content="这是一个面板内容，用于展示重要信息。",
#     title="信息面板"
# )
# print()
#
# # 测试6: print_tree
# print("测试6: 树形结构展示")
# rich_ui.print_tree(
#     data={
#         "公司": {
#             "技术部": {
#                 "前端组": ["张三", "李四"],
#                 "后端组": ["王五", "赵六"]
#             },
#             "产品部": {
#                 "产品经理": "钱七",
#                 "UI设计师": "孙八"
#             },
#             "市场部": {
#                 "销售": "周九",
#                 "运营": "吴十"
#             }
#         }
#     },
#     title="公司组织架构"
# )
# print()
#
# # 测试7: print_columns
# print("测试7: 多列展示")
# rich_ui.print_columns(
#     items=[
#         "第一列内容",
#         "第二列内容",
#         "第三列内容"
#     ],
#     title="三列布局"
# )
# print()
#
# # 测试8: print_info
# print("测试8: 信息消息")
# rich_ui.print_info("这是一条普通信息消息。")
# print()
#
# # 测试9: print_warning
# print("测试9: 警告消息")
# rich_ui.print_warning("这是一条警告消息，请注意检查！")
# print()
#
# # 测试10: print_error
# print("测试10: 错误消息")
# rich_ui.print_error("这是一条错误消息，操作失败！")
# print()
#
# # 测试11: print_success
# print("测试11: 成功消息")
# rich_ui.print_success("操作成功完成！")
# print()
#
# # 测试12: print_list (编号)
# print("测试12: 编号列表")
# rich_ui.print_list(
#     items=["任务1", "任务2", "任务3", "任务4"],
#     title="待办任务",
#     numbered=True
# )
# print()
#
# # 测试13: print_list (项目符号)
# print("测试13: 项目符号列表")
# rich_ui.print_list(
#     items=["特性1", "特性2", "特性3"],
#     title="产品特性",
#     numbered=False,
#     bullet="★"
# )
# print()
#
# # 测试14: print_key_value
# print("测试14: 键值对展示")
# rich_ui.print_key_value(
#     data={
#         "版本": "1.0.0",
#         "作者": "Anfioo",
#         "许可证": "MIT",
#         "状态": "活跃"
#     },
#     title="项目信息"
# )
# print()
#
# # 测试15: print_aligned
# print("测试15: 对齐文本")
# rich_ui.print_aligned("居中对齐的标题文本", align="center")
# rich_ui.print_aligned("左对齐的文本", align="left")
# rich_ui.print_aligned("右对齐的文本", align="right")
# print()
#
# # 测试16: print_rule
# print("测试16: 分隔线")
# rich_ui.print_rule("章节一", style="cyan")
# rich_ui.print_rule("章节二", style="green")
# rich_ui.print_rule("章节三", style="magenta")
# print()
#
# # 测试17: 综合展示
# print("测试17: 综合展示")
# rich_ui.print_dict_as_table(
#     data={
#         "测试项目": "RichWingUI综合测试",
#         "测试时间": "2026-02-14",
#         "测试状态": "通过",
#         "测试覆盖率": "100%"
#     },
#     title="测试报告"
# )
# print()
#
# # 测试18: 嵌套数据结构
# print("测试18: 复杂嵌套数据")
# rich_ui.print_tree(
#     data={
#         "配置": {
#             "数据库": {
#                 "主机": "localhost",
#                 "端口": 3306,
#                 "用户": "admin"
#             },
#             "缓存": {
#                 "类型": "Redis",
#                 "超时": 3600
#             },
#             "日志": {
#                 "级别": "INFO",
#                 "路径": "/var/log/app.log"
#             }
#         }
#     },
#     title="系统配置"
# )
# print()
#
# # 测试19: 表格样式
# print("测试19: 大数据量表格")
# large_data = [
#     {"ID": i, "名称": f"项目{i}", "状态": "完成" if i % 2 == 0 else "进行中"}
#     for i in range(1, 11)
# ]
# rich_ui.print_table(
#     data=large_data,
#     title="项目状态表",
#     show_index=True
# )
# print()
#
# # 测试20: 多面板展示
# print("测试20: 多面板展示")
# panel1_content = Text("面板1内容", style="bold blue")
# panel2_content = Text("面板2内容", style="bold green")
# panel3_content = Text("面板3内容", style="bold yellow")
#
# rich_ui.print_columns(
#     items=[
#         panel1_content,
#         panel2_content,
#         panel3_content
#     ],
#     title="三个面板并排展示"
# )
# print()
#
# print("=== 所有测试完成！===")
# print(f"\nRichWingUI 提供了 {len([m for m in dir(rich_ui) if m.startswith('print_')])} 个打印方法")
# print(f"样式加载器: {rich_ui.get_style_loader().__class__.__name__}")
from wing_utils.system import EnvManager, UserEnvRunner
from wing_utils.system.env.path_env_utils import PathEnvUtils

user_manager = EnvManager(UserEnvRunner())
to_list = PathEnvUtils.path_str_to_list(user_manager.get("PATH")["value"])
path_print_list = [ [p] for p in to_list]
print(path_print_list)

rich_ui.print_table(
    data=path_print_list,
    columns=["PATH列表值"],
    title="PATH环境变量预览",
    show_index=True
)