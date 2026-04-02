#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------Project Information------------------
@Project : WingShake->WingEnv
@File : path_env_utils.py
@Path : wing_utils/system/env
@Author : Anfioo
@Date : 2026/4/2 17:21
------------------------Contact------------------------
@Github : https://github.com/Anfioo
@Gmail : anfioozys@gmail.com
@QQ Email : 3485977506@qq.com
"""


class PathEnvUtils:
    """
    PATH 环境变量工具类
    提供：字符串转列表、列表转字符串、按索引插入路径
    """

    @staticmethod
    def path_str_to_list(path_str: str) -> list[str]:
        """
        把 PATH 字符串 转为 干净的 list[str]
        自动去空、去前后空格、去重
        :param path_str: 从系统获取的原始 PATH 字符串
        :return: 干净的路径列表
        """
        if not path_str:
            return []

        # 按 ; 分割 + 去空 + 去空格
        path_list = [p.strip() for p in path_str.split(";") if p.strip()]

        # 去重（保持顺序）
        unique_list = []
        for item in path_list:
            if item not in unique_list:
                unique_list.append(item)

        return unique_list

    @staticmethod
    def list_to_path_str(path_list: list[str]) -> str:
        """
        把 list[str] 转回标准 PATH 字符串
        :param path_list: 路径列表
        :return: 用 ; 连接的 PATH 字符串
        """
        if not path_list:
            return ""
        return ";".join(path_list)

    @staticmethod
    def insert_path_at_index(
            original_path_list: list[str],
            insert_str: str,
            index: int
    ) -> list[str]:
        """
        在列表指定索引位置插入路径（0开始）
        自动去重：已存在则不插入，并红色提示
        :param original_path_list: 原始路径列表（来自 path_str_to_list）
        :param insert_str: 要插入的路径字符串
        :param index: 插入位置，0=最前面，len(list)=最后面
        :return: 处理后的新列表
        """
        # 复制一份，避免修改原列表
        new_list = original_path_list.copy()

        # 去重：已存在 → 红色提示，跳过插入
        if insert_str in new_list:
            # 红色输出提示
            print(f"\033[91m❌ 路径已存在，跳过插入：{insert_str}\033[0m")
            return new_list

        # 安全处理索引越界
        if index < 0:
            index = 0
        if index > len(new_list):
            index = len(new_list)

        # 插入
        new_list.insert(index, insert_str)
        return new_list
