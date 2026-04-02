#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------Project Information------------------
@Project : WingShake->WingEnv
@File : __init__.py.py
@Path : install/client
@Author : Anfioo
@Date : 2026/3/31 10:16
------------------------Contact------------------------
@Github : https://github.com/Anfioo
@Gmail : anfioozys@gmail.com
@QQ Email : 3485977506@qq.com
"""

from .install_base_cli import BaseInstallCLIData
from .install_jdk_cli import JdkCLI
from .install_jdk_cli import JdkCLIData

__all__ = ["BaseInstallCLIData","JdkCLI","JdkCLIData"]

