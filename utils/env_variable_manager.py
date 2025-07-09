import os
import sys
import winreg
import ctypes


class WinEnvManager:
    USER_ENV_PATH = r"Environment"
    SYSTEM_ENV_PATH = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"

    def __init__(self, user_admin=False):
        """
        :param user_admin: bool
            False 默认操作当前用户环境变量（无管理员权限要求）
            True 操作系统环境变量（需要管理员权限）
        """
        self.user_admin = user_admin
        self.hive = winreg.HKEY_CURRENT_USER if not user_admin else winreg.HKEY_LOCAL_MACHINE
        self.path = self.USER_ENV_PATH if not user_admin else self.SYSTEM_ENV_PATH
        self.scope = "用户" if not user_admin else "系统"

        # 缓存待执行操作
        self._set_vars = {}
        self._paths_to_add = set()

    def set_variable(self, key: str, value: str):
        self._set_vars[key] = value
        return self  # 支持链式调用

    def add_path(self, value: str):
        if value:
            self._paths_to_add.add(value)
        return self  # 支持链式调用

    def execute(self):
        if self.user_admin and not self._check_admin_and_maybe_elevate():
            return

        try:
            reg_key = winreg.OpenKey(self.hive, self.path, 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
        except PermissionError:
            print(f"❌ 权限不足，无法修改{self.scope}环境变量")
            return

        # 先设置普通变量
        for key, value in self._set_vars.items():
            try:
                winreg.SetValueEx(reg_key, key, 0, winreg.REG_EXPAND_SZ, value)
                print(f"✅（{self.scope}）已设置 {key} = {value}")
            except Exception as e:
                print(f"❌ 设置 {key} 失败: {e}")

        # 处理PATH变量，先获取当前PATH
        try:
            current_path, _ = winreg.QueryValueEx(reg_key, "Path")
        except FileNotFoundError:
            current_path = ""

        # 将新增路径添加到PATH尾部，避免重复
        paths_lower = {p.lower() for p in current_path.split(';') if p}
        new_paths = [p for p in self._paths_to_add if p.lower() not in paths_lower]

        if new_paths:
            updated_path = current_path
            for p in new_paths:
                updated_path = f"{updated_path};{p}" if updated_path else p
            try:
                winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, updated_path)
                print(f"✅（{self.scope}）已添加路径到 PATH: {new_paths}")
            except Exception as e:
                print(f"❌ 更新 PATH 失败: {e}")
        else:
            if self._paths_to_add:
                print(f"ℹ️ PATH 已包含所有待添加路径，无需更新")

        winreg.CloseKey(reg_key)
        self.broadcast_env_change()

    def _check_admin_and_maybe_elevate(self):
        if self.is_admin():
            return True

        print("⚠️ 当前无管理员权限，操作系统环境变量需要管理员权限。")
        ans = input("是否尝试以管理员权限重新启动脚本？(Y/N): ").strip().lower()
        if ans == "y":
            if self.run_as_admin():
                print("脚本已以管理员权限重新启动，请关闭当前窗口。")
                sys.exit(0)
            else:
                print("❌ 提权失败，请手动以管理员身份运行程序。")
                return False
        else:
            print("放弃提权，操作可能失败。")
            return False

    @staticmethod
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    @staticmethod
    def run_as_admin():
        params = ' '.join([f'"{arg}"' for arg in sys.argv])
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1)
            return True
        except Exception as e:
            print(f"❌ 无法以管理员权限重启: {e}")
            return False

    @staticmethod
    def broadcast_env_change():
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        SMTO_ABORTIFHUNG = 0x0002
        result = ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(ctypes.c_ulong())
        )
        if result:
            print("🔄 已通知系统刷新环境变量")
        else:
            print("⚠️ 无法通知系统刷新环境变量（可能不影响）")


# 用法示例
user_env = WinEnvManager(user_admin=False)
user_env.set_variable("JAVA_HOME", r"C:\Apps\JDK\jdk-17.0.12") \
    .add_path(r"%JAVA_HOME%\bin") \
    .add_path(r"%JAVA_HOME%\jre\bin") \
    .execute()

system_env = WinEnvManager(user_admin=True)
system_env.set_variable("JAVA_HOME", r"C:\Apps\JDK\jdk-17.0.12") \
    .add_path(r"%JAVA_HOME%\bin") \
    .add_path(r"%JAVA_HOME%\jre\bin") \
    .execute()

input("按任意键退出...")
