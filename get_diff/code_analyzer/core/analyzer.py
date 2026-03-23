import os
from openai import OpenAI
import json
from .utils import retry

class Analyzer:
    def __init__(self, api_key, base_url=None, model="gpt-4o", temperature=0.7, max_retries=3):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries

    def _call_llm(self, system_prompt, user_content):
        @retry(exceptions=(Exception,), tries=self.max_retries, delay=2, backoff=2)
        def _do_call():
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ]
            )
            return response.choices[0].message.content
            
        try:
            return _do_call()
        except Exception as e:
            return f"Error during analysis after {self.max_retries} retries: {str(e)}"

    def _call_llm_stream(self, system_prompt, user_content):
        """Returns a generator for streaming responses."""
        @retry(exceptions=(Exception,), tries=self.max_retries, delay=2, backoff=2)
        def _do_call_stream():
            return self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                stream=True
            )
            
        try:
            response_stream = _do_call_stream()
            for chunk in response_stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n[Stream Error: {str(e)}]"

    def analyze_context(self, diff, pr_details, language="中文", stream=False):
        lang_instruction = "请用中文回答" if language == "中文" else "Please answer in English"
        system_prompt = f"""
        你是一位经验丰富的技术专家。请根据提供的代码变更（Diff）和 PR 详情，分析以下内容：
        1. **业务领域**: 这个仓库可能属于什么业务领域（例如：电商、社交、金融、基础设施等）？
        2. **功能定位**: 本次变更主要涉及什么具体功能或模块？
        
        {lang_instruction}，保持简明扼要。
        """
        user_content = f"""
        Title: {pr_details['title']}
        Description: {pr_details.get('description', '')}
        
        Diff:
        {diff[:10000]} 
        """
        if stream:
            return self._call_llm_stream(system_prompt, user_content)
        return self._call_llm(system_prompt, user_content)

    def analyze_for_dev(self, diff, pr_details, context, language="中文", stream=False):
        lang_instruction = "你的输出必须使用中文" if language == "中文" else "Your output must be in English"
        system_prompt = f"""
        你是一位高级软件工程师，正在进行代码审查。
        
        **背景信息**:
        {context}
        
        请结合上述业务和功能背景，分析提供的代码变更（Diff）和 PR 详情。
        
        {lang_instruction}，并遵循以下结构（使用Markdown格式）：
        1. **📌 摘要 / Summary**: 简要概述变更内容。
        2. **✨ 代码质量 / Code Quality**: 关于代码风格、可读性和最佳实践的评论。
        3. **⚠️ 潜在问题 / Potential Issues**: Bug、性能瓶颈或安全风险（请结合业务场景考虑）。
        4. **💡 建议 / Recommendations**: 具体的改进建议。
        
        请保持专业、客观，如果可能，请引用具体的代码片段进行说明。
        """
        
        user_content = f"""
        Title: {pr_details['title']}
        Description: {pr_details.get('description', '')}
        
        Diff:
        {diff[:15000]} # Truncate to avoid token limits if necessary
        """
        
        if stream:
            return self._call_llm_stream(system_prompt, user_content)
        return self._call_llm(system_prompt, user_content)

    def analyze_for_qa(self, diff, pr_details, context, language="中文", stream=False):
        lang_instruction = "你的输出必须使用中文" if language == "中文" else "Your output must be in English"
        system_prompt = f"""
        你是一位首席 QA 工程师，正在分析代码变更以确定测试策略。
        
        **背景信息**:
        {context}
        
        请结合上述业务和功能背景，分析提供的代码变更（Diff）和 PR 详情。
        
        {lang_instruction}，并遵循以下结构（使用Markdown格式）：
        1. **🎯 影响分析 / Impact Analysis**: 哪些功能或模块可能受到影响？（请结合业务链路分析）
        2. **📊 风险评估 / Risk Assessment**: 低/中/高风险及其原因。
        3. **🔬 测试范围 / Test Scope**:
           - **回归测试 / Regression**: 需要验证哪些现有功能？
           - **新功能测试 / New Tests**: 应该覆盖哪些新场景？
        4. **🚧 边界情况 / Edge Cases**: 需要测试的具体棘手场景（结合业务规则）。
        
        请关注功能影响而不是代码语法。
        """
        
        user_content = f"""
        Title: {pr_details['title']}
        Description: {pr_details.get('description', '')}
        
        Diff:
        {diff[:15000]} # Truncate to avoid token limits if necessary
        """
        
        if stream:
            return self._call_llm_stream(system_prompt, user_content)
        return self._call_llm(system_prompt, user_content)
