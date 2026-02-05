import json
import os
from datetime import datetime

from wing_utils.system.env.runnner.runner import SystemEnvRunner
from wing_utils.system.env.admin_utils import AdminUtils


class EnvManager:
    """环境变量管理类"""
    
    def __init__(self, runner):
        """
        初始化管理器
        :param runner: EnvRunner 的实例 (UserEnvRunner 或 SystemEnvRunner)
        """
        self.runner = runner

    def _check_permission(self):
        """内部权限检查"""
        if isinstance(self.runner, SystemEnvRunner):
            if not AdminUtils.is_admin():
                print("警告: 当前操作需要管理员权限，系统环境变量修改将被跳过。")
                return False
        return True

    def backup(self, file_path=None):
        """
        备份当前 runner 对应的环境变量到 JSON 文件 (与 backup.py 格式对齐)
        """
        env_vars = self.runner.get_all()
        scope = "system" if isinstance(self.runner, SystemEnvRunner) else "user"
        
        # 模拟 backup.py 中的完整路径
        if scope == "user":
            full_reg_path = r"HKEY_CURRENT_USER\Environment"
        else:
            full_reg_path = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"

        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"{scope}_env_backup_{timestamp}.json"
        
        # 构建与 backup.py 一致的数据结构
        backup_data = {
            'backup_time': datetime.now().isoformat(),
            'backup_scope': scope,
            'backup_type': full_reg_path,
            'environment_variables': env_vars,
            'total_count': len(env_vars)
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=4, ensure_ascii=False)
            print(f"✅ {'用户' if scope == 'user' else '系统'}环境变量备份成功！")
            print(f"📁 备份文件: {os.path.abspath(file_path)}")
            print(f"📊 环境变量数量: {len(env_vars)}")
            print()
            
            # 对齐 backup.py 的列表显示
            print("已备份的环境变量:")
            print("-" * 80)
            for name, data in sorted(env_vars.items()):
                value_preview = str(data['value'])
                if len(value_preview) > 60:
                    value_preview = value_preview[:57] + "..."
                type_display = data['type'].replace('REG_', '')
                print(f"  {name:<25} [{type_display:<8}] = {value_preview}")
            print("-" * 80)
            
            return file_path
        except Exception as e:
            print(f"❌ 写入备份文件时出错: {e}")
            return None

    def restore(self, file_path):
        """
        从 JSON 文件恢复环境变量 (兼容 backup.py 格式)
        """
        if not self._check_permission():
            return False

        if not os.path.exists(file_path):
            print(f"错误: 备份文件 {file_path} 不存在")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 兼容处理：如果是 backup.py 格式，提取 environment_variables
            if isinstance(data, dict) and 'environment_variables' in data:
                env_vars = data['environment_variables']
                print(f"📅 备份时间: {data.get('backup_time', '未知')}")
                print(f"� 备份类型: {'用户' if data.get('backup_scope') == 'user' else '系统'}环境变量")
                print(f"�📊 变量数量: {len(env_vars)}")
                
                # 对齐 backup.py 的显示
                print("\n将要恢复的环境变量:")
                print("-" * 80)
                for name, info in sorted(env_vars.items()):
                    value_preview = str(info['value'])
                    if len(value_preview) > 50:
                        value_preview = value_preview[:47] + "..."
                    print(f"  {name:<20} = {value_preview}")
                print("-" * 80)
            else:
                # 兼容旧的直接字典格式
                env_vars = data
            
            success_count = 0
            total_count = len(env_vars)
            
            print(f"正在恢复环境变量...")
            for name, info in env_vars.items():
                value = info.get('value')
                reg_type = info.get('type', 'REG_SZ')
                # 恢复时关闭逐个通知，以提高速度
                if self.runner.set(name, value, reg_type, notify=False):
                    success_count += 1
            
            # 循环结束后统一通知系统一次
            self.runner.notify_system()
            
            print(f"✅ 恢复完成！成功恢复了 {success_count}/{total_count} 个环境变量")
            return success_count == total_count
        except Exception as e:
            print(f"❌ 恢复失败: {e}")
            return False

    def add(self, name, value, reg_type='REG_SZ'):
        """添加环境变量"""
        if not self._check_permission():
            return False
        return self.runner.set(name, value, reg_type)

    def update(self, name, value, reg_type='REG_SZ'):
        """更新环境变量"""
        if not self._check_permission():
            return False
        return self.runner.set(name, value, reg_type)

    def delete(self, name):
        """删除环境变量"""
        if not self._check_permission():
            return False
        return self.runner.delete(name)

    def get_all(self):
        """获取所有环境变量"""
        return self.runner.get_all()

    def get(self, name):
        """获取单个环境变量"""
        return self.runner.get(name)
