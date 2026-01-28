#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------Project Information------------------
@Project : WingShake->WingEnv
@File : console.py.py
@Path : wing_utils/ui
@Author : Anfioo
@Date : 2026/1/28 10:42
------------------------Contact------------------------
@Github : https://github.com/Anfioo
@Gmail : anfioozys@gmail.com
@QQ Email : 3485977506@qq.com
"""
import sys

from rich.console import Console

# 全局单进程统一的控制台
console = Console(
    file=sys.__stdout__,  # <- 关键：绕过 patch_stdout
    force_terminal=True,
    color_system="truecolor"
)