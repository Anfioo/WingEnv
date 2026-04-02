# WingEnv 贡献者指南

欢迎来到 WingEnv 项目！我们很高兴你对这个现代化开发环境管理工具感兴趣。本指南将帮助你了解如何为项目做出贡献。

## 🎯 项目愿景

WingEnv 旨在成为**一站式开发环境管理平台**，解决开发者在不同项目间切换环境版本的痛点。我们已经完整实现了 JDK 环境管理，现在需要社区的力量来实现更多环境类型。

## 🏗️ 项目架构概览

WingEnv 采用**高度模块化**和**插件化**的架构设计：

```
WingEnv/
├── install/                    # 环境安装管理（核心模块）
│   ├── client/                # 命令行客户端
│   ├── install_builder/       # 环境安装构建器
│   ├── retrieval_flow_builder/# 数据检索流程构建器
│   └── configure_flow_builder/# 配置流程构建器
├── wing_utils/                # 工具库（高度复用）
├── wing_ui/                   # 用户界面组件
├── wing_client/               # 客户端框架
├── loader/                    # 加载器和配置管理
└── test/                      # 测试代码
```

### 核心设计模式

1. **构建者模式（Builder Pattern）**：每个环境类型都有对应的 `RetrievalFlowBuilder`
2. **插件化架构**：新的环境类型可以像插件一样轻松添加
3. **模块化设计**：各功能模块高度独立，易于维护和扩展

## 🚀 如何开始贡献

### 第一步：环境设置

1. **克隆仓库**
   ```bash
   git clone https://github.com/Anfioo/WingEnv.git
   cd WingEnv
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行测试**
   ```bash
   # 运行现有测试确保环境正常
   python -m pytest test/ -v
   ```

### 第二步：选择贡献方向

我们为贡献者准备了多个难度级别的任务：

#### 🟢 新手友好任务（适合第一次贡献者）

1. **文档改进**
   - 完善现有功能的文档
   - 添加使用示例
   - 翻译文档

2. **测试编写**
   - 为现有功能添加单元测试
   - 编写集成测试
   - 创建测试用例

3. **Bug 修复**
   - 修复已知的小问题
   - 改进错误处理
   - 优化用户体验

#### 🟡 中级任务（适合有一定经验的贡献者）

1. **环境类型实现**（最需要的贡献！）
   - 实现 Node.js 环境管理
   - 实现 Python 环境管理  
   - 实现 Go 环境管理
   - 实现 Maven 环境管理
   - 实现 CMake 环境管理
   - 实现 Miniconda 环境管理

2. **功能增强**
   - 添加新的下载镜像源
   - 实现环境备份/恢复功能
   - 添加环境模板功能

#### 🔴 高级任务（适合资深贡献者）

1. **架构改进**
   - 优化性能
   - 重构核心模块
   - 添加插件系统

2. **新特性开发**
   - Docker 集成
   - 云环境同步
   - IDE 插件开发

## 🛠️ 实现新环境类型的完整指南

这是最重要的贡献方向！让我们以 **Node.js 环境实现**为例，展示完整的实现流程：

### 步骤 1：理解现有架构

首先，查看已实现的 JDK 环境作为参考：
- [jdk_flow_builder.py](install/retrieval_flow_builder/jdk_flow_builder.py) - 数据检索流程
- [install_jdk_builder.py](install/install_builder/install_jdk_builder.py) - 安装构建器
- [install_jdk_cli.py](install/client/install_jdk_cli.py) - 命令行客户端
- [jdk_ini_manager.py](install/client/ini/jdk_ini_manager.py) - 配置管理器

### 步骤 2：扩展 EnvsEnum

在 [envs_enum.py](loader/envs_enum.py) 中添加新的环境类型：

```python
class EnvsEnum(Enum):
    JDK = "jdk"
    NODEJS = "nodejs"  # 新增
    PYTHON = "python"
    GO = "go"
    MAVEN = "maven"
    CMAKE = "cmake"
    MINICONDA = "miniconda"
```

### 步骤 3：实现 RetrievalFlowBuilder

创建 `nodejs_flow_builder.py` 在 `install/retrieval_flow_builder/` 目录：

```python
from typing import Any, Callable, Optional, Dict, Self
import requests

from install.retrieval_flow_builder import BaseRetrievalFlowBuilder
from loader.ini.cache_file_manager import CacheFileManager

class NodeJSRetrievalFlowBuilder(BaseRetrievalFlowBuilder):
    @classmethod
    def default(cls, os: str = "windows", arch: str = "x64", selector: Callable = None) -> Self:
        instance = cls(selector=selector)
        instance._metadata["os"] = os
        instance._metadata["arch"] = arch
        return instance

    def fetch_data(self) -> Self:
        # 实现从 Node.js 官方源获取版本数据
        # 可以参考 JDK 的实现
        pass
    
    def vendor(self) -> Self:
        # Node.js 通常只有一个官方源，但可以支持 LTS/Current 版本选择
        pass
    
    def version(self) -> Self:
        # 实现版本选择逻辑
        pass
```

### 步骤 4：实现 InstallBuilder

创建 `install_nodejs_builder.py` 在 `install/install_builder/` 目录：

```python
from install.install_builder import BaseInstallBuilder

class InstallNodeJSBuilder(BaseInstallBuilder):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.env_type = "nodejs"
    
    def download(self) -> bool:
        # 实现 Node.js 下载逻辑
        pass
    
    def extract(self) -> bool:
        # 实现解压逻辑
        pass
    
    def configure(self) -> bool:
        # 配置环境变量（NODE_HOME, PATH）
        pass
```

### 步骤 5：实现 CLI 客户端

创建 `install_nodejs_cli.py` 在 `install/client/` 目录：

```python
from install.client.install_base_cli import BaseInstallCLI

class NodeJSCLI(BaseInstallCLI):
    def __init__(self):
        super().__init__("nodejs")
    
    def ls(self) -> None:
        # 列出已安装的 Node.js 版本
        pass
    
    def install(self) -> None:
        # 安装新的 Node.js 版本
        pass
    
    def set(self, version: str) -> None:
        # 切换当前使用的 Node.js 版本
        pass
```

### 步骤 6：注册到主程序

在 `we.py` 中添加新的命令：

```python
# 添加新的命令处理器
def cmd_nodejs(args):
    from install.client.install_nodejs_cli import NodeJSCLI
    cli = NodeJSCLI()
    cli.run(args)

# 在命令映射中添加
command_map = {
    "help": cmd_help,
    "info": info,
    "jdk": cmd_jdk,
    "nodejs": cmd_nodejs,  # 新增
    "themes": cmd_themes,
    "qr": cmd_qr,
}
```

### 步骤 7：编写测试

创建测试文件确保功能正确：

```python
# test/install/test_nodejs_builder.py
import pytest
from install.install_builder.install_nodejs_builder import InstallNodeJSBuilder

def test_nodejs_builder_initialization():
    config = {"version": "18.17.0", "os": "windows", "arch": "x64"}
    builder = InstallNodeJSBuilder(config)
    assert builder.env_type == "nodejs"
```

## 📋 贡献流程

### 1. 寻找或创建 Issue

- 查看 [Issues](https://github.com/Anfioo/WingEnv/issues) 页面
- 如果没有相关 Issue，可以创建一个新的
- 描述清楚你要实现的功能或修复的问题

### 2. 创建功能分支

```bash
git checkout -b feature/nodejs-support
# 或
git checkout -b fix/issue-123
```

### 3. 开发实现

- 遵循项目的代码风格
- 添加适当的注释
- 编写单元测试
- 确保代码通过现有测试

### 4. 提交更改

```bash
git add .
git commit -m "feat: add Node.js environment support"
```

### 5. 推送到远程仓库

```bash
git push origin feature/nodejs-support
```

### 6. 创建 Pull Request

- 在 GitHub 上创建 Pull Request
- 描述你的更改内容
- 链接相关的 Issue
- 等待代码审查

## 🎨 代码规范

### Python 代码风格

- 使用 **PEP 8** 规范
- 函数和类使用**蛇形命名法**（snake_case）
- 类名使用**驼峰命名法**（CamelCase）
- 添加适当的类型提示

### 文档要求

- 公共函数和类必须有文档字符串
- 复杂的逻辑需要添加注释
- 更新相关的 README 文档

### 测试要求

- 新功能必须包含单元测试
- 测试覆盖率不应降低
- 测试文件名以 `test_` 开头

## 🤝 沟通与协作

### 讨论渠道

1. **GitHub Issues** - 功能讨论和问题报告
2. **Pull Requests** - 代码审查和合并
3. **项目文档** - 查看架构和设计决策

### 行为准则

- 尊重所有贡献者
- 建设性的代码审查
- 友好的沟通氛围
- 帮助新贡献者入门

## 🏆 贡献者认可

所有贡献者都将被记录在项目的贡献者列表中。我们特别鼓励：

- **第一次贡献者** - 特别欢迎，我们会提供额外指导
- **持续贡献者** - 有机会成为项目维护者
- **重大功能实现** - 在发布说明中特别提及

## 🚀 快速入门任务清单

如果你不确定从哪里开始，这里有一些具体的入门任务：

### 任务 1：完善 Node.js 环境实现
- 难度：🟡 中级
- 预计时间：2-3天
- 技能要求：Python、HTTP 请求、文件操作
- 参考：[JDK 实现](install/retrieval_flow_builder/jdk_flow_builder.py)

### 任务 2：添加 Python 环境支持
- 难度：🟡 中级  
- 预计时间：2-3天
- 技能要求：Python、环境变量管理
- 参考：同上

### 任务 3：创建贡献者示例项目
- 难度：🟢 新手
- 预计时间：1天
- 技能要求：文档编写、示例代码
- 描述：创建一个完整的示例，展示如何实现一个新环境类型

### 任务 4：编写更多测试
- 难度：🟢 新手
- 预计时间：几小时
- 技能要求：Python、pytest
- 描述：为现有功能添加更多测试用例

## 📚 学习资源

### 项目相关
- [JDK 实现代码](install/retrieval_flow_builder/jdk_flow_builder.py) - 最佳参考
- [架构设计文档](README_ENHANCED.md) - 了解整体设计
- [测试代码](test/) - 学习如何编写测试

### 技术相关
- [Python 官方文档](https://docs.python.org/3/)
- [pytest 文档](https://docs.pytest.org/)
- [requests 库文档](https://docs.python-requests.org/)

## ❓ 常见问题

### Q: 我需要多深的 Python 知识？
A: 中级 Python 知识即可。如果你熟悉函数、类、异常处理和基本文件操作，就可以开始贡献。

### Q: 如何获取帮助？
A: 可以在相关 Issue 中提问，或者查看现有代码作为参考。

### Q: 我的 Pull Request 会被接受吗？
A: 只要你的代码符合规范、有适当的测试、解决了明确的问题，我们很乐意接受。

### Q: 我可以实现什么环境类型？
A: 任何开发环境都可以！Node.js、Python、Go、Rust、Ruby、PHP 等等。

## 📞 联系与支持

- **项目维护者**: Anfioo
- **GitHub**: [https://github.com/Anfioo/WingEnv](https://github.com/Anfioo/WingEnv)
- **邮箱**: 3485977506@qq.com

---

**感谢你考虑为 WingEnv 做出贡献！** 🎉

你的每一行代码都将帮助成千上万的开发者更高效地管理他们的开发环境。让我们一起构建更好的开发工具生态系统！

*"优秀的工具让优秀的开发者更加出色"*