<div align="center">

# ACE-PyQt

<img src="https://socialify.git.ci/Cassianvale/ACE-PyQt/image?font=Raleway&language=1&name=1&pattern=Signal&theme=Light" alt="ACE-PyQt" width="640" height="320" />

<!-- 项目状态徽章 -->
<div>
    <img alt="python" src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white">
    <img alt="license" src="https://img.shields.io/badge/License-GPL--3.0-green?style=flat-square&logo=gnu">
    <img alt="version" src="https://img.shields.io/github/v/release/Cassianvale/ACE-PyQt?style=flat-square&color=orange&logo=github">
    <img alt="platform" src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square">
</div>

<div align="left">

> **现代化的 PyQt6 桌面应用程序开发框架**
> 基于 [ACE-KILLER](https://github.com/Cassianvale/ACE-KILLER) 项目重构，提供完整的桌面应用开发解决方案

</div>

</div>

## 📖 简介

ACE-PyQt 是一个功能完整的 PyQt6 桌面应用程序开发框架，采用现代化的架构设计和最佳实践。该框架提供了开发桌面应用程序所需的核心功能，包括配置管理、日志系统、主题切换、系统通知等，让开发者能够快速构建专业的桌面应用程序。

## ✨ 核心特性

### 🎨 用户界面

- [x] **现代化 UI 设计** - 基于 PyQt6 的现代化界面
- [x] **明暗主题切换** - 支持浅色/深色主题动态切换
- [x] **响应式布局** - 自适应窗口大小调整
- [x] **自定义组件** - 丰富的自定义 UI 组件库

### ⚙️ 系统功能

- [x] **配置管理** - 基于 YAML 的灵活配置系统
- [x] **日志系统** - 基于 Loguru 的高性能日志记录
- [x] **系统通知** - 跨平台的系统通知支持
- [x] **托盘支持** - 完整的系统托盘功能
- [x] **开机自启** - 支持开机静默自启动
- [x] **版本更新** - 自动检查和提示版本更新

### 🔧 开发特性

- [x] **模块化架构** - 基于管理器模式的清晰架构
- [x] **类型提示** - 完整的 Python 类型注解
- [x] **文档完善** - 详细的代码文档和使用指南
- [x] **自动构建** - GitHub Actions 自动构建和发布

## 🚀 快速开始

### 环境要求

- Python 3.10 或更高版本
- PyQt6 6.9.0 或更高版本
- Windows 10/11（推荐）、macOS 或 Linux

### 安装步骤

1. **克隆项目**

   ```bash
   git clone https://github.com/Cassianvale/ACE-PyQt.git
   cd ACE-PyQt
   ```

2. **创建虚拟环境**（推荐）

   ```bash
   python -m venv venv

   # Windows
   .\venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   # 使用 pip
   pip install -r requirements.txt

   # 或使用国内镜像源（推荐）
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

   # 或使用 uv（更快）
   uv sync
   ```

4. **运行应用**
   ```bash
   python main.py
   ```

### 配置说明

应用程序的配置文件位于 `config/app_config.py`，包含以下主要配置项：

- **应用信息**：名称、版本、作者等基本信息
- **默认配置**：通知、日志、主题等用户可配置项
- **系统配置**：目录名称、超时时间等系统级配置

详细配置说明请参考 [配置文档](docs/README.md)。

## 📦 构建和打包

### 开发环境测试打包

```bash
# 基础打包（生成多文件）
pyinstaller --noconsole --add-data "assets/icon/*;assets/icon" main.py

# 单文件打包（仅用于测试）
pyinstaller --noconsole --add-data "assets/icon/*;assets/icon" --onefile main.py
```

> ⚠️ **注意**：`--onefile` 选项仅适用于开发测试，生产环境请使用多文件打包以获得更好的性能和兼容性。

### 生产环境构建

项目配置了 GitHub Actions 自动构建流程，每次发布新版本时会自动构建 Windows 可执行文件。

## 📁 项目结构

```
ACE-PyQt/
├── assets/                 # 资源文件
│   ├── font/              # 字体文件
│   └── icon/              # 图标文件
├── config/                # 配置模块
│   ├── app_config.py      # 应用配置
│   └── config_manager.py  # 配置管理器
├── docs/                  # 文档目录
├── ui/                    # 用户界面模块
│   ├── components/        # UI 组件
│   ├── handlers/          # 事件处理器
│   ├── managers/          # UI 管理器
│   ├── styles/            # 样式文件
│   └── main_window.py     # 主窗口
├── utils/                 # 工具模块
│   ├── logger.py          # 日志工具
│   ├── notification.py    # 通知工具
│   ├── system_utils.py    # 系统工具
│   └── version_checker.py # 版本检查
├── main.py               # 程序入口
├── requirements.txt      # 依赖列表
└── pyproject.toml       # 项目配置
```

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 GPL-3.0 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - 强大的 Python GUI 框架
- [Loguru](https://github.com/Delgan/loguru) - 优雅的 Python 日志库
- [ACE-KILLER](https://github.com/Cassianvale/ACE-KILLER) - 原始项目基础

## 📞 联系方式

- 作者：Cassianvale
- 项目主页：[https://github.com/Cassianvale/ACE-PyQt](https://github.com/Cassianvale/ACE-PyQt)
- 问题反馈：[Issues](https://github.com/Cassianvale/ACE-PyQt/issues)

---

<div align="center">

**如果这个项目对您有帮助，请给它一个 ⭐️**

</div>
