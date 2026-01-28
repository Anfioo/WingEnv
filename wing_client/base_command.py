from typing import List, Dict, Optional, Union, Callable

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import print_formatted_text as print_html


# ==========================================
# 1. 核心命令类
# ==========================================

class BaseCommand:
    def __init__(self,
                 identity: Union[str, List[str]],
                 usage: str,
                 help_text: str,
                 action_key: Optional[str] = None,
                 sub_commands: Optional[List["BaseCommand"]] = None,
                 dynamic_completer: Optional[Callable[[], List[str]]] = None
                 ):
        self.identities = [identity] if isinstance(identity, str) else identity
        self.usage = usage
        self.help_text = help_text
        self.action_key = action_key
        self.sub_commands = sub_commands or []
        self.dynamic_completer = dynamic_completer

    def match(self, cmd_name: str) -> bool:
        return cmd_name.lower() in [i.lower() for i in self.identities]

    def get_completer_dict(self) -> Optional[Dict]:
        res = {}
        for sub in self.sub_commands:
            res[sub.identities[0]] = sub.get_completer_dict()

        # 实时调用函数获取最新列表
        if self.dynamic_completer:
            items = self.dynamic_completer()
            for item in items:
                res[item] = None
        return res if res else None


class CommandRegistry:
    def __init__(self, 
                 commands: List[BaseCommand], 
                 action_map: Dict[str, Callable]
                 ):
        self.commands = commands
        self.action_map = action_map

    def execute(self, args: List[str]):
        if not args: return
        current_layer = self.commands
        last_found_action = None
        consumed_count = 0

        for i, arg in enumerate(args):
            matched = False
            for cmd in current_layer:
                if cmd.match(arg):
                    # 记录当前匹配到的动作
                    last_found_action = cmd.action_key
                    # 进入下一层子命令
                    current_layer = cmd.sub_commands
                    consumed_count = i + 1
                    matched = True
                    break

            # 如果这一层没匹配到子命令，说明剩下的都是参数
            if not matched:
                break

            # 关键：如果已经找到了子命令，通常我们不希望执行父命令的 action
            # 除非你的逻辑要求父子命令同时执行。
            # 这里我们继续循环，直到找到最深层的 action

        if last_found_action in self.action_map:
            # 确保传递的是切片后的参数列表
            remaining_args = args[consumed_count:]
            self.action_map[last_found_action](remaining_args)
        else:
            print_html(HTML(f"<ansired>❓ 未知命令: {' '.join(args)}</ansired>"))
