import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers import auth, suppliers, inventory, templates, dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化数据库表
    await init_db()
    
    # 生产环境：自动初始化种子数据
    if settings.AUTO_SEED:
        from app.seed import auto_seed
        await auto_seed()
    
    yield

app = FastAPI(
    title="培英中学 Steven AI 行政助手",
    description="Steven 的 3 项需求：标书/报价单生成、供应商搜索、库存计算",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 配置（支持环境变量配置）
origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=(origins != ["*"]),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== API 路由 ==========
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["供应商管理"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["库存管理"])
app.include_router(templates.router, prefix="/api/templates", tags=["标书与文书生成"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["仪表盘"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# ========== 静态文件服务（生产环境）==========
# 生产环境中，前端构建产物会被复制到 ./static 目录
# FastAPI 同时提供 API 和前端页面，用户只需访问一个地址
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(static_dir):
    # 挂载静态资源目录（Vite 构建的 CSS/JS/图片等）
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    # SPA 回退：所有非 API 路由返回 index.html（支持 Vue Router 的 history 模式）
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        # 尝试返回请求的静态文件（如 favicon.ico）
        file_path = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        # 其他路由返回 SPA 入口文件（交给 Vue Router 处理）
        index_path = os.path.join(static_dir, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Not Found")
else:
    # 开发环境：根路径返回 API 信息
    @app.get("/")
    async def root():
        return {
            "message": "Steven AI 行政助手 API",
            "version": "0.1.0",
            "scope": "Steven 的 3 项需求",
            "docs": "/docs",
            "note": "前端开发服务器请访问 http://localhost:3000",
        }
