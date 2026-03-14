import os
from openai import OpenAI

class Analyzer:
    def __init__(self, api_key, base_url=None, model="gpt-4o"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def _call_llm(self, system_prompt, user_content):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error during analysis: {str(e)}"

    def analyze_context(self, diff, pr_details):
        system_prompt = """
        你是一位经验丰富的技术专家。请根据提供的代码变更（Diff）和 PR 详情，分析以下内容：
        1. **业务领域**: 这个仓库可能属于什么业务领域（例如：电商、社交、金融、基础设施等）？
        2. **功能定位**: 本次变更主要涉及什么具体功能或模块？
        
        请用中文简要回答。
        """
        user_content = f"""
        Title: {pr_details['title']}
        Description: {pr_details['description']}
        
        Diff:
        {diff[:10000]} 
        """
        return self._call_llm(system_prompt, user_content)

    def analyze_for_dev(self, diff, pr_details, context):
        system_prompt = f"""
        你是一位高级软件工程师，正在进行代码审查。
        
        **背景信息**:
        {context}
        
        请结合上述业务和功能背景，分析提供的代码变更（Diff）和 PR 详情。
        
        你的输出必须使用中文，并遵循以下结构：
        1. **摘要**: 简要概述变更内容。
        2. **代码质量**: 关于代码风格、可读性和最佳实践的评论。
        3. **潜在问题**: Bug、性能瓶颈或安全风险（请结合业务场景考虑）。
        4. **建议**: 具体的改进建议。
        
        请保持简洁但具体。如果可能，请引用具体的代码片段。
        """
        
        user_content = f"""
        Title: {pr_details['title']}
        Description: {pr_details['description']}
        
        Diff:
        {diff[:15000]} # Truncate to avoid token limits if necessary
        """
        
        return self._call_llm(system_prompt, user_content)

    def analyze_for_qa(self, diff, pr_details, context):
        system_prompt = f"""
        你是一位首席 QA 工程师，正在分析代码变更以确定测试策略。
        
        **背景信息**:
        {context}
        
        请结合上述业务和功能背景，分析提供的代码变更（Diff）和 PR 详情。
        
        你的输出必须使用中文，并遵循以下结构：
        1. **影响分析**: 哪些功能或模块可能受到影响？（请结合业务链路分析）
        2. **风险评估**: 低/中/高风险及其原因。
        3. **测试范围**:
           - **回归测试**: 需要验证哪些现有功能？
           - **新测试**: 应该覆盖哪些新场景？
        4. **边界情况**: 需要测试的具体棘手场景（结合业务规则）。
        
        请关注功能影响而不是代码语法。
        """
        
        user_content = f"""
        Title: {pr_details['title']}
        Description: {pr_details['description']}
        
        Diff:
        {diff[:15000]} # Truncate to avoid token limits if necessary
        """
        
        return self._call_llm(system_prompt, user_content)
