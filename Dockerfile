# ============================================================
# 生产环境 Dockerfile - 单服务部署（前端+后端合为一个服务）
# 适用于 Render / Railway / VPS 等平台
# ============================================================

# ---- 第 1 阶段：构建前端 ----
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ---- 第 2 阶段：后端 + 前端静态文件 ----
FROM python:3.11-slim
WORKDIR /app

# 安装系统依赖（精简版，不需要 opencv/paddleocr 的依赖）
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY backend/requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# 复制后端代码
COPY backend/app/ ./app/

# 复制前端构建产物到 static 目录
COPY --from=frontend-builder /frontend/dist ./static

ENV PYTHONPATH=/app
ENV DEBUG=false

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
