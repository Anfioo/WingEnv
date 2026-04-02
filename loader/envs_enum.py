#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------Project Information------------------
@Project : WingShake->WingEnv
@File : env_manager.py
@Path : loader/ini
@Author : Anfioo
@Date : 2026/1/29 18:44
------------------------Contact------------------------
@Github : https://github.com/Anfioo
@Gmail : anfioozys@gmail.com
@QQ Email : 3485977506@qq.com
"""
from enum import Enum  # 必须导入枚举基类
from pathlib import Path
from typing import Optional, Dict

from wing_utils import IniConfigUtils


class EnvsEnum(Enum):
    # 格式：名称 = 值
    JDK = "jdk"  # 开发环境
    PYTHON = "python"  # 测试环境
    MAVEN = "maven"  # 生产环境
