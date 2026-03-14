# 代码分析工具 (Code Analysis Tool)

这是一个基于 AI 的智能代码分析工具，旨在帮助**开发人员**和**测试人员 (QA)** 快速理解代码变更（Diff）并获取有价值的见解。

## 功能特点

- **多平台支持**: 支持 GitHub Pull Requests 和 GitLab Merge Requests。
- **双视角分析**:
  - **👨‍💻 开发人员视角**: 提供代码审查、代码质量评估、潜在 Bug 发现及改进建议。
  - **🧪 测试人员视角**: 分析功能影响范围、评估风险、推荐回归测试和新测试场景。
- **AI 驱动**: 利用大语言模型（如 Gemini Pro, GPT-4）进行深度语义分析。
- **中文支持**: 全中文界面与分析结果。

## 快速开始

### 1. 环境准备

确保您的系统中已安装 Python 3.8 或更高版本。

### 2. 安装依赖

在项目根目录下运行以下命令安装所需的 Python 库：

```bash
pip install -r code_analyzer/requirements.txt
```

### 3. 运行应用

使用 Streamlit 启动 Web 应用：

```bash
streamlit run code_analyzer/app.py
```

### 4. 使用说明

1.  **配置设置**:
    - 在左侧边栏输入您的 **OpenAI API Key** (或兼容的 API Key，如 Google AI)。
    - 默认配置已适配 Google Gemini 模型 (`gemini-2.5-pro`)。
    - (可选) 如果分析私有仓库，请输入 GitHub 或 GitLab Token。

2.  **开始分析**:
    - 在主输入框中粘贴 GitHub PR 或 GitLab MR 的完整链接。
    - 点击 **"开始分析"** 按钮。

3.  **查看报告**:
    - 工具将自动拉取 Diff 并生成两份报告：一份用于代码审查，一份用于测试策略。

## 常见问题

- **无法识别链接**: 请确保您使用的是包含 `/pull/` (GitHub) 或 `/merge_requests/` (GitLab) 的完整 URL。
- **API 错误**: 请检查您的 API Key 是否正确，以及是否有访问对应仓库的权限。

## 目录结构

```text
code_analyzer/
├── app.py                 # Streamlit 主程序
├── requirements.txt       # 依赖列表
└── core/
    ├── analyzer.py        # AI 分析逻辑
    ├── git_provider.py    # Git 平台接口
    └── utils.py           # 工具函数
```
