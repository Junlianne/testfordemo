import streamlit as st
import os
from dotenv import load_dotenv
from core.utils import parse_git_url
from core.git_provider import GitHubProvider, GitLabProvider
from core.analyzer import Analyzer

# Load environment variables
load_dotenv()

st.set_page_config(page_title="代码分析工具", layout="wide")

st.title("🕵️ 代码分析工具")
st.markdown("### 为开发和测试人员提供的 AI 智能分析")

# Sidebar for Configuration
with st.sidebar:
    st.header("配置")
    
    st.subheader("LLM 设置")
    llm_api_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
    llm_base_url = st.text_input("Base URL (可选)", value=os.getenv("OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"))
    llm_model = st.text_input("模型名称", value="gemini-2.5-pro")
    
    st.subheader("Git Token (可选)")
    github_token = st.text_input("GitHub Token", value=os.getenv("GITHUB_TOKEN", ""), type="password")
    gitlab_token = st.text_input("GitLab Token", value=os.getenv("GITLAB_TOKEN", ""), type="password")

# Main Input
url = st.text_input("请输入 GitHub PR 或 GitLab MR 链接", placeholder="https://github.com/owner/repo/pull/123")

if st.button("开始分析"):
    if not url:
        st.error("请输入链接。")
    elif not llm_api_key:
        st.error("请提供 OpenAI API Key。")
    else:
        with st.spinner("正在获取 PR 详情..."):
            try:
                # 1. Parse URL
                parsed = parse_git_url(url)
                if not parsed:
                    st.error("链接格式无效。请使用有效的 GitHub PR 或 GitLab MR 链接。")
                    st.stop()
                
                # 2. Initialize Provider
                if parsed["provider"] == "github":
                    provider = GitHubProvider(token=github_token)
                elif parsed["provider"] == "gitlab":
                    provider = GitLabProvider(token=gitlab_token)
                
                # 3. Fetch Data
                pr_details = provider.get_pr_details(parsed)
                diff = provider.get_diff(parsed)
                
                st.success(f"成功获取: {pr_details['title']}")
                
                # Display Metadata
                with st.expander("PR 详情", expanded=False):
                    st.write(f"**作者:** {pr_details['author']}")
                    st.write(f"**状态:** {pr_details['state']}")
                    st.write(f"**描述:** {pr_details['description']}")
                    st.text_area("Diff 预览", diff[:500] + "...", height=150)

                # 4. Analyze
                analyzer = Analyzer(api_key=llm_api_key, base_url=llm_base_url if llm_base_url else None, model=llm_model)
                
                with st.spinner("正在分析业务背景..."):
                    context_analysis = analyzer.analyze_context(diff, pr_details)
                    st.info(f"**业务与功能背景分析**:\n\n{context_analysis}")

                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("👨‍💻 开发人员代码审查")
                    with st.spinner("正在生成代码审查..."):
                        dev_analysis = analyzer.analyze_for_dev(diff, pr_details, context_analysis)
                        st.markdown(dev_analysis)
                        
                with col2:
                    st.subheader("🧪 QA 测试策略")
                    with st.spinner("正在生成测试计划..."):
                        qa_analysis = analyzer.analyze_for_qa(diff, pr_details, context_analysis)
                        st.markdown(qa_analysis)
                        
            except Exception as e:
                st.error(f"发生错误: {str(e)}")
