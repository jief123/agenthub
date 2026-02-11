# Unit 5: Docker — Deployment Design

## Docker Compose 架构

```yaml
# docker-compose.yml（生产模式，使用 PostgreSQL）
services:
  app:        # FastAPI + React 静态文件
    build: .
    ports: ["8000:8000"]
    depends_on: [db]
    environment:
      - DATABASE_URL=postgresql+asyncpg://skills:${POSTGRES_PASSWORD}@db:5432/skills_registry
      - SECRET_KEY=${SECRET_KEY}
      - ADMIN_API_KEY=${ADMIN_API_KEY}
    volumes:
      - skill-cache:/app/.skills-registry/cache

  db:         # PostgreSQL（生产模式）
    image: postgres:16-alpine
    ports: ["5432:5432"]
    environment:
      - POSTGRES_DB=skills_registry
      - POSTGRES_USER=skills
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
  skill-cache:
```

> **开发/测试模式**: 不需要 Docker Compose，直接 `uvicorn app.main:app --reload`，使用 SQLite（`DATABASE_URL=sqlite+aiosqlite:///./skills_registry.db`）。

## Dockerfile（多阶段构建）

```
# Stage 1: 前端构建
FROM node:20-alpine AS frontend-build
COPY frontend/ .
RUN npm ci && npm run build

# Stage 2: 后端运行
FROM python:3.12-slim
RUN apt-get update && apt-get install -y git  # Git 用于克隆仓库
COPY backend/ .
COPY shared/ .
COPY --from=frontend-build /dist ./static/
RUN pip install .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 启动流程

```
docker compose up
  1. PostgreSQL 启动
  2. FastAPI 启动:
     a. 运行 Alembic 迁移（自动）
     b. 创建初始 admin 用户（如果 ADMIN_API_KEY 环境变量设置）
     c. 启动 API 服务
     d. 启动定时同步任务（如果配置了同步源）
  3. 访问 http://localhost:8000
```

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| DATABASE_URL | 是 | - | PostgreSQL 连接字符串 |
| SECRET_KEY | 是 | - | 应用密钥 |
| ADMIN_API_KEY | 否 | - | 初始管理员 API Key（首次启动时创建） |
| ADMIN_USERNAME | 否 | admin | 初始管理员用户名 |
| ADMIN_EMAIL | 否 | admin@local | 初始管理员邮箱 |
| GIT_SSH_KEY | 否 | - | SSH 私钥（访问私有 Git 仓库） |
| SYNC_ENABLED | 否 | false | 是否启用自动同步 |
