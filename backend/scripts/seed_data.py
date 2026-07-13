"""
Steven AI 行政助手 - 手动初始化种子数据
运行方式: cd backend && python scripts/seed_data.py
"""
import asyncio
import sys
import os

# 将 backend 目录加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.seed import auto_seed

if __name__ == "__main__":
    print("开始初始化种子数据...")
    asyncio.run(auto_seed())
    print("完成！")
