import sys


def cmd_help(args):
    # 初始化 RichWingUI
    if env():
        if init():
            from loader import StyleLoader
            from wing_ui.rich_wing_ui import RichWingUI
            style_loader = StyleLoader()
            rich_ui = RichWingUI(style_loader)

            # 定义命令帮助数据
            commands_data = [
                {"命令": "help", "描述": "查看完整帮助文档"},
                {"命令": "init", "描述": "初始化项目环境"},
                {"命令": "run", "描述": "运行主程序"},
                {"命令": "info", "描述": "打印项目信息 + 项目 Banner"},
                {"命令": "av", "描述": "打印头像/标识"},
                {"命令": "qr", "描述": "生成并展示支付宝、微信收款二维码"},
                {"命令": "themes", "描述": "主题配置管理工具（交互式/命令式）"},
                {"命令": "jdk", "描述": "JDK 环境管理工具（交互式/命令式）"},
            ]

            # 使用 RichWingUI 打印表格
            rich_ui.print_table(
                data=commands_data,
                columns=["命令", "描述"],
                title="WingEnv 命令帮助",
                show_index=True
            )

            # 添加使用说明
            rich_ui.print_info("使用方法: we <命令> [参数]", title="使用说明")
            rich_ui.print_info("示例: we info  # 查看项目信息", title="示例")
        else:
            print("初始化失败")
    else:
        print("将we放入系统变量失败")


# def cmd_run(args):
#     print("执行 run")
#     print("参数:", args)


def info(args):
    from wing_ui.banner import print_banner

    print_banner()


def av(args):
    from wing_ui.print_avatar_ui import print_avatar

    print_avatar()


def qr(args):
    from conf.QR_CONFIG import QR_ALIAPY_CONFIG, QR_WECHAT_CONFIG
    from wing_utils.qr.qr_utils import print_qr_with_info, QRCompressionUtils

    info = {
        "姓名": "Anfioo",
        "微信": "AnfiooWork",
        "邮箱": "3485977506@qq.com",
        "GitHub": "github.com/Anfioo",
        "备注": "欢迎交流技术 🤝",
    }
    # 还原
    print_qr_with_info(QRCompressionUtils.decompress_to_matrix(QR_ALIAPY_CONFIG), mode="alipay", title="支付宝",
                       info=info)
    print_qr_with_info(QRCompressionUtils.decompress_to_matrix(QR_WECHAT_CONFIG), mode="wechat", title="微信",
                       info=info)


def cmd_run_themes(args):
    from wing_client.theme_cli import ThemeCLI

    cli = ThemeCLI(prompt_text="WingEnv-ThemeCLI > ")
    if len(args) == 0:
        cli.start_interactive()
    else:
        cli.execute_argv(args)


def cmd_run_jdk(args):
    from install.client import JdkCLI

    cli = JdkCLI(prompt_text="WingEnv-JdkCLI > ")
    if len(args) == 0:
        cli.start_interactive()
    else:
        cli.execute_argv(args)


def cmd_build(args):
    if not args:
        print("❌ build 需要参数: dev / prod")
        return
    print(f"开始 build，环境: {args[0]}")


def init():
    from loader import ThemeManager, EnvsSymlinkManager, DownloadsManager
    from loader.ini.extract_manager import ExtractManager
    from wing_utils import IniConfigUtils

    ini_config = IniConfigUtils()
    path = ini_config.getConfigWorkingPath()
    style_path = path / "data" / "style"
    exists = style_path.exists()
    if exists:
        return True
    else:
        try:
            ThemeManager().initialize_theme()
            EnvsSymlinkManager().initialize_symlink()
            ExtractManager().initialize_extract()
            DownloadsManager().initialize_downloads()
            return True
        except Exception as e:
            print(f"❌ 更新环境变量失败: {e}")
            return False


def env():
    from wing_utils import IniConfigUtils
    from wing_utils.system import UserEnvRunner, EnvManager
    from wing_utils.system.env.path_env_utils import PathEnvUtils
    import sys
    import shutil
    from pathlib import Path

    ini_config = IniConfigUtils()
    path = ini_config.getConfigWorkingPath()
    try:
        # 启动用户环境变量工具
        user_manager = EnvManager(UserEnvRunner())
        path_result = user_manager.get("PATH")
        if path_result and "value" in path_result:
            current_path_str = path_result["value"]
            current_path_list = PathEnvUtils.path_str_to_list(current_path_str)
            path_str = str(path)

            # 检查路径是否已存在
            if path_str in current_path_list:
                return True

            # ===================== 获取当前可执行文件路径 =====================
            is_frozen = getattr(sys, 'frozen', False)

            if is_frozen:
                # EXE模式：sys.executable 指向实际的EXE文件
                current_exe = Path(sys.executable).resolve()
                target_exe = path / current_exe.name
            else:
                # 脚本模式：使用__file__
                current_exe = Path(__file__).resolve()
                target_exe = path / current_exe.name

            # 如果目录不存在，先创建
            path.mkdir(parents=True, exist_ok=True)

            # 复制文件（不存在才复制，避免重复覆盖）
            if not target_exe.exists():
                shutil.copy2(current_exe, target_exe)
                print(f"✅ 已复制{'EXE' if is_frozen else '脚本'}到：{target_exe}")
            # =============================================================

            # 更新PATH环境变量
            new_path_list = PathEnvUtils.insert_path_at_index(current_path_list, path_str, 0)
            user_manager.add("PATH", PathEnvUtils.list_to_path_str(new_path_list))
            print("✅ 已将 WingEnv 添加到环境变量")
            return True
        else:
            print("❌ 无法获取PATH环境变量")
            return False
    except Exception as e:
        print(f"❌ 更新环境变量失败: {e}")
        return False


COMMANDS = {
    "help": cmd_help,
    "info": info,
    "av": av,
    # "run": cmd_run,
    "qr": qr,
    "themes": cmd_run_themes,
    "jdk": cmd_run_jdk,
    "init": init
}


def main():
    if len(sys.argv) < 2:
        cmd_help([])
        input()
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    if command not in COMMANDS:
        print(f"❌ 未知命令: {command}")
        cmd_help([])
        return

    COMMANDS[command](args)


if __name__ == "__main__":
    main()
