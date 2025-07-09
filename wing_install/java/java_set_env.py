import os
import winreg


def set_user_java_env(java_home_path: str):
    if not os.path.isdir(java_home_path):
        print(f"❌ 无效的 JAVA_HOME 路径: {java_home_path}")
        return

    try:
        # 打开用户环境变量注册表键
        reg_path = r"Environment"
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)

        # 设置 JAVA_HOME
        winreg.SetValueEx(reg_key, "JAVA_HOME", 0, winreg.REG_EXPAND_SZ, java_home_path)
        print(f"✅ 已设置 JAVA_HOME = {java_home_path}")

        # 获取当前 PATH
        try:
            current_path, _ = winreg.QueryValueEx(reg_key, "Path")
        except FileNotFoundError:
            current_path = ""

        java_add_bin_path = r"%JAVA_HOME%\bin"

        # 如果 PATH 中没有 %JAVA_HOME%\bin 就添加进去
        if java_add_bin_path.lower() not in current_path.lower():
            new_path = f"{java_add_bin_path};{current_path}" if current_path else java_add_bin_path
            winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"✅ 已将 {java_add_bin_path} 添加到 PATH")
        else:
            print("ℹ️  PATH 中已包含 %JAVA_HOME%\\bin，无需添加")

        java_add_bin_path = r"%JAVA_HOME%\jre\bin"

        # 如果 PATH 中没有 %JAVA_HOME%\bin 就添加进去
        if java_add_bin_path.lower() not in current_path.lower():
            new_path = f"{java_add_bin_path};{current_path}" if current_path else java_add_bin_path
            winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"✅ 已将 {java_add_bin_path} 添加到 PATH")
        else:
            print("ℹ️  PATH 中已包含 %JAVA_HOME%\\jre\\bin，无需添加")

        winreg.CloseKey(reg_key)

        print("\n⚠️  修改后的环境变量将在你 重新启动命令行或资源管理器 后生效")

    except PermissionError:
        print("❌ 权限不足，无法写入用户环境变量。")

    broadcast_env_change()


import ctypes


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

