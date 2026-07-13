from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "培英中学 AI 行政管理平台"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    DATABASE_URL: str = "postgresql+asyncpg://peiying:peiying123@localhost:5432/peiying_ai"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "peiying-ai-secret-key-2026"
    
    # 生产环境配置
    CORS_ORIGINS: str = "*"  # 逗号分隔的域名列表，或 * 表示全部允许
    AUTO_SEED: bool = False  # 启动时自动初始化种子数据
    
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o"
    
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    @property
    def async_database_url(self) -> str:
        """确保 DATABASE_URL 使用 asyncpg 驱动（Render/Railway 提供的是 postgresql:// 格式）"""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
