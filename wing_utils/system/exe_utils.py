#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------Project Information------------------
@Project : WingShake->WingEnv
@File : exe_utils.py
@Path : wing_utils/system
@Author : Anfioo
@Date : 2026/4/3 14:30
------------------------Contact------------------------
@Github : https://github.com/Anfioo
@Gmail : anfioozys@gmail.com
@QQ Email : 3485977506@qq.com
"""

import sys
import os
from pathlib import Path


class ExeUtils:
    """EXE打包相关工具类"""
    
    @staticmethod
    def is_frozen() -> bool:
        """
        检测是否运行在打包的EXE环境中
        :return: True如果是EXE，False如果是脚本
        """
        return getattr(sys, 'frozen', False)
    
    @staticmethod
    def get_executable_path() -> Path:
        """
        获取可执行文件的真实路径（兼容脚本和EXE模式）
        :return: 可执行文件的Path对象
        """
        if ExeUtils.is_frozen():
            # EXE模式：sys.executable 指向实际的EXE文件
            return Path(sys.executable).resolve()
        else:
            # 脚本模式：使用__file__
            return Path(__file__).resolve().parent.parent.parent / "we.py"
    
    @staticmethod
    def get_executable_name() -> str:
        """
        获取可执行文件名
        :return: 文件名（如 "we.exe" 或 "we.py"）
        """
        if ExeUtils.is_frozen():
            return Path(sys.executable).name
        else:
            return "we.py"
    
    @staticmethod
    def get_working_dir() -> Path:
        """
        获取工作目录（EXE所在目录或脚本所在目录）
        :return: 目录的Path对象
        """
        if ExeUtils.is_frozen():
            return Path(sys.executable).parent.resolve()
        else:
            return Path(__file__).resolve().parent.parent.parent
    
    @staticmethod
    def setup_for_exe(target_dir: Path) -> bool:
        """
        为EXE模式设置环境（创建快捷方式或批处理文件）
        :param target_dir: 目标目录（环境变量要添加的目录）
        :return: 是否成功
        """
        try:
            if not ExeUtils.is_frozen():
                return True  # 不是EXE模式，不需要特殊处理
            
            exe_path = Path(sys.executable).resolve()
            exe_name = exe_path.name
            
            # 确保目标目录存在
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建批处理文件（.bat）来调用EXE
            bat_content = f"""@echo off
REM WingEnv 启动脚本
"{exe_path}" %*
"""
            bat_file = target_dir / "we.bat"
            
            with open(bat_file, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            print(f"✅ 已创建启动脚本: {bat_file}")
            return True
            
        except Exception as e:
            print(f"❌ EXE环境设置失败: {e}")
            return False
    
    @staticmethod
    def get_system_info() -> dict:
        """
        获取系统信息（用于调试）
        :return: 包含系统信息的字典
        """
        info = {
            "is_frozen": ExeUtils.is_frozen(),
            "executable": str(sys.executable) if hasattr(sys, 'executable') else "N/A",
            "argv": sys.argv,
            "platform": sys.platform,
            "python_version": sys.version,
        }
        
        if ExeUtils.is_frozen():
            info["frozen_attributes"] = {
                "frozen": sys.frozen if hasattr(sys, 'frozen') else "N/A",
                "meipass": sys._MEIPASS if hasattr(sys, '_MEIPASS') else "N/A",
            }
        
        return info
    
    @staticmethod
    def print_system_info():
        """打印系统信息（用于调试）"""
        info = ExeUtils.get_system_info()
        print("=== 系统信息 ===")
        for key, value in info.items():
            if key == "argv":
                print(f"  {key}: {value}")
            elif key == "frozen_attributes" and isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")