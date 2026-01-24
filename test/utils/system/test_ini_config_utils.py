#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------Project Information------------------
@Project : WingShake->WingEnv
@File : test_ini_config_utils.py.py
@Path : test/utils/system
@Author : Anfioo
@Date : 2026/1/12 14:44
------------------------Contact------------------------
@Github : https://github.com/Anfioo
@Gmail : anfioozys@gmail.com
@QQ Email : 3485977506@qq.com
"""
from wing_utils import IniConfigUtils

cfg = IniConfigUtils()

cfg.set("pip", "index-url", "https://pypi.tuna.tsinghua.edu.cn/simple1asd")
print(cfg.get("pip", "index-url"))
print(cfg.get_section("pip"))

print(cfg.dump())
