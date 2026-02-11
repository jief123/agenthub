# Infrastructure Design — Skills Registry Platform

## 1. 部署环境

### 双模式架构
- **开发/测试模式**: SQLite + 本地运行（零依赖，无需 Docker）
- **生产模式**: Docker Compose（默认 SQLite）+ 可选 PostgreSQL
- **切换方式**: 只改 `DATABASE_URL` 环境变量
- **运行环境**: 纯内网，不依赖外部云服务（外部源导入除外）
- **镜像分发**: Docker Hub `jief123/agenthub`（多架构: amd64 + arm64）
- **CLI 分发**: PyPI `agenthub-cli`

### 硬件需求
| 资源 | 开发/测试 | 生产（推荐） |
|------|---------|-------------|
| CPU | 1 core | 4 cores |
| 内存 | 1 GB | 4 GB |
| 磁盘 | 5 GB | 50 GB |
| 数据库 | SQLite（内嵌） | PostgreSQL 16（可选） |

## 2. 开发/测试模式（SQLite）

### 架构
```
┌──────────────────────────────────────────┐
│            开发者本机                      │
│                                          │
│  uvicorn app.main:app --port 8000        │
│  ┌────────────────────────────────────┐  │
│  │  FastAPI + React Static            │  │
│  │  SQLite: ./skills_registry.db      │  │
│  │  :8000                             │  │
│  └────────────────────────────────────┘  │
│                                          │
│  数据文件:                                │
│  ├── skills_registry.db  (数据库)        │
│  └── .skills-registry/cache/ (Git缓存)   │
└──────────────────────────────────────────┘
```

### 启动方式
```bash
# 安装依赖
pip install -e ./shared
pip install -e ./backend

# 前端构建（首次或前端有改动时）
cd frontend && npm ci && npm run build && cd ..

# 启动（SQLite 自动创建数据库文件）
SECRET_KEY=dev-secret \
ADMIN_API_KEY=sr_dev-admin-key \
ADMIN_PASSWORD=admin123 \
uvicorn app.main:app --reload --port 8000
```

### 优势
- 零外部依赖，不需要 Docker 或 PostgreSQL
- 数据库就是一个文件，方便备份/重置/分享
- `--reload` 支持热重载开发
- 适合单人开发、CI 测试、Demo 演示

## 3. Docker Compose 模式

### 当前架构（单服务 + SQLite）
```
┌─────────────────────────────────────────────────┐
│                 Docker Host                      │
│                                                  │
│  ┌─────────────────────────────────────────────┐│
│  │          Docker Compose                      ││
│  │                                              ││
│  │  ┌──────────────────────────────────────┐   ││
│  │  │            app container              │   ││
│  │  │  FastAPI + React Static               │   ││
│  │  │  SQLite: /app/backend/data/*.db       │   ││
│  │  │  :8000                                │   ││
│  │  └──────────────┬───────────────────────┘   ││
│  │                 │                            ││
│  │  ┌──────────────▼───────────────────────┐   ││
│  │  │         appdata volume                │   ││
│  │  │  (SQLite .db 持久化)                   │   ││
│  │  └──────────────────────────────────────┘   ││
│  └─────────────────────────────────────────────┘│
│         │                                        │
│    :8000 exposed                                 │
└─────────────────────────────────────────────────┘
```

> **说明**: 当前 `docker-compose.yml` 定义单个 `app` 服务，默认使用 SQLite。
> 如需 PostgreSQL，需自行添加 db 服务或连接外部 PG 实例。

### 服务定义

#### app 服务（当前实现）
- **镜像**: 自定义多阶段构建 或 `jief123/agenthub`
- **端口**: 8000:8000
- **数据库**: SQLite（默认），通过 `DATABASE_URL` 切换 PG
- **数据持久化**: `appdata` volume → `/app/backend/data/`
- **重启策略**: `unless-stopped`
- **健康检查**: `python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"`
- **健康检查间隔**: 30s，超时 5s，重试 3 次

#### db 服务（生产模式，需自行添加）
- **镜像**: postgres:16-alpine
- **端口**: 5432（仅内部网络，不对外暴露）
- **数据持久化**: pgdata volume
- **重启策略**: unless-stopped
- **健康检查**: pg_isready

## 4. 容器构建策略

### 多阶段 Dockerfile
```
阶段 1: frontend-build (node:20-alpine)
  - 安装前端依赖 (npm ci)
  - 构建 React 应用 (npm run build)
  - 产出: /build/dist 目录

阶段 2: backend (python:3.12-slim)
  - 安装系统依赖 (git — 用于 Git clone 操作)
  - 安装 shared 包: pip install /app/shared/
  - 安装 backend 包: pip install /app/backend/
  - 复制前端构建产物到 /app/backend/static/
  - 工作目录: /app/backend
  - 暴露端口: 8000
  - 入口: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 镜像优化
- 使用 alpine/slim 基础镜像减小体积
- 多阶段构建避免前端工具链（Node.js）进入最终镜像
- `pip install --no-cache-dir` 减小层大小
- 多架构构建: amd64 + arm64（发布到 Docker Hub）

## 5. 数据持久化

### 开发模式
| 文件 | 用途 | 备份方式 |
|------|------|---------|
| skills_registry.db | SQLite 数据库 | 直接复制文件 |

### Docker Compose 模式
| Volume | 挂载路径 | 用途 | 备份需求 |
|--------|---------|------|---------|
| appdata | /app/backend/data/ | SQLite 数据库文件 | 高（直接复制 .db 文件） |

### 生产模式（PostgreSQL）
| Volume | 用途 | 备份需求 |
|--------|------|---------|
| pgdata | PostgreSQL 数据 | 高（pg_dump 定期备份） |

## 6. 网络设计

### Docker Compose 网络
- 默认 bridge 网络
- app 服务暴露 8000 端口到宿主机
- 如添加 db 服务，数据库端口不暴露到宿主机（安全）

### 生产网络建议
```
外部访问:
  [用户] → [Nginx/Traefik 反向代理] → [app:8000]
                    │
                    └── TLS 终止
                    └── 请求限流
                    └── 静态文件缓存
```

## 7. 环境配置

### 环境变量（来源: `backend/app/config.py`）
| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| DATABASE_URL | 否 | `sqlite+aiosqlite:///./skills_registry.db` | 数据库连接字符串 |
| SECRET_KEY | 是 | `change-me-in-production` | JWT 签名密钥 |
| ADMIN_API_KEY | 否 | 无 | 管理员 API Key（设置后自动创建 admin 用户） |
| ADMIN_USERNAME | 否 | `admin` | 初始管理员用户名 |
| ADMIN_EMAIL | 否 | `admin@localhost.dev` | 初始管理员邮箱 |
| ADMIN_PASSWORD | 否 | `admin123` | 初始管理员密码（用于 Web 登录） |
| SYNC_ENABLED | 否 | `false` | 启用外部源自动同步 |
| SYNC_INTERVAL | 否 | `86400`（1天） | 同步间隔（秒） |
| LOG_LEVEL | 否 | `INFO` | 日志级别 |
| GIT_CLONE_TIMEOUT | 否 | `60` | Git clone 超时（秒） |
| GIT_MAX_CONCURRENT | 否 | `5` | 最大并发 Git 操作数 |

### docker-compose.yml 默认环境变量
```yaml
environment:
  - DATABASE_URL=sqlite+aiosqlite:///./data/skills_registry.db
  - SECRET_KEY=${SECRET_KEY:-dev-secret-key}
  - ADMIN_API_KEY=${ADMIN_API_KEY:-sr_dev-admin-key}
  - ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
  - ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}
  - ADMIN_EMAIL=${ADMIN_EMAIL:-admin@localhost.dev}
  - SYNC_ENABLED=${SYNC_ENABLED:-false}
  - SYNC_INTERVAL=${SYNC_INTERVAL:-86400}
  - LOG_LEVEL=${LOG_LEVEL:-INFO}
```

## 8. 启动与初始化流程

### 应用启动序列（`main.py` lifespan）
```
1. init_db()
   - SQLite: Base.metadata.create_all（自动建表）
   - PostgreSQL: 需提前运行 alembic upgrade head

2. init_admin()
   - 检查 ADMIN_API_KEY 是否设置
   - 如设置且 admin 用户不存在 → 自动创建
   - 创建时使用 ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD
   - API Key 和密码均 bcrypt hash 后存储

3. sync_sources_loop()（如 SYNC_ENABLED=true）
   - 启动后台 asyncio task
   - 每 SYNC_INTERVAL 秒执行一次同步
   - 遍历所有活跃 SyncSource，调用 import_service

4. 挂载静态文件
   - 检查 /app/backend/static/ 目录是否存在
   - 存在则挂载 /assets 路由 + SPA fallback
   - 不存在则跳过（纯 API 模式）

5. 日志输出: "Skills Registry started."
```

### 开发模式
```bash
pip install -e ./shared && pip install -e ./backend
cd frontend && npm ci && npm run build && cd ..
uvicorn app.main:app --reload --port 8000
# → http://localhost:8000 可访问
```

### Docker Compose 模式
```bash
docker compose up -d --build
# → http://localhost:8000 可访问
```

## 9. 运维操作

### 开发模式
```bash
# 启动
uvicorn app.main:app --reload --port 8000

# 重置数据库
rm skills_registry.db && uvicorn app.main:app

# 备份
cp skills_registry.db backup_$(date +%Y%m%d).db
```

### Docker Compose 模式
```bash
# 启动
docker compose up -d

# 查看日志
docker compose logs -f app

# 更新部署（本地构建）
docker compose up -d --build

# 更新部署（使用预构建镜像）
docker pull jief123/agenthub:latest
docker compose up -d

# 数据库备份（SQLite）
docker compose cp app:/app/backend/data/skills_registry.db ./backup.db

# 数据库备份（PostgreSQL，如使用）
docker compose exec db pg_dump -U skills skills_registry > backup.sql

# 手动运行迁移（PostgreSQL）
docker compose exec app alembic upgrade head
```

## 10. SQLite → PostgreSQL 迁移路径

```
迁移步骤:
1. 导出 SQLite 数据（自定义脚本或 pgloader）
2. 修改 DATABASE_URL 为 postgresql+asyncpg://...
3. 运行 Alembic 迁移创建 PG 表结构
4. 导入数据到 PG
5. 验证数据完整性

代码改动: 零（SQLAlchemy 抽象层处理差异）
可选优化（迁移后）:
  - tags 字段改为 PG ARRAY + GIN 索引
  - config/embedded 字段改为 JSONB
  - 搜索改为 ILIKE
```
