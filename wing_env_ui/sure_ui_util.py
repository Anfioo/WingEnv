from prompt_toolkit.shortcuts import yes_no_dialog, message_dialog, input_dialog

def confirm_action_ui(title: str = "确认操作",
                   message: str = "你确定要执行此操作吗？",
                   yes_text: str = "确认",
                   no_text: str = "取消") -> bool:
    """显示确认对话框，返回用户是否确认（True/False）"""
    return yes_no_dialog(
        title=title,
        text=message,
        yes_text=yes_text,
        no_text=no_text
    ).run()

def show_message_ui(title: str = "消息",
                message: str = "操作完成") -> None:
    """显示简单消息对话框"""
    message_dialog(
        title=title,
        text=message
    ).run()


# 使用示例
if __name__ == "__main__":
    # 确认操作
    if confirm_action_ui("删除文件", "确定要删除此文件吗？"):
        show_message_ui("操作结果", "文件已删除")
    else:
        show_message_ui("操作结果", "已取消删除")

