# 智能代码分析工具 (Code Analysis Tool)

这是一个基于 AI 的智能代码分析平台，专为**开发人员**和**测试人员 (QA)** 设计。它能够自动分析 GitHub Pull Requests 和 GitLab Merge Requests，提供代码审查建议、功能影响分析以及测试策略推荐。

## 🌟 核心功能

- **多平台支持**: 无缝集成 GitHub 和 GitLab。
- **双视角深度分析**:
  - **👨‍💻 开发人员视角**: 自动化代码审查，关注代码质量、潜在 Bug、安全风险及性能优化。
  - **🧪 测试人员视角**: 智能分析业务影响范围，评估风险等级，自动生成回归测试与新功能测试策略。
- **业务背景感知**: AI 会首先分析代码变更的业务领域与功能背景，从而提供更具针对性的见解。
- **后台自动监控**: 提供后台服务持续监控指定仓库，发现新 PR/MR 时自动触发分析并生成报告。
- **报告管理**: 支持在线查看及下载 Markdown 格式的详细分析报告。

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装 Python 3.8+。

### 2. 安装依赖

```bash
pip install -r code_analyzer/requirements.txt
```

### 3. 配置

在 `code_analyzer` 目录下创建一个 `.env` 文件（可参考 `.env.example`），配置以下必要的环境变量：

```ini
# 必须配置
OPENAI_API_KEY=your_api_key_here
# 如果使用 Google Gemini 或其他兼容接口，请配置 Base URL
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/

# 监控功能必须配置
MONITOR_REPO_URL=https://github.com/owner/repo

# 可选配置
GITHUB_TOKEN=your_github_token
GITLAB_TOKEN=your_gitlab_token
CHECK_INTERVAL=600  # 监控检查间隔（秒），默认 600
LLM_MODEL=gemini-2.5-pro # 默认模型
```

### 4. 运行应用

#### 🖥️ 启动 Web 界面 (Streamlit)

用于单次手动分析和查看已生成的报告。

```bash
streamlit run code_analyzer/app.py
```

#### 🤖 启动后台监控服务

用于持续监控仓库并自动生成报告。建议在独立的终端或后台进程中运行。

```bash
python code_analyzer/monitor.py
```

## 📖 使用指南

### 方式一：单次手动分析
1. 打开 Web 界面。
2. 切换到 **"🔍 单次分析"** 标签页。
3. 输入 GitHub PR 或 GitLab MR 的完整链接。
4. 点击 **"开始分析"**，等待 AI 生成报告。
5. 分析完成后，可直接下载 Markdown 报告。

### 方式二：后台自动监控
1. 确保 `.env` 中已配置 `MONITOR_REPO_URL`。
2. 运行 `python code_analyzer/monitor.py`。
3. 服务将每隔 10 分钟检查一次新 PR。
4. 发现新 PR 后，会自动进行分析并将报告保存在 `reports/` 目录下。
5. 您可以在 Web 界面的 **"📊 已生成的分析报告"** 标签页中查看和下载这些报告。

## 📂 目录结构

```text
code_analyzer/
├── app.py                 # Streamlit Web 应用入口
├── monitor.py             # 后台监控服务脚本
├── requirements.txt       # 项目依赖
├── reports/               # 自动生成的报告存储目录
├── core/                  # 核心逻辑模块
│   ├── analyzer.py        # AI 分析与报告生成
│   ├── git_provider.py    # GitHub/GitLab API 适配器
│   └── utils.py           # 通用工具函数
└── .env.example           # 环境变量配置示例
```

## ❓ 常见问题

- **Q: 为什么无法识别我的 PR 链接？**
  - A: 请确保使用的是浏览器地址栏中的完整 URL，例如 `https://github.com/owner/repo/pull/123`。
- **Q: 监控服务报错 "Invalid repository URL"？**
  - A: 请检查 `.env` 中的 `MONITOR_REPO_URL` 是否正确，它应该是仓库的主页链接，不包含 `/pulls` 等后缀。
