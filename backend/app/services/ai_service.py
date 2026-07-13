import os
from typing import Optional, List, Dict, Any
import openai
from app.config import settings

class AIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY or "demo-key",
            base_url=settings.OPENAI_BASE_URL,
        )
        self.model = settings.LLM_MODEL
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """调用 LLM 生成回复"""
        try:
            if not settings.OPENAI_API_KEY:
                return "[Demo 模式] 暂无 AI 回复，请配置 OPENAI_API_KEY"
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI 服务暂时不可用: {str(e)}"
    
    async def summarize_text(self, text: str, max_length: int = 200) -> str:
        """文本摘要"""
        messages = [
            {"role": "system", "content": f"请用不超过{max_length}字的中文概括以下内容:"},
            {"role": "user", "content": text},
        ]
        return await self.chat_completion(messages, temperature=0.3)
    
    async def classify_document(self, text: str, categories: List[str]) -> str:
        """文档分类"""
        categories_str = ", ".join(categories)
        messages = [
            {"role": "system", "content": f"请将以下文档分类到其中一个类别: {categories_str}。只返回类别名称，不要其他内容。"},
            {"role": "user", "content": text[:2000]},
        ]
        result = await self.chat_completion(messages, temperature=0.1)
        # 确保返回的是合法类别
        for cat in categories:
            if cat in result:
                return cat
        return categories[0] if categories else "其他"
    
    async def generate_document_from_template(
        self,
        template_content: str,
        variables: Dict[str, Any],
    ) -> str:
        """基于模板和变量生成文档"""
        from jinja2 import Template
        template = Template(template_content)
        return template.render(**variables)
    
    async def answer_question_with_context(
        self,
        question: str,
        context: str,
    ) -> str:
        """基于上下文回答问题 (RAG)"""
        messages = [
            {"role": "system", "content": "你是一个学校行政助手。请基于以下参考信息回答问题。如果参考信息不足以回答，请说明。\n\n参考信息:\n" + context},
            {"role": "user", "content": question},
        ]
        return await self.chat_completion(messages, temperature=0.5)
    
    async def extract_info_from_text(
        self,
        text: str,
        fields: List[str],
    ) -> Dict[str, str]:
        """从文本中提取结构化信息"""
        fields_str = ", ".join(fields)
        messages = [
            {"role": "system", "content": f"请从以下文本中提取这些信息: {fields_str}。以 JSON 格式返回。"},
            {"role": "user", "content": text[:3000]},
        ]
        result = await self.chat_completion(messages, temperature=0.1)
        # 简单解析 JSON
        try:
            import json
            # 尝试从回复中提取 JSON
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
        except:
            pass
        return {f: "" for f in fields}

ai_service = AIService()
