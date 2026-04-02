# 🦅 WingEnv - 现代化开发环境管理平台

## 🚀 项目简介

WingEnv 是一个现代化的开发环境管理工具，旨在解决多版本开发环境配置的难题。**当前版本已完整实现 JDK 环境管理功能**，提供了完整的 JDK 版本切换、安装和管理解决方案。项目采用高度解耦的架构设计，为未来扩展更多环境类型（如 Node.js、Python、Go 等）奠定了坚实基础。

## ✨ 核心亮点

### 🔄 **动态环境切换**
- **多版本 JDK 管理**：无缝切换 JDK 8/11/17/21 等不同版本，解决 Java 版本碎片化问题
- **智能软链接技术**：通过符号链接实现环境变量的动态切换，彻底避免 PATH 污染问题
- **可扩展架构**：为未来支持 Node.js、Python、Go 等环境提供了完整的架构基础

### 🏗️ **高度解耦架构**
- **模块化设计**：清晰的目录结构，各功能模块高度独立，易于维护和扩展
- **构建器模式**：采用现代化的构建者模式（Builder Pattern）实现优雅的流程控制
- **插件化扩展**：新的环境类型可以轻松添加，无需修改核心代码

### 🎯 **一站式解决方案**
- **绿色安装**：所有环境均为解压即用，无需复杂配置和安装向导
- **智能下载**：自动从官方源或国内镜像站下载最新版本，支持断点续传
- **环境备份**：完整的环境变量备份与恢复功能，确保环境安全
- **优雅 UI**：基于 Rich 库的现代化命令行界面，提供出色的用户体验

## 🎮 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 基本命令
```bash
# 查看完整帮助文档
we help

# 显示项目信息和 Banner
we info

# 进入 JDK 环境管理（交互式界面）
we jdk

# 管理主题配置
we themes

# 显示二维码信息
we qr
```

### JDK 管理示例
```bash
# 进入 JDK 交互式管理界面
we jdk

# 可用命令：
#   ls      - 列出所有已安装的 JDK 版本
#   install - 安装新的 JDK 版本（智能向导）
#   set     - 切换当前使用的 JDK 版本
#   add     - 手动添加 JDK 安装路径
#   remove  - 删除指定的 JDK 版本
#   info    - 显示当前 JDK 详细信息
```

## 🏗️ 架构设计

### 构建者模式（Builder Pattern）
每个环境类型都有对应的 `RetrievalFlowBuilder`，通过链式调用实现配置流程：

```python
# JDK 安装流程示例
jdk_result = (JDKRetrievalFlowBuilder.default(os="windows", arch="x64")
              .fetch_data()          # 从网络获取可用版本
              .vendor()              # 选择厂商（Oracle、OpenJDK、GraalVM等）
              .select_ui()           # 用户交互选择
              .version()             # 选择具体版本
              .select_ui()           # 用户交互选择
              .data())               # 获取最终配置
```

### 环境管理器模式
- `BaseInstallIniManager` - 基础配置管理抽象类
- `JdksManager` - JDK 专用管理器
- `EnvsSymlinkManager` - 软链接管理器，实现环境动态切换

### 插件化架构
添加新的环境类型只需：
1. 在 `EnvsEnum` 中添加枚举值
2. 创建对应的 `RetrievalFlowBuilder`
3. 创建对应的 `InstallBuilder`
4. 创建对应的 CLI 客户端

## 📁 项目结构
```
WingEnv/
├── install/                    # 环境安装管理（核心模块）
│   ├── client/                # 命令行客户端
│   ├── install_builder/       # 环境安装构建器
│   ├── retrieval_flow_builder/# 数据检索流程构建器
│   └── configure_flow_builder/# 配置流程构建器
├── wing_utils/                # 工具库（高度复用）
│   ├── system/               # 系统工具（环境变量、路径管理）
│   ├── download/             # 下载工具（支持多线程、断点续传）
│   ├── extract/              # 解压工具（支持多种压缩格式）
│   └── ui/                   # UI 工具（基于 Rich）
├── wing_ui/                  # 用户界面组件
├── wing_client/              # 客户端框架
├── loader/                   # 加载器和配置管理
├── conf/                     # 配置文件
├── backup/                   # 备份工具
└── test/                     # 测试代码
```

## 🛠️ 当前支持的环境

| 环境 | 状态 | 描述 | 特色功能 |
|------|------|------|----------|
| **JDK** | ✅ **已完整实现** | Java 开发工具包 | 多版本切换、厂商选择、智能安装、自动配置 |
| **Node.js** | 🔄 架构已准备 | JavaScript 运行时 | *未来支持：LTS/最新版选择、镜像源切换* |
| **Python** | 🔄 架构已准备 | Python 解释器 | *未来支持：版本管理、虚拟环境集成* |
| **Go** | 🔄 架构已准备 | Go 编程语言 | *未来支持：版本管理、GOPATH 配置* |
| **Maven** | 🔄 架构已准备 | Java 项目构建工具 | *未来支持：版本管理、仓库配置* |
| **CMake** | 🔄 架构已准备 | 跨平台构建系统 | *未来支持：版本管理、工具链配置* |
| **Miniconda** | 🔄 架构已准备 | Python 环境管理 | *未来支持：环境创建、包管理* |

> **说明**：✅ 表示已完整实现，🔄 表示架构已准备，待具体实现

## 🔧 技术栈
- **Python 3.12+** - 核心编程语言
- **prompt_toolkit** - 交互式命令行界面
- **Rich** - 终端美化与表格显示
- **requests** - HTTP 请求处理
- **Pygments** - 语法高亮

## 📈 项目优势

### 当前已实现的优势（JDK 环境）
- **完整的 JDK 版本管理**：支持多版本 JDK 的安装、切换和管理
- **智能环境配置**：自动设置 JAVA_HOME 和 PATH 环境变量
- **绿色安装方案**：所有 JDK 均为解压即用，无需复杂安装向导
- **避免环境冲突**：通过软链接技术实现环境隔离，彻底解决 PATH 污染问题

### 架构设计优势（为未来扩展准备）
- **高度解耦的模块化设计**：各功能模块独立，易于维护和扩展
- **统一的构建器模式**：为新增环境类型提供了标准化的开发模式
- **插件化架构**：新的环境类型可以像插件一样轻松添加
- **可复用的工具库**：下载、解压、UI 等工具模块已高度抽象化

### 打包

> **命令**： pyinstaller -F -i favicon.ico --collect-all  rich we.py

## 🔮 未来规划
- [ ] **Docker 集成**：与 Docker 容器环境无缝集成
- [ ] **云环境同步**：云端环境配置同步和共享
- [ ] **IDE 插件**：为 VS Code、IntelliJ 等主流 IDE 提供插件支持
- [ ] **环境模板**：预定义的项目环境配置模板
- [ ] **性能监控**：环境使用情况监控和优化建议

## 🤝 参与贡献
我们欢迎任何形式的贡献！项目采用 Python 开发，逻辑清晰，易于理解和修改。

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证
本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系与支持
- **GitHub**: [https://github.com/Anfioo/WingEnv](https://github.com/Anfioo/WingEnv)
- **邮箱**: 3485977506@qq.com
- **微信**: AnfiooWork
- **Notion 笔记**: [项目文档](https://warp-cause-4c4.notion.site/2fe512a662d880889639ceef47efde0d)

---

**让开发环境管理变得简单而优雅** 🚀

*"一次配置，随处开发" - WingEnv 设计理念*