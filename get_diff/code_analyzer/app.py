import streamlit as st
import os
from dotenv import load_dotenv
from core.utils import parse_git_url
from core.git_provider import GitHubProvider, GitLabProvider, GiteeProvider
from core.analyzer import Analyzer
import datetime

# Load environment variables
load_dotenv()

st.set_page_config(page_title="代码分析工具 / Code Analyzer", layout="wide", initial_sidebar_state="expanded")

st.title("🕵️ 智能代码分析工具 / AI Code Analyzer")
st.markdown("### 为开发和测试人员提供的 AI 智能分析 / AI Analysis for Dev & QA")

# Sidebar for Configuration
with st.sidebar:
    st.header("⚙️ 配置 / Configuration")
    
    st.subheader("🤖 LLM 设置 / LLM Settings")
    llm_api_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
    llm_base_url = st.text_input("Base URL (可选/Optional)", value=os.getenv("OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"))
    llm_model = st.selectbox("模型名称 / Model Name", ["gemini-2.5-pro", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo", "claude-3-opus", "doubao-pro"], index=0)
    
    analysis_language = st.radio("输出语言 / Output Language", ["中文", "English"])
    
    st.subheader("🔑 Git Token (可选/Optional)")
    github_token = st.text_input("GitHub Token", value=os.getenv("GITHUB_TOKEN", ""), type="password")
    gitlab_token = st.text_input("GitLab Token", value=os.getenv("GITLAB_TOKEN", ""), type="password")
    gitee_token = st.text_input("Gitee Token", value=os.getenv("GITEE_TOKEN", ""), type="password")
    
    st.markdown("---")
    st.markdown("💡 **Tip**: Add tokens to analyze private repositories.")

# Main Input
st.markdown("#### 输入 PR/MR 链接 / Enter PR/MR Link")
url = st.text_input("", placeholder="https://github.com/owner/repo/pull/123", label_visibility="collapsed")

# Session state to store results
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

if st.button("🚀 开始分析 / Start Analysis", use_container_width=True, type="primary"):
    if not url:
        st.warning("⚠️ 请输入链接。/ Please enter a URL.")
    elif not llm_api_key:
        st.warning("⚠️ 请提供 OpenAI API Key。/ Please provide OpenAI API Key.")
    else:
        with st.spinner("⏳ 正在获取 PR 详情... / Fetching PR details..."):
            try:
                # 1. Parse URL
                parsed = parse_git_url(url)
                if not parsed:
                    st.error("❌ 链接格式无效。请使用有效的 GitHub/GitLab/Gitee PR/MR 链接。/ Invalid URL format.")
                    st.stop()
                
                # 2. Initialize Provider
                if parsed["provider"] == "github":
                    provider = GitHubProvider(token=github_token)
                elif parsed["provider"] == "gitlab":
                    provider = GitLabProvider(token=gitlab_token)
                elif parsed["provider"] == "gitee":
                    provider = GiteeProvider(token=gitee_token)
                else:
                    st.error(f"不支持的提供商: {parsed['provider']}")
                    st.stop()
                
                # 3. Fetch Data
                pr_details = provider.get_pr_details(parsed)
                diff = provider.get_diff(parsed)
                
                st.success(f"✅ 成功获取 / Successfully fetched: **{pr_details['title']}**")
                
                # Display Metadata
                with st.expander("📄 PR 详情 / PR Details", expanded=False):
                    st.markdown(f"**作者 / Author:** `{pr_details['author']}`")
                    st.markdown(f"**状态 / State:** `{pr_details['state']}`")
                    st.markdown(f"**描述 / Description:**\n\n> {pr_details.get('description', 'No description provided.')}")
                    st.text_area("Diff 预览 / Diff Preview", diff[:1000] + "\n\n...[truncated]", height=200)

                # 4. Analyze
                analyzer = Analyzer(api_key=llm_api_key, base_url=llm_base_url if llm_base_url else None, model=llm_model)
                
                with st.spinner("🧠 正在分析业务背景... / Analyzing business context..."):
                    context_analysis = analyzer.analyze_context(diff, pr_details, analysis_language)
                    
                with st.spinner("👨‍💻 正在生成代码审查... / Generating dev review..."):
                    dev_analysis = analyzer.analyze_for_dev(diff, pr_details, context_analysis, analysis_language)
                    
                with st.spinner("🧪 正在生成测试计划... / Generating QA strategy..."):
                    qa_analysis = analyzer.analyze_for_qa(diff, pr_details, context_analysis, analysis_language)
                
                # Save to session state
                st.session_state.analysis_results = {
                    "context": context_analysis,
                    "dev": dev_analysis,
                    "qa": qa_analysis,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "pr_title": pr_details['title']
                }
                        
            except Exception as e:
                st.error(f"❌ 发生错误 / Error occurred: {str(e)}")

# Display results if available in session state
if st.session_state.analysis_results:
    results = st.session_state.analysis_results
    
    st.markdown("---")
    st.info(f"**🌐 业务与功能背景分析 / Business Context**:\n\n{results['context']}")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👨‍💻 开发人员代码审查 / Dev Review")
        st.markdown(results['dev'])
            
    with col2:
        st.subheader("🧪 QA 测试策略 / QA Strategy")
        st.markdown(results['qa'])
        
    st.markdown("---")
    
    # Export functionality
    markdown_content = f"""# 代码分析报告: {results['pr_title']}
Generated at: {results['timestamp']}

## 业务与功能背景分析
{results['context']}

## 开发人员代码审查
{results['dev']}

## QA 测试策略
{results['qa']}
"""
    
    st.download_button(
        label="📥 导出 Markdown 报告 / Export Report",
        data=markdown_content,
        file_name=f"code_analysis_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.md",
        mime="text/markdown",
        use_container_width=True
    )
