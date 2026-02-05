import winreg
import ctypes
import os
from wing_utils.system.env.admin_utils import AdminUtils

class EnvRunner:
    """环境变量操作基类"""
    
    TYPE_MAP = {
        winreg.REG_SZ: 'REG_SZ',
        winreg.REG_EXPAND_SZ: 'REG_EXPAND_SZ',
        winreg.REG_MULTI_SZ: 'REG_MULTI_SZ'
    }
    
    REV_TYPE_MAP = {v: k for k, v in TYPE_MAP.items()}

    def __init__(self, hkey, subkey):
        self.hkey = hkey
        self.subkey = subkey

    def _open_key(self, access=winreg.KEY_READ):
        try:
            return winreg.OpenKey(self.hkey, self.subkey, 0, access)
        except WindowsError as e:
            print(f"无法打开注册表项: {e}")
            return None

    def get_all(self):
        """获取所有环境变量"""
        env_vars = {}
        key = self._open_key(winreg.KEY_READ)
        if not key:
            return env_vars

        try:
            i = 0
            while True:
                name, value, reg_type = winreg.EnumValue(key, i)
                type_str = self.TYPE_MAP.get(reg_type, f"REG_{reg_type}")
                env_vars[name] = {
                    'value': value,
                    'type': type_str
                }
                i += 1
        except WindowsError:
            pass
        finally:
            winreg.CloseKey(key)
        return env_vars

    def get(self, name):
        """获取特定环境变量"""
        key = self._open_key(winreg.KEY_READ)
        if not key:
            return None

        try:
            value, reg_type = winreg.QueryValueEx(key, name)
            type_str = self.TYPE_MAP.get(reg_type, f"REG_{reg_type}")
            return {
                'key': name,
                'value': value,
                'type': type_str
            }
        except WindowsError:
            return None
        finally:
            winreg.CloseKey(key)

    def set(self, name, value, reg_type_str='REG_SZ', notify=True):
        """设置或更新环境变量"""
        key = self._open_key(winreg.KEY_WRITE)
        if not key:
            return False

        try:
            reg_type = self.REV_TYPE_MAP.get(reg_type_str, winreg.REG_SZ)
            winreg.SetValueEx(key, name, 0, reg_type, value)
            if notify:
                self.notify_system()
            return True
        except WindowsError as e:
            print(f"设置环境变量 {name} 失败: {e}")
            return False
        finally:
            winreg.CloseKey(key)

    def delete(self, name, notify=True):
        """删除环境变量"""
        key = self._open_key(winreg.KEY_WRITE)
        if not key:
            return False

        try:
            winreg.DeleteValue(key, name)
            if notify:
                self.notify_system()
            return True
        except WindowsError as e:
            print(f"删除环境变量 {name} 失败: {e}")
            return False
        finally:
            winreg.CloseKey(key)

    def notify_system(self):
        """通知系统环境变量已更改"""
        try:
            # HWND_BROADCAST = 0xFFFF, WM_SETTINGCHANGE = 0x001A
            ctypes.windll.user32.SendMessageTimeoutW(
                0xFFFF, 0x001A, 0, "Environment", 0x0002, 1000, ctypes.byref(ctypes.c_long())
            )
        except:
            pass


class UserEnvRunner(EnvRunner):
    """用户级环境变量操作 (HKCU)"""
    def __init__(self):
        super().__init__(winreg.HKEY_CURRENT_USER, r"Environment")


class SystemEnvRunner(EnvRunner):
    """系统级环境变量操作 (HKLM)"""
    def __init__(self):
        super().__init__(
            winreg.HKEY_LOCAL_MACHINE, 
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        )
    
    

    def set(self, name, value, reg_type_str='REG_SZ', notify=True):
        if not AdminUtils.is_admin():
            print("错误: 修改系统环境变量需要管理员权限")
            return False
        return super().set(name, value, reg_type_str, notify=notify)

    def delete(self, name, notify=True):
        if not AdminUtils.is_admin():
            print("错误: 删除系统环境变量需要管理员权限")
            return False
        return super().delete(name, notify=notify)
