# AgentHub — AI Agent Skills Registry 平台设计

## 1. 背景与目标

### 1.1 问题分析

当前 AI Agent 生态中存在三类可复用资产：
- **Skills**：领域知识和工作流程（SKILL.md + 辅助脚本 + 参考文档）
- **MCP Server**：工具调用能力的配置（transport、command、args、env）
- **Agent 配置**：prompt + Skills + MCP 的组合包（面向业务场景的完整配置）

Skills 是最适合在团队/组织内共享的资产——本质是配置文件，不绑定运行环境，任何开发者都可以将最佳实践打包分享。

### 1.2 目标

构建可私有化部署的 Skills Registry 平台（AgentHub），实现：
- 开发者可以将 Skills、MCP Server 配置、Agent 配置发布到内部平台
- 其他开发者可以搜索、浏览、一键安装
- 兼容 Anthropic Agent Skills 开放标准和 skills.sh 生态
- 三种资产类型统一管理和分发
- 单容器部署，可运行在客户私有网络

## 2. 核心概念

### 2.1 Skill 标准格式（兼容 Agent Skills 开放标准）

```
my-skill/
├── SKILL.md          # 核心文件：YAML frontmatter + 指令内容
├── scripts/          # 可选：辅助脚本
│   └── extract.py
├── references/       # 可选：参考文档
│   └── api-guide.md
└── resources/        # 可选：模板、配置等静态资源
    └── template.yaml
```

SKILL.md 格式：
```yaml
---
name: my-skill
description: 这个 Skill 做什么，什么时候用
version: 1.0.0
author: zhangsan
tags: [react, performance, frontend]
compatibility:
  agents: [claude-code, cursor, kiro]
---

# My Skill

具体指令内容...
```

### 2.2 MCP Server 注册格式

通过 API 注册，核心字段：
- `name`：唯一标识
- `description`：描述
- `transport`：传输方式（stdio / sse / streamable-http）
- `config`：JSON 配置（command、args、env 等），直接对应 `mcp.json` 中的 `mcpServers` 格式

### 2.3 Agent 配置格式

Agent 配置是 Skills + MCP 的组合包：
- `name`：唯一标识
- `prompt`：系统提示词
- `embedded_skills`：内嵌的 Skill 列表（含文件内容）
- `embedded_mcps`：内嵌的 MCP Server 配置列表

安装时一次性部署 prompt、Skills 文件和 MCP 配置。

## 3. 系统架构

```
┌──────────────────────────────────────────────────────────┐
│                     客户私有网络                           │
│                                                          │
│  ┌───────────────────────────────────────────────────┐   │
│  │          单容器 (jief123/agenthub)                  │   │
│  │                                                   │   │
│  │  ┌──────────┐    ┌──────────────┐                 │   │
│  │  │  React   │    │   FastAPI    │                 │   │
│  │  │  静态文件  │◀──│   后端服务    │                 │   │
│  │  │ (Vite 构建)│    │  (Uvicorn)  │                 │   │
│  │  └──────────┘    └──────┬───────┘                 │   │
│  │                         │                         │   │
│  │                  ┌──────┴───────┐                 │   │
│  │                  │  SQLAlchemy  │                 │   │
│  │                  │  (异步 ORM)   │                 │   │
│  │                  └──────┬───────┘                 │   │
│  │                         │                         │   │
│  │                  ┌──────┴───────┐                 │   │
│  │                  │   SQLite /   │                 │   │
│  │                  │  PostgreSQL  │                 │   │
│  │                  └──────────────┘                 │   │
│  └───────────────────────────────────────────────────┘   │
│                         ▲                                │
│           ┌─────────────┼─────────────┐                  │
│           │             │             │                  │
│     ┌─────┴────┐  ┌─────┴────┐  ┌─────┴────┐           │
│     │  Web UI  │  │   CLI    │  │ 后台同步   │           │
│     │ (浏览器)  │  │agenthub  │  │ (Git 源)  │           │
│     │          │  │  -cli    │  │          │           │
│     └──────────┘  └──────────┘  └──────────┘           │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │          JWT + API Key 双认证                      │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### 3.1 组件说明

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| Web UI | React 18 + Vite + TailwindCSS 4 | 浏览、搜索、管理的前端 SPA |
| API Server | Python 3.12 + FastAPI + Uvicorn | RESTful API，处理注册/搜索/分发 |
| ORM | SQLAlchemy 2.0 (async) | 异步数据库访问层 |
| 数据库 | SQLite（默认）/ PostgreSQL（生产） | 存储元数据、用户、统计数据 |
| 数据库迁移 | Alembic | 生产环境 schema 迁移 |
| CLI | Python + Typer + Rich + httpx | 开发者本地工具，发布和安装资产 |
| 认证 | JWT（前端）+ API Key（CLI） | 双路径认证，bcrypt 哈希 |
| 容器 | Docker 多阶段构建 | 前后端打包为单镜像 |

### 3.2 单容器架构

采用多阶段 Docker 构建，将前端和后端打包到同一个镜像中：
1. 第一阶段：Node.js 构建 React 前端静态文件
2. 第二阶段：Python 运行时，安装 shared 包和后端依赖，拷入前端构建产物

FastAPI 同时提供 API 路由和静态文件服务：
- `/api/v1/*` 路由由 FastAPI 路由处理
- `/health` 健康检查端点
- 其他路径回退到 React SPA 的 `index.html`

## 4. 认证与授权

### 4.1 双路径认证

系统支持两种认证方式，由 `get_current_user` 依赖统一处理：

**JWT Bearer Token（前端使用）：**
- 用户通过 `/api/v1/auth/login` 用邮箱+密码登录，获取 JWT
- 也支持 `/api/v1/auth/register` 自助注册
- Token 有效期 24 小时，通过 `Authorization: Bearer <token>` 传递
- 使用 HS256 算法，密钥为环境变量 `SECRET_KEY`

**API Key（CLI / 自动化使用）：**
- 格式为 `sr_` 前缀 + 随机 token（如 `sr_abc123...`）
- 通过 `X-API-Key` Header 传递
- 密钥使用 bcrypt 哈希存储在数据库中
- 支持环境变量 `ADMIN_API_KEY` 直接匹配（初始管理员）

### 4.2 RBAC 权限

两个角色：
- `user`：浏览、安装、发布自己的资产
- `admin`：全部权限 + 用户管理 + 导入 + 同步源管理

管理员通过 `require_admin` 依赖保护管理端点。

## 5. 数据模型

使用 SQLAlchemy 2.0 Mapped Column 风格，所有主键为自增整数 ID。

### 5.1 Skills 表

```python
class Skill(Base):
    __tablename__ = "skills"

    id: int              # 自增主键
    name: str            # 唯一，最长 64 字符
    description: str     # 描述
    version: str | None  # 版本号
    tags: str            # JSON 序列化的标签列表
    git_url: str         # 源码 Git 地址
    git_ref: str | None  # 分支/tag
    commit_hash: str     # 发布时的 commit SHA
    skill_path: str      # 仓库内路径
    readme_content: str  # SKILL.md 原始内容
    readme_html: str     # 渲染后的 HTML
    source: str          # "internal" 或 "synced"
    author_id: int       # 外键 → users.id
    installs: int        # 安装计数
    created_at: datetime
    updated_at: datetime
```

### 5.2 MCP Server 表

```python
class MCPServer(Base):
    __tablename__ = "mcp_servers"

    id: int              # 自增主键
    name: str            # 唯一，最长 64 字符
    description: str
    version: str | None
    tags: str            # JSON 序列化
    transport: str       # stdio / sse / streamable-http
    config: str          # JSON 序列化的配置（command, args, env）
    author_id: int       # 外键 → users.id
    installs: int
    created_at: datetime
    updated_at: datetime
```

### 5.3 Agent 配置表

```python
class AgentConfig(Base):
    __tablename__ = "agent_configs"

    id: int              # 自增主键
    name: str            # 唯一，最长 64 字符
    description: str
    tags: str            # JSON 序列化
    prompt: str          # 系统提示词
    embedded_skills: str # JSON 序列化的 Skill 列表
    embedded_mcps: str   # JSON 序列化的 MCP 配置列表
    git_url: str | None
    git_ref: str | None
    commit_hash: str | None
    author_id: int       # 外键 → users.id
    installs: int
    created_at: datetime
    updated_at: datetime
```

### 5.4 用户表

```python
class User(Base):
    __tablename__ = "users"

    id: int              # 自增主键
    username: str        # 唯一
    display_name: str | None
    email: str           # 唯一
    role: str            # "user" 或 "admin"
    password_hash: str | None  # bcrypt 哈希
    api_key_hash: str | None   # bcrypt 哈希
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### 5.5 安装记录表

```python
class InstallLog(Base):
    __tablename__ = "install_logs"

    id: int              # 自增主键
    asset_type: str      # "skill" | "mcp" | "agent"
    asset_id: int        # 对应资产的 ID
    user_id: int         # 外键 → users.id
    agent_type: str      # "kiro" / "claude-code" / "cursor" 等
    installed_at: datetime
```

### 5.6 同步源表

```python
class SyncSource(Base):
    __tablename__ = "sync_sources"

    id: int
    git_url: str           # Git 仓库地址
    sync_interval: int     # 同步间隔（秒）
    last_synced_at: datetime | None
    last_commit_hash: str | None
    is_active: bool
    created_by: int        # 外键 → users.id
    created_at: datetime
```

## 6. API 设计

所有 API 路由前缀为 `/api/v1`。

### 6.1 Skills

```
GET    /api/v1/skills                    # 列表（支持 keyword/tag/page/size）
GET    /api/v1/skills/top                # 按安装量排序的热门列表
GET    /api/v1/skills/{id}               # 详情
POST   /api/v1/skills                    # 发布（需认证）
DELETE /api/v1/skills/{id}               # 删除（需 admin）
GET    /api/v1/skills/{id}/install       # 获取安装包（文件内容）
POST   /api/v1/skills/{id}/install       # 记录安装（统计）
```

### 6.2 MCP Servers

```
GET    /api/v1/mcps                      # 列表
GET    /api/v1/mcps/top                  # 热门列表
GET    /api/v1/mcps/{id}                 # 详情
POST   /api/v1/mcps                      # 注册（需认证）
DELETE /api/v1/mcps/{id}                 # 删除（需 admin）
GET    /api/v1/mcps/{id}/install         # 获取安装配置
POST   /api/v1/mcps/{id}/install         # 记录安装
```

### 6.3 Agent 配置

```
GET    /api/v1/agents                    # 列表
GET    /api/v1/agents/top                # 热门列表
GET    /api/v1/agents/{id}               # 详情
POST   /api/v1/agents                    # 注册（需认证）
DELETE /api/v1/agents/{id}               # 删除（需 admin）
GET    /api/v1/agents/{id}/install       # 获取安装包
POST   /api/v1/agents/{id}/install       # 记录安装
```

### 6.4 认证

```
POST   /api/v1/auth/register             # 注册（用户名+邮箱+密码）
POST   /api/v1/auth/login                # 登录（邮箱+密码 → JWT）
POST   /api/v1/auth/api-key              # 生成 API Key（需认证）
GET    /api/v1/users/me                  # 当前用户信息
GET    /api/v1/users/me/published        # 我发布的资产
GET    /api/v1/users/me/installed        # 我安装的资产
GET    /api/v1/users/me/stats            # 发布统计
POST   /api/v1/users/me/api-key/regenerate  # 重新生成 API Key
```

### 6.5 搜索

```
GET    /api/v1/search?q=keyword&type=skill|mcp|agent&tag=xxx
```

跨资产类型统一搜索，返回按类型分组的结果。

### 6.6 管理（需 admin）

```
GET    /api/v1/admin/users               # 用户列表
PUT    /api/v1/admin/users/{id}/role     # 修改角色
PUT    /api/v1/admin/users/{id}/disable  # 禁用用户
POST   /api/v1/admin/import              # 从 Git URL 导入资产
GET    /api/v1/admin/assets              # 所有资产列表
DELETE /api/v1/admin/assets/{type}/{id}  # 删除任意资产
GET    /api/v1/admin/sync-sources        # 同步源列表
POST   /api/v1/admin/sync-sources        # 添加同步源
DELETE /api/v1/admin/sync-sources/{id}   # 删除同步源
POST   /api/v1/admin/sync-sources/{id}/sync  # 手动触发同步
```

## 7. CLI 功能

CLI 工具名为 `agenthub-cli`，通过 PyPI 安装：`pip install agenthub-cli`。

配置文件存储在 `~/.agenthub/config.toml`。

### 7.1 命令一览

```bash
# 配置
agenthub-cli config set registry.url http://your-server:8000
agenthub-cli config set registry.api_key sr_your-key
agenthub-cli config show

# Skills
agenthub-cli publish                  # 从当前目录发布（读取 SKILL.md）
agenthub-cli find [keyword]           # 搜索（跨所有资产类型）
agenthub-cli add <name>               # 安装 Skill（支持 --agent/--method/--scope）
agenthub-cli list                     # 列出本地已安装的 Skills
agenthub-cli remove <name>            # 卸载 Skill

# MCP Server
agenthub-cli mcp list                 # 列出可用 MCP Server
agenthub-cli mcp add <name>           # 安装 MCP 配置到本地 mcp.json

# Agent 配置
agenthub-cli agent list               # 列出可用 Agent 配置
agenthub-cli agent add <name>         # 安装完整 Agent 配置（Skills + MCP + prompt）
```

### 7.2 安装机制

- Skill 安装支持 `copy`（复制文件）和 `symlink`（符号链接）两种方式
- 支持 `workspace`（当前项目）和 `global`（用户级）两种作用域
- 通过 `AdapterFactory` 适配不同 Agent（kiro、claude-code、cursor 等）
- MCP 安装直接写入对应 Agent 的 `mcp.json` 配置
- Agent 配置安装一次性部署 Skills 文件 + MCP 配置

## 8. 后台同步

支持从外部 Git 仓库自动同步资产：
- 管理员通过 API 添加同步源（Git URL）
- 后台任务按 `SYNC_INTERVAL`（默认 86400 秒 = 1 天）定期拉取
- 自动解析仓库中的 SKILL.md 文件并导入
- 也支持通过 `/api/v1/admin/import` 手动触发一次性导入

## 9. 部署方案

### 9.1 Docker 部署（推荐）

```yaml
# docker-compose.yml
services:
  app:
    image: jief123/agenthub:latest    # 多架构：amd64 + arm64
    ports:
      - "8000:8000"
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
    volumes:
      - appdata:/app/backend/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 5s
      retries: 3

volumes:
  appdata:
```

单容器，单端口（8000），前后端一体。

### 9.2 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./skills_registry.db` | 数据库连接串（支持 SQLite 和 PostgreSQL） |
| `SECRET_KEY` | `change-me-in-production` | JWT 签名密钥 |
| `ADMIN_API_KEY` | 无 | 初始管理员 API Key（设置后自动创建管理员） |
| `ADMIN_USERNAME` | `admin` | 管理员用户名 |
| `ADMIN_PASSWORD` | `admin123` | 管理员密码 |
| `ADMIN_EMAIL` | `admin@localhost.dev` | 管理员邮箱 |
| `SYNC_ENABLED` | `false` | 是否启用后台同步 |
| `SYNC_INTERVAL` | `86400` | 同步间隔（秒） |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `GIT_CLONE_TIMEOUT` | `60` | Git 克隆超时（秒） |
| `GIT_MAX_CONCURRENT` | `5` | 最大并发 Git 操作数 |

### 9.3 PostgreSQL 生产部署

将 `DATABASE_URL` 改为 PostgreSQL 连接串即可：
```
DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/agenthub
```

使用 Alembic 管理数据库迁移。

### 9.4 Docker 镜像

- 镜像名：`jief123/agenthub`
- 多架构支持：`linux/amd64` + `linux/arm64`
- 基础镜像：`python:3.12-slim`
- 内置 `git` 用于仓库克隆和导入

## 10. 技术栈总结

| 层 | 技术 | 说明 |
|----|------|------|
| 前端 | React 18 + Vite + TailwindCSS 4 | SPA，react-router-dom 路由，react-markdown 渲染 |
| 后端 | Python 3.12 + FastAPI + Uvicorn | 异步 API 服务 |
| ORM | SQLAlchemy 2.0 (async) + Alembic | 异步 ORM + 数据库迁移 |
| 数据库 | SQLite (aiosqlite) / PostgreSQL (asyncpg) | 开发用 SQLite，生产用 PostgreSQL |
| CLI | Python + Typer + Rich + httpx | PyPI 包名 `agenthub-cli` |
| 共享包 | agenthub-shared | Schema 定义、解析器、Agent 适配器 |
| 认证 | PyJWT + bcrypt | JWT Token + API Key 双认证 |
| 容器 | Docker 多阶段构建 | 单镜像 `jief123/agenthub` |
| Markdown | markdown + rehype-highlight | 后端渲染 HTML，前端语法高亮 |

## 11. 与外部生态的兼容性

### 11.1 兼容 skills.sh

- SKILL.md 格式遵循 Agent Skills 开放标准
- 管理员可添加同步源，从外部 Git 仓库（包括 skills.sh 生态）自动导入

### 11.2 兼容多 Agent

通过 `AdapterFactory` 适配不同 Agent 的安装路径和配置格式：
- 支持 kiro、claude-code、cursor 等 Agent
- 按各 Agent 约定路径安装（如 `.kiro/skills/`、`.claude/skills/`）
- MCP 配置写入对应 Agent 的 `mcp.json`

### 11.3 三种资产统一管理

与 skills.sh 的关键区别：

| 维度 | skills.sh | AgentHub |
|------|-----------|----------|
| 部署 | SaaS（Vercel 托管） | 私有化部署（单 Docker 容器） |
| 资产类型 | 仅 Skills | Skills + MCP Server + Agent 配置 |
| 认证 | 无 | JWT + API Key |
| 安装方式 | Git clone | API 分发（文件内容直接返回） |
| CLI | `skills`（Node.js） | `agenthub-cli`（Python / PyPI） |
| 网络 | 公网 | 可纯内网运行 |
