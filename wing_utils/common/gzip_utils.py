#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------Project Information------------------
@Project : WingShake->WingEnv
@File : gzip_utils.py
@Path : wing_utils/qr
@Author : Anfioo
@Date : 2026/1/27 17:34
------------------------Contact------------------------
@Github : https://github.com/Anfioo
@Gmail : anfioozys@gmail.com
@QQ Email : 3485977506@qq.com
"""

import gzip
import base64
import binascii


class GzipUtils:
    """Gzip压缩与解压工具类"""

    @staticmethod
    def compress(data: str, level: int = 9) -> str:
        """
        压缩字符串为Base64编码的Gzip数据

        Args:
            data: 要压缩的字符串
            level: 压缩级别 (1-9)

        Returns:
            Base64编码的压缩数据
        """
        try:
            compressed_bytes = gzip.compress(data.encode('utf-8'), compresslevel=level)
            return base64.b64encode(compressed_bytes).decode('utf-8')
        except Exception as e:
            raise ValueError(f"压缩过程出错: {str(e)}")

    @staticmethod
    def decompress(compressed_data: str) -> str:
        """
        从Base64编码的Gzip数据中解压字符串

        Args:
            compressed_data: Base64编码的压缩数据

        Returns:
            解压后的字符串
        """
        try:
            # Base64解码
            compressed_bytes = base64.b64decode(compressed_data)
            # Gzip解压
            return gzip.decompress(compressed_bytes).decode('utf-8')
        except (binascii.Error, TypeError) as e:
            raise ValueError(f"Base64解码失败: {str(e)}")
        except (gzip.BadGzipFile, binascii.Error) as e:
            raise ValueError(f"解压缩失败，数据可能损坏: {str(e)}")
        except Exception as e:
            raise ValueError(f"解压过程发生未知错误: {str(e)}")

    @staticmethod
    def compress_bytes(data: bytes, level: int = 9) -> bytes:
        """
        压缩字节数据

        Args:
            data: 要压缩的字节数据
            level: 压缩级别 (1-9)

        Returns:
            压缩后的字节数据
        """
        try:
            return gzip.compress(data, compresslevel=level)
        except Exception as e:
            raise ValueError(f"压缩过程出错: {str(e)}")

    @staticmethod
    def decompress_bytes(compressed_data: bytes) -> bytes:
        """
        解压字节数据

        Args:
            compressed_data: 压缩的字节数据

        Returns:
            解压后的字节数据
        """
        try:
            return gzip.decompress(compressed_data)
        except Exception as e:
            raise ValueError(f"解压过程出错: {str(e)}")
