# Component Dependency - 组件依赖关系与通信模式

## 依赖矩阵

```
                 API Layer  Service  Data  Adapter  Git  Frontend  CLI  Auth
API Layer           -         ✓       -      -       -      -       -    ✓
Service Layer       -         -       ✓      ✓       ✓      -       -    -
Data Layer          -         -       -      -       -      -       -    -
Adapter Layer       -         -       -      -       -      -       -    -
Git Integration     -         -       -      -       -      -       -    -
Frontend (React)    ✓         -       -      -       -      -       -    -
CLI Tool            ✓         -       -      ✓       -      -       -    -
Auth Module         -         -       ✓      -       -      -       -    -
```

## 依赖关系说明

### 后端内部依赖（分层架构）
```
API Layer (Routes)
    │
    ├── depends on → Auth Module（认证中间件）
    │
    └── calls → Service Layer（业务逻辑）
                    │
                    ├── calls → Data Layer / Repositories（数据访问）
                    │
                    ├── calls → Git Integration（外部源导入时）
                    │
                    └── calls → Adapter Layer（生成安装指令时）
```

### 前端 → 后端
```
React SPA ──HTTP/JSON──► FastAPI /api/v1/*
```
- 前端通过 RESTful API 与后端通信
- 前端静态文件由 FastAPI 托管（同一容器）
- 认证：请求头携带 API Key

### CLI → 后端 + 本地
```
CLI Tool ──HTTP/JSON──► FastAPI /api/v1/*  （搜索、注册、获取安装包）
    │
    └── local ──► Adapter Layer（本地文件操作：安装 Skills/MCP/Agent）
```
- CLI 是纯 API 客户端（数据操作走 API）
- CLI 本地持有 Adapter Layer 副本（执行文件放置）
- CLI 和后端共享 Adapter 接口定义（Python 包共享）

## 数据流

### 写入流（注册/发布）
```
CLI/Web → API Route → Service → Repository → PostgreSQL
                         │
                         └→ GitService（验证 Git URL 可达性，可选）
```

### 读取流（搜索/浏览）
```
CLI/Web → API Route → Service → Repository → PostgreSQL
                                    │
                                    └→ ILIKE 查询
```

### 安装流
```
CLI → API Route → Service → Repository（获取元数据）
                     │
                     └→ GitService（浅克隆，读取文件）
                            │
                            └→ 返回文件内容给 CLI
                                    │
CLI ← ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
 │
 └→ AdapterFactory → KiroAdapter → 本地文件系统
```

## 共享代码策略

### 后端与 CLI 共享的代码
- **Pydantic Models**: API 请求/响应模型（CLI 用于序列化/反序列化）
- **Adapter 接口**: BaseAdapter + KiroAdapter（CLI 本地执行安装）
- **SKILL.md 解析器**: YAML frontmatter 解析逻辑

### 项目结构（Monorepo）
```
skills-registry/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── routes/       # API 路由
│   │   ├── services/     # 业务逻辑
│   │   ├── models/       # ORM 模型
│   │   ├── repositories/ # 数据访问
│   │   ├── auth/         # 认证模块
│   │   └── main.py       # FastAPI app
│   ├── migrations/       # Alembic
│   └── pyproject.toml
├── cli/                  # CLI 工具
│   ├── skills_registry/
│   │   ├── commands/     # Typer 命令
│   │   ├── client.py     # API 客户端
│   │   └── config.py     # CLI 配置
│   └── pyproject.toml
├── shared/               # 共享代码
│   ├── schemas/          # Pydantic 模型
│   ├── adapters/         # Agent Adapter
│   ├── parsers/          # SKILL.md 解析
│   └── pyproject.toml
├── frontend/             # React 前端
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 通信协议

| 通信路径 | 协议 | 格式 | 认证 |
|---------|------|------|------|
| Frontend → Backend | HTTP | JSON (REST) | API Key (Header) |
| CLI → Backend | HTTP | JSON (REST) | API Key (Header) |
| Backend → PostgreSQL | TCP | SQL (SQLAlchemy) | 连接字符串 |
| Backend → Git Repos | SSH/HTTPS | Git Protocol | SSH Key / Token |
| CLI → Local FS | - | 文件操作 | - |
