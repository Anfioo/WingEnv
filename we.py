import sys

from conf.QR_CONFIG import QR_ALIAPY_CONFIG, QR_WECHAT_CONFIG
from wing_client.theme_cli import ThemeCLI
from wing_ui.banner import print_banner
from wing_ui.print_avatar_ui import print_avatar
from wing_utils.qr.qr_utils import print_qr_with_info, QRCompressionUtils


def cmd_help(args):
    print("""
可用命令：
  help                显示帮助
  run                 运行程序
  build <env>         构建环境（dev / prod）
""")


def cmd_run(args):
    print("执行 run")
    print("参数:", args)


def info(args):
    print("执行 info")
    print("参数:", args)
    print_banner()

def av(args):
    print("执行 info")
    print("参数:", args)
    print_avatar()
def qr(args):
    info = {
        "姓名": "Anfioo",
        "微信": "anfioo_dev",
        "邮箱": "me@example.com",
        "GitHub": "github.com/anfioo",
        "备注": "欢迎交流技术 🤝",
    }
    # 还原
    print_qr_with_info(QRCompressionUtils.decompress_to_matrix(QR_ALIAPY_CONFIG), mode="alipay", title="支付宝",
                       info=info)
    print_qr_with_info(QRCompressionUtils.decompress_to_matrix(QR_WECHAT_CONFIG), mode="wechat", title="微信",
                       info=info)




def cmd_run_themes(args):
    print("执行 run")
    cli = ThemeCLI(prompt_text="WingEnv > ")
    print("参数:", args)
    cli.execute_argv(args)


def cmd_build(args):
    if not args:
        print("❌ build 需要参数: dev / prod")
        return
    print(f"开始 build，环境: {args[0]}")


COMMANDS = {
    "help": cmd_help,
    "info": info,
    "av": av,
    "run": cmd_run,
    "build": cmd_build,
    "qr": qr,
    "themes": cmd_run_themes,
}


def main():
    if len(sys.argv) < 2:
        cmd_help([])
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
