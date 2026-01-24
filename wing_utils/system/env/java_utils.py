import os
import subprocess
import winreg
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class JavaEnv:
    name: str
    type: str  # system / registry / path
    java_home: str  # JAVA_HOME 路径
    java_bin: str   # java.exe 路径
    version: Optional[str]
    source: str     # env / registry / path


def run(cmd):
    """执行命令返回 stdout"""
    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=5
        )
        if p.returncode == 0:
            return p.stdout.strip()
    except Exception:
        pass
    return None


def java_version(java_exe: str) -> Optional[str]:
    """获取 java 版本"""
    out = run([java_exe, "-version"])
    if not out:
        return None
    # java -version 输出通常是 stderr，也用 stdout 处理了
    # 输出示例：
    # java version "17.0.8" 2023-07-18 LTS
    # OpenJDK Runtime Environment ...
    for line in out.splitlines():
        if "version" in line:
            # 提取双引号内的版本号
            parts = line.split('"')
            if len(parts) >= 2:
                return parts[1]
    return None


def detect_java_home() -> List[JavaEnv]:
    """通过 JAVA_HOME 环境变量检测"""
    envs = []
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        java_bin = os.path.join(java_home, "bin", "java.exe")
        if os.path.exists(java_bin):
            envs.append(JavaEnv(
                name="JAVA_HOME",
                type="system",
                java_home=java_home,
                java_bin=java_bin,
                version=java_version(java_bin),
                source="env"
            ))
    return envs


def detect_registry() -> List[JavaEnv]:
    """通过注册表检测 Java"""
    envs = []
    roots = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]

    # 常见注册表路径
    reg_paths = [
        r"SOFTWARE\JavaSoft\Java Development Kit",
        r"SOFTWARE\JavaSoft\Java Runtime Environment"
    ]

    for root in roots:
        for path in reg_paths:
            try:
                with winreg.OpenKey(root, path) as key:
                    i = 0
                    while True:
                        try:
                            ver = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, ver) as sub:
                                java_home, _ = winreg.QueryValueEx(sub, "JavaHome")
                                java_bin = os.path.join(java_home, "bin", "java.exe")
                                if os.path.exists(java_bin):
                                    envs.append(JavaEnv(
                                        name=ver,
                                        type="registry",
                                        java_home=java_home,
                                        java_bin=java_bin,
                                        version=java_version(java_bin),
                                        source="registry"
                                    ))
                            i += 1
                        except OSError:
                            break
            except FileNotFoundError:
                continue
    return envs


def detect_path_java() -> List[JavaEnv]:
    """通过系统 PATH 中的 java.exe 检测"""
    envs = []
    out = run(["where", "java"])
    if not out:
        return envs
    for line in out.splitlines():
        java_bin = line.strip()
        java_home = os.path.dirname(os.path.dirname(java_bin))
        envs.append(JavaEnv(
            name="PATH",
            type="path",
            java_home=java_home,
            java_bin=java_bin,
            version=java_version(java_bin),
            source="path"
        ))
    return envs


def get_all_java_envs() -> List[JavaEnv]:
    """返回所有已检测到的 Java 环境"""
    envs = []
    envs += detect_java_home()
    envs += detect_registry()
    envs += detect_path_java()

    # 按 java_bin 去重
    unique = {}
    for e in envs:
        unique[e.java_bin.lower()] = e

    return list(unique.values())


# 调用示例
if __name__ == "__main__":
    java_envs = get_all_java_envs()
    for env in java_envs:
        print(env)
