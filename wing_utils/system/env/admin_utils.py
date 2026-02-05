import ctypes
import sys
from typing import List


class AdminUtils:
    @staticmethod
    def is_admin() -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    @staticmethod
    def relaunch_as_admin(extra_args: List[str] | None = None):
        """
        以管理员权限重新启动当前脚本，并附加额外参数
        :param extra_args: 需要额外传递的参数列表，例如 ["--elevated", "--from=install_driver"]
        """
        if extra_args is None:
            extra_args = []

        # 当前脚本
        params = [f'"{sys.argv[0]}"']

        # 原始参数
        print(sys.argv)
        params += [f'"{arg}"' for arg in sys.argv[1:]]

        # 额外参数（标记用）
        params += [f'"{arg}"' for arg in extra_args]

        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            " ".join(params),
            None,
            1
        )
        sys.exit(0)

    @staticmethod
    def ensure_admin(extra_args: List[str] | None = None):
        """
        如果当前不是管理员，则自动提权并退出当前进程
        """
        if not AdminUtils.is_admin():
            AdminUtils.relaunch_as_admin(extra_args)


import sys


def install_driver():
    AdminUtils.ensure_admin([
        "--elevated",
        "--from=install_driver"
    ])

    print("管理员环境，继续执行 install_driver")


if __name__ == "__main__":
    install_driver()
    print("argv =", sys.argv)
    input()

