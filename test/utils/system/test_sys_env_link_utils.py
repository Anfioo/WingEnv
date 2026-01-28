#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------Project Information------------------
@Project : WingShake->WingEnv
@File : test_sys_env_link_utils.py
@Path : test/utils/system
@Author : Anfioo
@Date : 2026/1/29 13:37
------------------------Contact------------------------
@Github : https://github.com/Anfioo
@Gmail : anfioozys@gmail.com
@QQ Email : 3485977506@qq.com
"""
from wing_utils.system import create_dir_symlink

create_dir_symlink(r"C:\Envs\JDK\jdk-17.0.12", r"C:\Apps\MyProjects\WingEnv\test\utils\system\envs\env", "backup")
