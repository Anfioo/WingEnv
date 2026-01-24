import os
import subprocess
import json
import winreg
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class PythonEnv:
    name: str
    type: str  # system / conda / uv / poetry / venv
    python: str  # python.exe 路径
    version: Optional[str]
    source: str  # cmd / registry / scan


def run(cmd):
    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5
        )
        if p.returncode == 0:
            return p.stdout.strip()
    except Exception:
        pass
    return None


def python_version(python_exe: str):
    out = run([python_exe, "--version"])
    return out.replace("Python ", "") if out else None


def extract_json(text: str):
    """从包含噪声的输出中提取第一个 JSON 对象"""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("未找到有效 JSON 数据")
    return json.loads(text[start:end + 1])


def detect_py_launcher() -> List[PythonEnv]:
    out = run(["py", "-0p"])
    envs = []

    if not out:
        return envs

    for line in out.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2:
            python = parts[-1]
            envs.append(PythonEnv(
                name=line.strip(),
                type="system",
                python=python,
                version=python_version(python),
                source="py-launcher"
            ))
    return envs


def detect_conda() -> List[PythonEnv]:
    envs = []
    out = run(["conda", "info", "--json"])
    if not out:
        return envs

    try:
        data = extract_json(out)
    except Exception as e:
        print("⚠ conda JSON 解析失败:", e)
        return envs

    for env_path in data.get("envs", []):
        python = os.path.join(env_path, "python.exe")
        if not os.path.exists(python):
            continue
        envs.append(PythonEnv(
            name=os.path.basename(env_path),
            type="conda",
            python=python,
            version=python_version(python),
            source="conda"
        ))

    return envs


def detect_uv() -> List[PythonEnv]:
    out = run(["uv", "python", "list"])
    envs = []

    if not out:
        return envs

    for line in out.splitlines():
        if "python.exe" in line:
            parts = line.split()
            python = parts[-1]
            envs.append(PythonEnv(
                name=parts[0],
                type="uv",
                python=python,
                version=python_version(python),
                source="uv"
            ))
    return envs


def detect_registry() -> List[PythonEnv]:
    envs = []
    roots = [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]
    base = r"SOFTWARE\Python\PythonCore"

    for root in roots:
        try:
            with winreg.OpenKey(root, base) as key:
                i = 0
                while True:
                    try:
                        ver = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, ver + r"\InstallPath") as sub:
                            path, _ = winreg.QueryValueEx(sub, "")
                            python = os.path.join(path, "python.exe")
                            envs.append(PythonEnv(
                                name=ver,
                                type="system",
                                python=python,
                                version=python_version(python),
                                source="registry"
                            ))
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            pass
    return envs


def get_all_python_envs() -> List[PythonEnv]:
    """返回所有已检测到的 Python 环境对象列表"""
    envs = []
    envs += detect_py_launcher()
    envs += detect_conda()
    envs += detect_uv()
    envs += detect_registry()

    # 按 python 路径去重
    unique = {}
    for e in envs:
        unique[e.python.lower()] = e

    return list(unique.values())


# 调用示例
if __name__ == "__main__":
    python_envs = get_all_python_envs()
    for env in python_envs:
        print(env)
