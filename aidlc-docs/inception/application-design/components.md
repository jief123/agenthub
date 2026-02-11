# Components - 组件定义与职责

## 系统架构概览

```
┌─────────────────────────────────────────────────────┐
│                    Docker Container                  │
│                                                      │
│  ┌──────────────┐    ┌───────────────────────────┐  │
│  │  React SPA   │    │      FastAPI Backend       │  │
│  │  (静态文件)   │◄──│  /api/*  → API Routes      │  │
│  │  /*  → index  │    │  /static → React Build     │  │
│  └──────────────┘    │                             │  │
│                      │  ┌─────────────────────┐   │  │
│                      │  │   Service Layer      │   │  │
│                      │  │  ┌───────────────┐   │   │  │
│                      │  │  │ SkillService   │   │   │  │
│                      │  │  │ MCPService     │   │   │  │
│                      │  │  │ AgentService   │   │   │  │
│                      │  │  │ UserService    │   │   │  │
│                      │  │  │ ImportService  │   │   │  │
│                      │  │  └───────────────┘   │   │  │
│                      │  └─────────────────────┘   │  │
│                      │                             │  │
│                      │  ┌─────────────────────┐   │  │
│                      │  │   Adapter Layer      │   │  │
│                      │  │  ┌───────────────┐   │   │  │
│                      │  │  │ AgentAdapter   │   │   │  │
│                      │  │  │ (Factory)      │   │   │  │
│                      │  │  │  └─ KiroAdapter │   │   │  │
│                      │  │  └───────────────┘   │   │  │
│                      │  └─────────────────────┘   │  │
│                      │                             │  │
│                      │  ┌─────────────────────┐   │  │
│                      │  │   Data Layer         │   │  │
│                      │  │  SQLAlchemy + Alembic│   │  │
│                      │  └─────────┬───────────┘   │  │
│                      └────────────┼───────────────┘  │
│                                   │                   │
│  ┌────────────────────────────────▼────────────────┐ │
│  │              PostgreSQL                          │ │
│  └──────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘

┌──────────────────────┐
│   Python CLI (uvx)   │
│   skills-registry    │──── HTTP ────► FastAPI /api/*
│                      │
│  ┌────────────────┐  │
│  │ AgentAdapter   │  │
│  │ (本地文件操作)  │  │
│  │  └─ KiroAdapter│  │
│  └────────────────┘  │
└──────────────────────┘
```

## 组件定义

### C-01: API Layer（FastAPI Routes）
- **职责**: HTTP 请求路由、参数校验、响应序列化
- **技术**: FastAPI + Pydantic
- **子模块**:
  - `routes/skills.py` — Skills CRUD + 搜索
  - `routes/mcps.py` — MCP Server 配置 CRUD + 搜索
  - `routes/agents.py` — Agent 配置 CRUD + 搜索
  - `routes/users.py` — 用户管理 + 认证
  - `routes/admin.py` — 管理后台 API
  - `routes/install.py` — 安装相关 API（获取安装包）

### C-02: Service Layer（业务逻辑）
- **职责**: 核心业务逻辑编排，不直接操作数据库
- **子模块**:
  - `SkillService` — Skill 注册、更新、搜索、获取安装包
  - `MCPService` — MCP Server 配置注册、更新、搜索
  - `AgentConfigService` — Agent 配置注册、更新、搜索、打包
  - `UserService` — 用户注册、API Key 管理、认证
  - `ImportService` — 外部源导入（从 Git URL 拉取并解析 SKILL.md）
  - `SyncService` — 外部源自动同步（定时任务）

### C-03: Data Layer（数据访问）
- **职责**: 数据库 CRUD 操作、ORM 模型定义
- **技术**: SQLAlchemy（async） + Alembic
- **子模块**:
  - `models/` — ORM 模型（Skill, MCPServer, AgentConfig, User, InstallLog）
  - `repositories/` — 数据访问层（每个实体一个 Repository）
  - `migrations/` — Alembic 迁移脚本

### C-04: Agent Adapter Layer（横切组件）
- **职责**: 抽象不同 IDE/Agent 产品的文件路径和配置格式差异
- **设计**: 简单工厂模式
- **位置**: 后端（生成安装指令）+ CLI（执行本地文件操作）
- **子模块**:
  - `AdapterFactory` — 根据 agent 名称返回对应 Adapter
  - `BaseAdapter` — 抽象基类，定义统一接口
  - `KiroAdapter` — Kiro IDE/CLI 的具体实现（MVP 唯一 Adapter）

### C-05: Git Integration（Git 操作）
- **职责**: 从 Git 仓库拉取文件、解析 SKILL.md
- **技术**: 系统 `git` 命令（`git clone --depth 1`）
- **功能**:
  - 浅克隆仓库到临时目录
  - 从仓库中发现和提取 SKILL.md
  - 解析 YAML frontmatter 提取元数据
  - 清理临时目录

### C-06: React Frontend（前端 SPA）
- **职责**: 用户界面
- **技术**: React + Vite + TypeScript
- **页面**:
  - 首页（Leaderboard + 搜索）
  - 资产列表页（分类浏览）
  - 资产详情页（SKILL.md 渲染 + 安装命令）
  - 个人中心（我发布的 / 我安装的）
  - 管理后台（资产管理、用户管理、外部源配置）
  - 登录页（API Key 认证）

### C-07: CLI Tool（命令行工具）
- **职责**: 开发者本地操作入口
- **技术**: Python + Typer + httpx
- **设计**: 纯 API 客户端，所有数据操作通过后端 API
- **本地操作**: 通过 Agent Adapter 执行文件放置（安装）
- **命令组**:
  - `skills publish` — 注册/更新 Skill
  - `skills add/remove/list/find/update` — Skill 安装管理
  - `skills mcp add/list` — MCP 配置安装
  - `skills agent add/list/init/publish` — Agent 配置管理
  - `skills config` — CLI 配置（Registry URL, API Key）

### C-08: Auth Module（认证模块）
- **职责**: API Key 认证、权限校验
- **MVP**: API Key 认证（Header: `X-API-Key`）
- **RBAC**: user / admin 两个角色
- **实现**: FastAPI Dependency Injection
