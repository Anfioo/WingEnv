# --- 使用示例 ---
from conf.QR_CONFIG import QR_ALIAPY_CONFIG, QR_WECHAT_CONFIG
from wing_utils.qr.qr_utils import print_qr_with_info, QRCompressionUtils

if __name__ == "__main__":
    try:
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

    except Exception as e:
        print(f"运行失败: {e}")
