import ctypes

exe_path = r"C:\Users\Anfioo\Desktop\Working\PycharmProjects\WingEnv\SystemPropertiesAdvanced.exe"

# 以管理员权限启动
ctypes.windll.shell32.ShellExecuteW(None, "runas", exe_path, None, None, 1)
