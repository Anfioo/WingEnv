import os

from wing_utils.system.env.manager.manager import EnvManager
from wing_utils.system.env.runnner.runner import UserEnvRunner, SystemEnvRunner


def test_utils_class():
    print("=== 开始测试 EnvManager 类 ===")

    # 测试用户环境变量
    print("\n--- 测试用户环境变量 (UserEnvRunner) ---")
    user_manager = EnvManager(UserEnvRunner())



    # 2.1 测试CRUD user
    test_key = "CLASS_TEST_KEY"
    test_value = "Value from EnvManager"

    print(f"添加变量: {test_key}")
    if user_manager.add(test_key, test_value):
        print(f"验证添加: {user_manager.get(test_key)}")

    print(f"更新变量: {test_key}")
    if user_manager.update(test_key, "Updated class value"):
        print(f"验证更新: {user_manager.get(test_key)}")

    # 1.1 测试备份 user
    backup_file_user = user_manager.backup("test_user_class_backup.json")
    if backup_file_user and os.path.exists(backup_file_user):
        print(f"备份文件已生成: {backup_file_user}")

    print("\n--- 测试用户环境变量 (UserEnvRunner) ---")
    sys_manager = EnvManager(SystemEnvRunner())

    # 1.2. 测试备份 system
    backup_file_sys = sys_manager.backup("test_sys_class_backup.json")
    if backup_file_sys and os.path.exists(backup_file_sys):
        print(f"备份文件已生成: {backup_file_sys}")



    print(user_manager.get(test_key))
    print(f"验证: {test_key} 存在")
    print(f"删除变量: {test_key}")
    user_manager.delete(test_key)
    print(f"验证删除: {test_key}")
    print(user_manager.get(test_key))
    print(f"验证: {test_key} 已删除")

    if user_manager.restore("test_user_class_backup.json"):
        print("ok")
        if user_manager.get(test_key):
            print(f"恢复验证: {test_key} 已恢复")

    #
    # # 2. 测试 CRUD
    # test_key = "CLASS_TEST_KEY"
    # test_value = "Value from EnvManager"
    #
    # print(f"添加变量: {test_key}")
    # if user_manager.add(test_key, test_value):
    #     print(f"验证添加: {user_manager.get(test_key)}")
    #
    # print(f"更新变量: {test_key}")
    # if user_manager.update(test_key, "Updated class value"):
    #     print(f"验证更新: {user_manager.get(test_key)}")

    # 3. 测试恢复
    # user_manager.delete(test_key)
    # print(f"删除了 {test_key}，准备恢复...")
    # if user_manager.restore("test_user_class_backup.json"):
    #     print("ok")
    #     # if user_manager.get(test_key):
    #     #     print(f"恢复验证: {test_key} 已恢复")

    # 清理
    # if user_manager.get(test_key):
    #     user_manager.delete(test_key)
    # # if os.path.exists(backup_file):
    #     os.remove(backup_file)
    #     print(f"已清理备份文件: {backup_file}")

    # # 测试系统环境变量权限提示
    # print("\n--- 测试系统环境变量 (SystemEnvRunner) ---")
    # sys_manager = EnvManager(SystemEnvRunner())
    # print("尝试在没有管理员权限的情况下执行操作:")
    # sys_manager.add("SYS_CLASS_KEY", "should_fail")

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_utils_class()
