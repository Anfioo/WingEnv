import winreg
import json
import os
import sys
import ctypes
from datetime import datetime


def get_user_environment_variables():
    """获取当前用户的环境变量"""
    env_vars = {}

    try:
        # 打开HKEY_CURRENT_USER\Environment注册表项
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_READ
        )

        # 获取所有值
        try:
            i = 0
            while True:
                name, value, reg_type = winreg.EnumValue(key, i)

                # 处理不同类型的值
                if reg_type == winreg.REG_SZ or reg_type == winreg.REG_EXPAND_SZ:
                    env_vars[name] = {
                        'value': value,
                        'type': 'REG_SZ' if reg_type == winreg.REG_SZ else 'REG_EXPAND_SZ'
                    }
                elif reg_type == winreg.REG_MULTI_SZ:
                    env_vars[name] = {
                        'value': value,
                        'type': 'REG_MULTI_SZ'
                    }
                i += 1
        except WindowsError:
            pass

        winreg.CloseKey(key)

    except WindowsError as e:
        print(f"访问注册表时出错: {e}")
        return None

    return env_vars


def get_system_environment_variables():
    """获取系统级环境变量（HKLM）"""
    env_vars = {}

    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
            0,
            winreg.KEY_READ
        )

        i = 0
        while True:
            name, value, reg_type = winreg.EnumValue(key, i)

            if reg_type in (winreg.REG_SZ, winreg.REG_EXPAND_SZ):
                env_vars[name] = {
                    "value": value,
                    "type": "REG_SZ" if reg_type == winreg.REG_SZ else "REG_EXPAND_SZ"
                }
            elif reg_type == winreg.REG_MULTI_SZ:
                env_vars[name] = {
                    "value": value,
                    "type": "REG_MULTI_SZ"
                }
            i += 1

    except OSError:
        pass
    finally:
        try:
            winreg.CloseKey(key)
        except:
            pass

    return env_vars



def backup_environment_variables(scope='user'):
    """备份环境变量
    scope: 'user' 或 'system'
    """
    print(f"正在备份{'用户' if scope == 'user' else '系统'}环境变量...")
    print("=" * 50)

    # 获取环境变量
    if scope == 'user':
        env_vars = get_user_environment_variables()
        reg_path = r"Environment"
        full_reg_path = r"HKEY_CURRENT_USER\Environment"
    else:  # system
        env_vars = get_system_environment_variables()
        reg_path = r"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment"
        full_reg_path = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"

    if not env_vars:
        print(f"未找到{'用户' if scope == 'user' else '系统'}环境变量或读取失败")
        return False

    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{scope}_env_backup_{timestamp}.json"

    # 备份信息
    backup_data = {
        'backup_time': datetime.now().isoformat(),
        'backup_scope': scope,  # 新增：记录备份范围
        'backup_type': full_reg_path,
        'environment_variables': env_vars,
        'total_count': len(env_vars)
    }

    try:
        # 写入备份文件
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=4, ensure_ascii=False)

        # 显示备份信息
        print(f"✅ {'用户' if scope == 'user' else '系统'}环境变量备份成功！")
        print(f"📁 备份文件: {os.path.abspath(backup_file)}")
        print(f"📊 环境变量数量: {len(env_vars)}")
        print()

        # 显示环境变量列表
        print("已备份的环境变量:")
        print("-" * 80)
        for name, data in sorted(env_vars.items()):
            value_preview = str(data['value'])
            if len(value_preview) > 60:
                value_preview = value_preview[:57] + "..."
            type_display = data['type'].replace('REG_', '')
            print(f"  {name:<25} [{type_display:<8}] = {value_preview}")

        print()
        print("=" * 50)
        return backup_file

    except Exception as e:
        print(f"❌ 写入备份文件时出错: {e}")
        return False


def restore_environment_variables():
    """恢复环境变量"""
    print("恢复环境变量")
    print("=" * 50)

    # 查找备份文件（用户和系统）
    user_backup_files = [f for f in os.listdir('.') if f.startswith('user_env_backup_') and f.endswith('.json')]
    system_backup_files = [f for f in os.listdir('.') if f.startswith('system_env_backup_') and f.endswith('.json')]
    all_backup_files = user_backup_files + system_backup_files

    if not all_backup_files:
        print("未找到备份文件")
        return False

    # 显示备份文件列表
    print("找到的备份文件:")
    files_info = []
    for i, file in enumerate(sorted(all_backup_files, reverse=True), 1):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
                backup_time = backup_data.get('backup_time', '未知时间')
                backup_scope = backup_data.get('backup_scope', '未知')
                scope_display = '用户' if backup_scope == 'user' else '系统'
                print(f"{i}. {file} ({scope_display}环境变量，备份时间: {backup_time})")
                files_info.append({
                    'filename': file,
                    'scope': backup_scope,
                    'data': backup_data
                })
        except:
            print(f"{i}. {file} (无法读取信息)")

    # 选择备份文件
    try:
        choice = int(input(f"\n请选择要恢复的备份文件 (1-{len(all_backup_files)}): ")) - 1
        if choice < 0 or choice >= len(all_backup_files):
            print("❌ 选择无效")
            return False
    except:
        print("❌ 输入无效")
        return False

    backup_file = all_backup_files[choice]
    scope = 'user' if backup_file.startswith('user_') else 'system'

    try:
        # 读取备份文件
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)

        env_vars = backup_data.get('environment_variables', {})
        backup_scope = backup_data.get('backup_scope', scope)

        print(f"\n📅 备份时间: {backup_data.get('backup_time', '未知')}")
        print(f"🔧 备份类型: {'用户' if backup_scope == 'user' else '系统'}环境变量")
        print(f"📊 变量数量: {len(env_vars)}")

        # 检查权限
        if backup_scope == 'system' and not ctypes.windll.shell32.IsUserAnAdmin():
            print("\n❌ 恢复系统环境变量需要管理员权限！")
            print("请以管理员身份重新运行此程序")
            return False

        # 显示将要恢复的内容
        print("\n将要恢复的环境变量:")
        print("-" * 80)
        for name, data in sorted(env_vars.items()):
            value_preview = str(data['value'])
            if len(value_preview) > 50:
                value_preview = value_preview[:47] + "..."
            print(f"  {name:<20} = {value_preview}")

        # 确认恢复
        print(f"\n⚠️  警告: 恢复将覆盖现有的同名{'用户' if backup_scope == 'user' else '系统'}环境变量")
        confirm = input("确认恢复？(输入 'yes' 确认): ")

        if confirm.lower() != 'yes':
            print("❌ 恢复已取消")
            return False

        # 创建当前状态的备份
        print(f"\n正在创建当前{'用户' if backup_scope == 'user' else '系统'}环境变量备份...")
        current_backup = backup_environment_variables(backup_scope)
        if current_backup:
            print(f"当前状态已备份到: {current_backup}")

        # 开始恢复
        print(f"\n正在恢复{'用户' if backup_scope == 'user' else '系统'}环境变量...")

        if backup_scope == 'user':
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0,
                winreg.KEY_WRITE
            )
        else:  # system
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
                0,
                winreg.KEY_WRITE
            )

        restored_count = 0
        for name, data in env_vars.items():
            try:
                value = data['value']
                reg_type = {
                    'REG_SZ': winreg.REG_SZ,
                    'REG_EXPAND_SZ': winreg.REG_EXPAND_SZ,
                    'REG_MULTI_SZ': winreg.REG_MULTI_SZ
                }.get(data['type'], winreg.REG_SZ)

                winreg.SetValueEx(key, name, 0, reg_type, value)
                restored_count += 1
                print(f"  ✓ {name}")
            except Exception as e:
                print(f"  ✗ {name} (错误: {e})")

        winreg.CloseKey(key)

        print(f"\n✅ 恢复完成！恢复了 {restored_count} 个{'用户' if backup_scope == 'user' else '系统'}环境变量")
        print("注意: 某些环境变量可能需要重启或注销后生效")
        return True

    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        return False


def show_current_env_vars(scope='user'):
    """显示当前环境变量
    scope: 'user' 或 'system'
    """
    print(f"当前{'用户' if scope == 'user' else '系统'}环境变量")
    print("=" * 50)

    if scope == 'user':
        env_vars = get_user_environment_variables()
    else:
        env_vars = get_system_environment_variables()

    if not env_vars:
        print(f"未找到{'用户' if scope == 'user' else '系统'}环境变量")
        return

    print(f"环境变量数量: {len(env_vars)}")
    print("-" * 80)

    for name, data in sorted(env_vars.items()):
        value = str(data['value'])
        type_display = data['type'].replace('REG_', '')

        # 如果是PATH变量，分行显示每个路径
        if name.upper() == 'PATH':
            print(f"\n{name} [{type_display}]:")
            paths = value.split(';')
            for i, path in enumerate(paths, 1):
                if path.strip():
                    print(f"  {i:3d}. {path}")
        else:
            # 其他变量，截断长值
            if len(value) > 80:
                value = value[:77] + "..."
            print(f"{name:<25} [{type_display:<8}] = {value}")


def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 50)
    print("Windows 环境变量管理工具")
    print("=" * 50)
    print("1. 备份用户环境变量 (HKCU)")
    print("2. 备份系统环境变量 (HKLM)")
    print("3. 显示用户环境变量")
    print("4. 显示系统环境变量")
    print("5. 恢复环境变量 (自动识别类型)")
    print("6. 退出")
    print("=" * 50)


def main():
    """主函数"""
    print("Windows 环境变量备份与恢复工具")
    print("支持用户环境变量 (HKCU) 和系统环境变量 (HKLM)")
    print()

    # 检查管理员权限
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("⚠️  当前程序未以管理员身份运行")
            print("   - 用户环境变量 (HKCU): 可以正常操作")
            print("   - 系统环境变量 (HKLM): 仅能查看，无法备份/恢复")
            print()
    except:
        print("⚠️  无法检测管理员权限状态")
        print()

    while True:
        show_menu()

        try:
            choice = input("\n请选择操作 (1-6): ").strip()

            if choice == '1':
                backup_environment_variables('user')
                input("\n按 Enter 键继续...")

            elif choice == '2':
                backup_environment_variables('system')
                input("\n按 Enter 键继续...")

            elif choice == '3':
                show_current_env_vars('user')
                input("\n按 Enter 键继续...")

            elif choice == '4':
                show_current_env_vars('system')
                input("\n按 Enter 键继续...")

            elif choice == '5':
                restore_environment_variables()
                input("\n按 Enter 键继续...")

            elif choice == '6':
                print("\n感谢使用，再见！")
                break

            else:
                print("❌ 无效选择，请重新输入")

        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            input("\n按 Enter 键继续...")


if __name__ == "__main__":
    main()