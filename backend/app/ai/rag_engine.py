from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import QAPair
from app.services.ai_service import ai_service

class RAGEngine:
    """检索增强生成引擎 - 用于家校沟通智能客服"""
    
    def __init__(self):
        self.top_k = 3
    
    async def retrieve_relevant_context(
        self,
        query: str,
        db: AsyncSession,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """检索相关问答对"""
        # 关键词匹配检索
        query_obj = select(QAPair)
        
        if category:
            query_obj = query_obj.where(QAPair.category == category)
        
        # 简单关键词匹配
        from sqlalchemy import or_
        keywords = query.split()
        conditions = []
        for kw in keywords:
            if len(kw) > 1:
                conditions.append(QAPair.question.ilike(f"%{kw}%"))
                conditions.append(QAPair.answer.ilike(f"%{kw}%"))
        
        if conditions:
            query_obj = query_obj.where(or_(*conditions))
        
        query_obj = query_obj.order_by(QAPair.usage_count.desc()).limit(self.top_k)
        
        result = await db.execute(query_obj)
        return [
            {
                "question": qa.question,
                "answer": qa.answer,
                "score": 0.9,
            }
            for qa in result.scalars().all()
        ]
    
    async def generate_answer(
        self,
        query: str,
        db: AsyncSession,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """RAG 完整流程：检索 + 生成"""
        # 1. 检索相关文档
        contexts = await self.retrieve_relevant_context(query, db, category)
        
        if not contexts:
            return {
                "answer": "抱歉，我暂时没有这个问题的答案。我会记录下来，稍后由人工回复您。",
                "sources": [],
                "confidence": 0.0,
            }
        
        # 2. 构建上下文
        context_text = "\n\n".join([
            f"Q: {ctx['question']}\nA: {ctx['answer']}"
            for ctx in contexts
        ])
        
        # 3. 生成回答
        answer = await ai_service.answer_question_with_context(query, context_text)
        
        return {
            "answer": answer,
            "sources": [ctx["question"] for ctx in contexts],
            "confidence": sum(ctx["score"] for ctx in contexts) / len(contexts),
        }

rag_engine = RAGEngine()
