import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers import auth, suppliers, inventory, templates, dashboard

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")

class SPAMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if response.status_code == 404:
            path = request.url.path
            if not path.startswith("/api") and not path.startswith("/docs") and not path.startswith("/health") and not path.startswith("/openapi"):
                index = os.path.join(STATIC_DIR, "index.html")
                if os.path.isfile(index):
                    return FileResponse(index)
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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

origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=(origins != ["*"]),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["供应商管理"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["库存管理"])
app.include_router(templates.router, prefix="/api/templates", tags=["标书与文书生成"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["仪表盘"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if os.path.isdir(STATIC_DIR):
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    app.add_middleware(SPAMiddleware)
else:
    @app.get("/")
    async def root():
        return {
            "message": "Steven AI 行政助手 API",
            "version": "0.1.0",
            "scope": "Steven 的 3 项需求",
            "docs": "/docs",
        }