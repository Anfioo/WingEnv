import sys
import winreg
import ctypes
import subprocess
import time



class WinEnvManager:
    USER_ENV_PATH = r"Environment"

    def __init__(self):
        # 只操作当前用户环境变量，无需管理员权限
        self.hive = winreg.HKEY_CURRENT_USER
        self.path = self.USER_ENV_PATH
        self.scope = "用户"

        self._set_vars = {}
        self._paths_to_add = set()

    def set_variable(self, key: str, value: str):
        self._set_vars[key] = value
        return self

    def add_path(self, value: str):
        if value:
            self._paths_to_add.add(value)
        return self

    def execute(self):
        try:
            reg_key = winreg.OpenKey(self.hive, self.path, 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
        except PermissionError:
            print(f"❌ 权限不足，无法修改{self.scope}环境变量")
            return

        # 设置普通变量
        for key, value in self._set_vars.items():
            try:
                winreg.SetValueEx(reg_key, key, 0, winreg.REG_EXPAND_SZ, value)
                print(f"✅（{self.scope}）已设置 {key} = {value}")
            except Exception as e:
                print(f"❌ 设置 {key} 失败: {e}")

        # 更新 PATH
        try:
            current_path, _ = winreg.QueryValueEx(reg_key, "Path")
        except FileNotFoundError:
            current_path = ""

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

    @staticmethod
    def restart_explorer():
        print("🛑 正在关闭资源管理器...")
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], shell=True)

        # 等待一会避免重启失败
        time.sleep(1)

        print("🚀 正在重新启动资源管理器...")
        subprocess.Popen(["explorer.exe"], shell=True)

        print("✅ Explorer 已重启，环境变量刷新应立即可见")


if __name__ == "__main__":
    user_env = WinEnvManager()
    user_env.set_variable("JAVA_HOME", r"C:\Apps\JDK\jdk-17.0.12") \
        .add_path(r"%JAVA_HOME%\bin") \
        .add_path(r"%JAVA_HOME%\jre\bin") \
        .execute()

    input("按任意键退出...")
