import sys
import re
from wing_env_install.java_install.java_config_utils import JavaConfigManager
from wing_env_install.java_install.java_env_shell import list_java_versions, set_java_version


def java_env_set_main_shell(args=None):
    """
    支持如下命令：
    we env java ls
    we env java set <version>
    """
    if args is None:
        args = sys.argv[3:]  # 默认处理 we env java 后面的参数

    mgr = JavaConfigManager()

    if not args:
        print("缺少子命令，请使用 'ls' 或 'set <version>'")
        return

    cmd = args[0]

    if cmd == 'ls':
        list_java_versions(mgr)
    elif cmd == 'set':
        if len(args) < 2:
            print("请指定要设置的 Java 版本号，例如：we env java set 8")
            return
        set_java_version(mgr, args[1])
    else:
        print(f"未知命令 '{cmd}'，仅支持 ls 和 set <version>")
