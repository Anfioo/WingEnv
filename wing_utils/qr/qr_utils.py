from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import base64
import gzip
import binascii

from conf.QR_CONFIG import COLOR_SCHEMES


def print_qr_with_info(
        matrix,
        mode: str = "default",
        title: str | None = None,
        info: dict | None = None,
):
    console = Console()
    h, w = len(matrix), len(matrix[0])

    scheme = COLOR_SCHEMES.get(mode, COLOR_SCHEMES["default"])

    def lerp(a, b, t):
        return int(a + (b - a) * t)

    # -------- 左侧：二维码 --------
    qr_lines = []

    for y in range(0, h, 2):
        text = Text()

        if scheme["type"] == "solid":
            r, g, b = scheme["color"]
        else:
            t = y / h
            r = lerp(scheme["start"][0], scheme["end"][0], t)
            g = lerp(scheme["start"][1], scheme["end"][1], t)
            b = lerp(scheme["start"][2], scheme["end"][2], t)

        color_style = f"rgb({r},{g},{b})"

        for x in range(w):
            top = matrix[y][x]
            bottom = matrix[y + 1][x] if y + 1 < h else False

            if top and bottom:
                text.append("█", style=color_style)
            elif top:
                text.append("▀", style=color_style)
            elif bottom:
                text.append("▄", style=color_style)
            else:
                text.append(" ")

        qr_lines.append(text)

    qr_block = Text("\n").join(qr_lines)

    qr_panel = Panel(
        qr_block,
        title=title or "QR Code",
        box=box.ROUNDED,
        border_style=scheme["border"],
        padding=(1, 2),
    )

    # -------- 右侧：信息表 --------
    info = info or {}

    table = Table.grid(padding=(0, 1))
    table.add_column(justify="right", style="bold cyan", no_wrap=True)
    table.add_column(style="white")

    for k, v in info.items():
        table.add_row(k, v)

    info_panel = Panel(
        table,
        title="Contact",
        box=box.ROUNDED,
        border_style="dim",
        padding=(1, 2),
    )

    # -------- 布局 --------
    console.print(
        Columns(
            [qr_panel, info_panel],
            equal=False,
            expand=False,
        )
    )


class QRCompressionUtils:
    """二维码矩阵压缩与还原工具类"""

    @staticmethod
    def compress_matrix(matrix: list, level: int = 9) -> str:
        """
        将二维码布尔矩阵转换为 "行长度.Base64压缩字符串" 格式

        Args:
            matrix: 二维布尔矩阵 (List[List[bool]])
            level: 压缩级别 (1-9)
        """
        if not matrix or not matrix[0]:
            raise ValueError("输入的二维码矩阵不能为空")

        row_len = len(matrix[0])

        # 1. 扁平化：将二维布尔矩阵转换为 '1010...' 字符串
        # 使用 join 提高性能，避免 += 产生的内存复制
        bits_list = []
        for row in matrix:
            if len(row) != row_len:
                raise ValueError(f"矩阵行长度不一致，预期 {row_len}")
            bits_list.append(''.join(['1' if b else '0' for b in row]))

        bit_str_all = ''.join(bits_list)

        # 2. 压缩：Gzip 压缩
        try:
            compressed_bytes = gzip.compress(bit_str_all.encode('utf-8'), compresslevel=level)
            # 3. 编码：Base64 编码
            compressed_b64 = base64.b64encode(compressed_bytes).decode('utf-8')
            return f"{row_len}.{compressed_b64}"
        except Exception as e:
            raise ValueError(f"压缩过程出错: {str(e)}")

    @staticmethod
    def decompress_to_matrix(compressed_str: str) -> list:
        """
        从 "行长度.Base64压缩字符串" 还原二维码布尔矩阵
        """
        try:
            # 1. 格式校验
            if '.' not in compressed_str:
                raise ValueError("格式错误，缺少行长度前缀")

            row_len_str, b64_data = compressed_str.split('.', 1)
            row_len = int(row_len_str)

            # 2. Base64 解码
            try:
                compressed_bytes = base64.b64decode(b64_data)
            except (binascii.Error, TypeError) as e:
                raise ValueError(f"Base64解码失败: {str(e)}")

            # 3. Gzip 解压缩
            try:
                decompressed_str = gzip.decompress(compressed_bytes).decode('utf-8')
            except (gzip.BadGzipFile, binascii.Error) as e:
                raise ValueError(f"解压缩失败，数据可能损坏: {str(e)}")

            # 4. 还原矩阵
            str_len = len(decompressed_str)
            if str_len % row_len != 0:
                raise ValueError(f"数据长度({str_len})与行长度({row_len})不匹配")

            qr_matrix = []
            for i in range(0, str_len, row_len):
                row_str = decompressed_str[i: i + row_len]
                qr_matrix.append([True if c == '1' else False for c in row_str])

            return qr_matrix

        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"还原二维码配置时发生未知错误: {str(e)}")
