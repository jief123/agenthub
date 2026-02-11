# Unit of Work - 工作单元定义

## 拆分策略
基于 Monorepo 项目结构，按 **可独立开发和测试的包** 拆分为 5 个工作单元。
开发顺序按依赖关系排列：shared → backend → frontend → cli → docker。

---

## Unit 1: Shared Package（共享库）
- **包路径**: `shared/`
- **职责**: 后端和 CLI 共享的代码
- **内容**:
  - Pydantic schemas（API 请求/响应模型）
  - Agent Adapter 层（BaseAdapter + KiroAdapter + AdapterFactory）
  - SKILL.md 解析器（YAML frontmatter 解析）
  - 通用常量和类型定义
- **依赖**: 无外部依赖
- **预估复杂度**: 中

## Unit 2: Backend API（后端服务）
- **包路径**: `backend/`
- **职责**: FastAPI 后端，提供 RESTful API
- **内容**:
  - SQLAlchemy ORM 模型（Skill, MCPServer, AgentConfig, User, InstallLog）
  - Alembic 数据库迁移
  - Repository 层（数据访问）
  - Service 层（SkillService, MCPService, AgentConfigService, UserService, ImportService, SyncService）
  - API Routes（skills, mcps, agents, users, admin, search, install）
  - Auth 模块（API Key 认证 + RBAC）
  - Git Integration（GitService — 浅克隆、文件发现、元数据解析）
  - 静态文件托管（serve React 构建产物）
  - 定时任务（自动同步）
- **依赖**: Unit 1 (shared)
- **预估复杂度**: 高

## Unit 3: Frontend（前端 SPA）
- **包路径**: `frontend/`
- **职责**: React 用户界面
- **内容**:
  - 页面组件:
    - 首页（Leaderboard + 搜索框）
    - 资产列表页（分类浏览 + 筛选）
    - 资产详情页（SKILL.md 渲染 + 安装命令 + 统计）
    - 个人中心（我发布的 / 我安装的）
    - 管理后台（资产管理、用户管理、外部源配置、平台统计）
    - 登录/注册页
  - API 客户端层（封装 fetch 调用）
  - 路由配置（React Router）
  - 状态管理（React Context 或轻量方案）
  - Markdown 渲染（SKILL.md 详情展示）
- **依赖**: Unit 2 (backend API 接口定义)
- **预估复杂度**: 中高

## Unit 4: CLI Tool（命令行工具）
- **包路径**: `cli/`
- **职责**: 开发者本地操作入口
- **内容**:
  - Typer 命令定义:
    - `skills publish` — 注册/更新 Skill
    - `skills add/remove/list/find/update` — Skill 管理
    - `skills mcp list/add` — MCP 配置管理
    - `skills agent list/add/init/publish` — Agent 配置管理
    - `skills config` — CLI 配置（Registry URL, API Key）
  - API 客户端（httpx，调用后端 API）
  - 本地安装逻辑（通过 shared Adapter 执行文件操作）
  - 配置文件管理（`~/.skills-registry/config.toml`）
  - 交互式提示（选择 agent、确认安装等）
- **依赖**: Unit 1 (shared), Unit 2 (backend API 接口)
- **预估复杂度**: 中

## Unit 5: Docker & Deployment（部署配置）
- **包路径**: 项目根目录
- **职责**: 容器化和部署
- **内容**:
  - `Dockerfile`（多阶段构建：前端构建 → 后端 + 静态文件）
  - `docker-compose.yml`（FastAPI + PostgreSQL）
  - 环境变量配置（`.env.example`）
  - 数据库初始化脚本
  - README.md（部署文档）
- **依赖**: Unit 2 (backend), Unit 3 (frontend build)
- **预估复杂度**: 低
