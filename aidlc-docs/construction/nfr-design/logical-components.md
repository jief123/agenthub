# Logical Components — Skills Registry Platform

## 概述
本文档定义系统中的逻辑组件及其在 NFR 设计中的角色。这些逻辑组件将在 Infrastructure Design 阶段映射到具体的基础设施服务。

## 1. 计算组件

### LC-01: Web Application Server
- **职责**: 托管 FastAPI 应用 + React 静态文件（SPA）
- **特征**: 异步 Python（uvicorn + asyncio）
- **框架**: FastAPI >= 0.110, uvicorn[standard] >= 0.27
- **静态文件**: React 构建产物挂载在 `/app/backend/static/`，FastAPI 直接服务
- **SPA 路由**: 非 API 路由 fallback 到 `index.html`
- **资源需求**: CPU 密集度低，I/O 密集（数据库查询、Git 操作）
- **并发模型**: 单进程 + asyncio event loop（MVP）
- **扩展路径**: 多 worker（uvicorn --workers N）或多实例 + 负载均衡

### LC-02: Background Sync Worker
- **职责**: 外部源自动同步定时任务
- **特征**: 周期性执行，非实时
- **实现**: `asyncio.create_task` 内嵌在应用进程中（`sync_sources_loop`）
- **触发条件**: `SYNC_ENABLED=true`
- **执行间隔**: `SYNC_INTERVAL`（默认 86400 秒 = 1 天）
- **行为**: 遍历所有活跃 SyncSource，调用 import_service 导入资产
- **扩展路径**: 独立 worker 进程 + 消息队列（Phase 2 如需要）

## 2. 存储组件

### LC-03: Primary Database
- **职责**: 持久化所有业务数据
- **数据**: Skills, MCPServers, AgentConfigs, Users, InstallLogs, SyncSources
- **双模式**:
  - **SQLite（开发/测试/小规模）**: 单文件数据库，零依赖，`sqlite+aiosqlite:///./skills_registry.db`
  - **PostgreSQL（大规模生产）**: 关系型，支持 JSONB、ARRAY、GIN 索引，`postgresql+asyncpg://...`
- **ORM**: SQLAlchemy[asyncio] >= 2.0
- **异步驱动**: aiosqlite >= 0.20（SQLite）, asyncpg >= 0.29（PostgreSQL）
- **迁移工具**: Alembic >= 1.13（PostgreSQL）; SQLite 使用 `create_all` 自动建表
- **兼容策略**: tags 用 JSON string（非 PG ARRAY），config/embedded 字段用 JSON string（非 JSONB）
- **切换方式**: 只改 `DATABASE_URL` 环境变量
- **容量预估**: < 1GB（1000+ 资产，元数据为主）
- **备份策略**: SQLite 直接复制 .db 文件；PG 用 pg_dump
- **Docker 持久化**: `appdata` volume → `/app/backend/data/`

### LC-04: Static File Storage
- **职责**: React 构建产物（JS/CSS/HTML）
- **特征**: 只读，构建时生成
- **位置**: Docker 镜像内 `/app/backend/static/`（多阶段构建复制）
- **服务方式**: FastAPI `StaticFiles` 挂载 `/assets` + SPA fallback
- **更新方式**: 重新构建镜像

## 3. 网络组件

### LC-05: API Gateway / Reverse Proxy
- **职责**: 请求路由、TLS 终止（可选）
- **MVP**: 不需要独立网关，FastAPI 直接暴露 8000 端口
- **生产建议**: Nginx 反向代理（TLS + 静态文件加速 + 请求限流）
- **扩展路径**: K8s Ingress Controller

### LC-06: Internal Network
- **职责**: 应用与数据库之间的通信（PostgreSQL 模式）
- **实现**: Docker Compose 默认网络（bridge）
- **安全**: 数据库端口不对外暴露（仅内部网络可达）
- **SQLite 模式**: 无需网络通信（数据库内嵌）

## 4. 安全组件

### LC-07: Authentication Provider
- **双认证模式**:
  - **JWT Bearer Token**: 前端 Web UI 使用，HS256 算法，24h 过期，pyjwt >= 2.8
  - **API Key**: CLI / 自动化使用，"sr_" 前缀，bcrypt hash 存储
  - **ADMIN_API_KEY**: 环境变量快捷通道，启动时自动创建 admin 用户
- **密码认证**: bcrypt hash（bcrypt >= 4.1），用于 Web 登录
- **Phase 2**: SSO/LDAP/OIDC 集成（当前未实现）
- **接口**: FastAPI Dependency Injection（get_current_user, get_optional_user, require_admin）

### LC-08: Secrets Management
- **MVP**: 环境变量（.env 文件 + Docker Compose `${VAR:-default}` 语法）
- **敏感数据**: SECRET_KEY（JWT 签名）, ADMIN_API_KEY, ADMIN_PASSWORD, DATABASE_URL
- **生产建议**: Docker Secrets 或 K8s Secrets
- **原则**: 不在代码或镜像中硬编码任何密钥
- **注意**: 默认值（dev-secret-key, admin123）仅用于开发环境

## 5. 可观测性组件

### LC-09: Logging
- **实现**: Python `logging` 标准库，`logging.basicConfig(level=settings.LOG_LEVEL)`
- **级别**: `LOG_LEVEL` 环境变量控制（默认 INFO）
- **输出**: stdout（Docker 标准实践）
- **关键日志**: 启动、admin 创建、同步任务执行、错误
- **收集**: Docker 日志驱动 → 外部日志系统（运维层面配置）

### LC-10: Health Monitoring
- **实现**: `GET /health` → `{"status": "ok"}`
- **当前范围**: 简单存活检查（不检查数据库连接）
- **Docker 集成**: healthcheck 配置（python urllib, 30s 间隔, 5s 超时, 3 次重试）
- **消费者**: Docker Compose healthcheck / K8s liveness probe

## 6. 分发组件

### LC-11: Docker Image
- **Docker Hub**: `jief123/agenthub`
- **多架构**: amd64 + arm64
- **构建**: 多阶段（node:20-alpine → python:3.12-slim）
- **内容**: FastAPI 后端 + React 前端 + shared 包

### LC-12: CLI Package
- **PyPI 包名**: `agenthub-cli`
- **入口命令**: `agenthub-cli`
- **技术栈**: typer >= 0.12, httpx >= 0.27, rich >= 13.0
- **认证方式**: API Key（X-API-Key header）

## 组件依赖关系

```
LC-01 (App Server)
  ├── depends on → LC-03 (Database)
  ├── serves → LC-04 (Static Files)
  ├── protected by → LC-07 (Auth Provider)
  └── reports to → LC-09 (Logging)

LC-02 (Sync Worker)
  ├── depends on → LC-03 (Database)
  └── runs inside → LC-01 (App Server, asyncio task)

LC-05 (API Gateway)
  └── routes to → LC-01 (App Server)

LC-06 (Internal Network)
  └── connects → LC-01 ↔ LC-03 (PostgreSQL 模式)

LC-10 (Health)
  └── checks → LC-01

LC-12 (CLI)
  └── calls → LC-01 (via HTTP + API Key)
```

## 逻辑组件 → 基础设施映射预览

| 逻辑组件 | MVP（Docker Compose） | 生产（K8s） |
|---------|---------------------|------------|
| LC-01 App Server | Docker container (python:3.12-slim) | K8s Deployment + HPA |
| LC-02 Sync Worker | 内嵌在 App Server (asyncio task) | 独立 K8s CronJob |
| LC-03 Database | SQLite 文件 (appdata volume) | RDS PostgreSQL / K8s StatefulSet |
| LC-04 Static Files | Docker 镜像内 (/app/backend/static/) | CDN / S3 + CloudFront |
| LC-05 API Gateway | 无（直接暴露 :8000） | K8s Ingress + ALB |
| LC-06 Internal Network | Docker bridge network | K8s Service mesh |
| LC-07 Auth Provider | 内置 JWT + API Key | JWT + API Key + OIDC |
| LC-08 Secrets | .env + Docker Compose | K8s Secrets / AWS Secrets Manager |
| LC-09 Logging | stdout + docker logs | CloudWatch / ELK |
| LC-10 Health | /health endpoint + Docker healthcheck | K8s probes |
| LC-11 Docker Image | jief123/agenthub (Docker Hub) | ECR / Docker Hub |
| LC-12 CLI Package | PyPI agenthub-cli | PyPI agenthub-cli |
