from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.validation import Validator, ValidationError


class ListCompleter(Completer):
    def __init__(self, options):
        self.options = options

    def get_completions(self, document, complete_event):
        word = document.text_before_cursor.lower()
        for option in self.options:
            if option.lower().startswith(word):
                yield Completion(option, start_position=-len(word))


class Selector:
    """
    基础选择器类，使用 prompt_toolkit 实现简单的列表选择器功能。
    支持传入选项列表，调用 run() 返回用户选择结果。
    """

    def __init__(self, options, prompt_text="请选择一个选项: "):
        if not options:
            raise ValueError("options 不能为空列表")
        self.options = options
        self.prompt_text = prompt_text

    def run(self):
        """
        运行选择器，提示用户输入选项名称，支持自动补全。
        返回用户选择的字符串。
        """
        completer = ListCompleter(self.options)

        # 验证输入必须是列表中的一个
        validator = Validator.from_callable(
            lambda x: x in self.options,
            error_message="请输入有效的选项名称",
            move_cursor_to_end=True,
        )
        while True:
            try:
                result = prompt(
                    self.prompt_text,
                    completer=completer,
                    complete_style=CompleteStyle.READLINE_LIKE,
                    validator=validator,
                    validate_while_typing=False,
                )
                return result
            except ValidationError as e:
                print(f"输入错误: {e}")


# 测试
if __name__ == "__main__":
    options = ["apple", "banana", "orange", "pear"]
    selector = Selector(options)
    choice = selector.run()
    print(f"你选择了: {choice}")
