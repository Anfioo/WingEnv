from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from wing_env_install.java_install.java_config_utils import JavaConfigManager
from wing_env_install.java_install.java_set_env import set_user_java_env
import re


class JavaCompleter(Completer):
    def __init__(self, mgr):
        self.mgr = mgr
        self.commands = ['ls', 'set','exit', 'quit']

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lstrip()
        parts = text.split()

        if len(parts) == 0:
            # 输入为空时补全所有命令
            for cmd in self.commands:
                yield Completion(cmd, start_position=0)
        elif len(parts) == 1:
            # 补全命令
            for cmd in self.commands:
                if cmd.startswith(parts[0]):
                    yield Completion(cmd, start_position=-len(parts[0]))
        elif len(parts) == 2 and parts[0] == 'set':
            # 补全版本号，提取所有版本号数字部分
            versions = []
            for k in self.mgr.get_java_path().keys():
                m = re.search(r'\d+', k)
                if m:
                    versions.append(m.group(0))
            versions = set(versions)  # 去重
            for v in versions:
                if v.startswith(parts[1]):
                    yield Completion(v, start_position=-len(parts[1]))


def list_java_versions(mgr):
    configs = mgr.get_java_path()
    if not configs:
        print("没有已配置的 Java 版本。")
        return
    print("已配置的 Java 版本:")
    for version, path in configs.items():
        print(f"  Java {version} => {path}")


def set_java_version(mgr, version_short):
    configs = mgr.get_java_path()
    matched_key = None
    for k in configs:
        if version_short in k:
            matched_key = k
            break

    if not matched_key:
        print(f"错误: Java 版本 {version_short} 未找到，请先安装或添加。")
        return

    path = configs[matched_key]
    set_user_java_env(path)
    print(f"系统环境变量已更新，当前 Java 版本设为 {version_short}，路径：{path}")




def java_env_set_main():
    mgr = JavaConfigManager()
    completer = JavaCompleter(mgr)
    session = PromptSession('java> ', completer=completer)

    while True:
        try:
            user_input = session.prompt()
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

        if not user_input.strip():
            continue

        parts = user_input.strip().split()
        cmd = parts[0]

        if cmd == 'ls':
            list_java_versions(mgr)
        elif cmd == 'set':
            if len(parts) < 2:
                print("请指定要设置的 Java 版本号，例如：set 8")
                continue
            set_java_version(mgr, parts[1])
        elif cmd in ('exit', 'quit'):
            break
        else:
            print("未知命令，仅支持 ls、set <version>、v、exit、quit")

