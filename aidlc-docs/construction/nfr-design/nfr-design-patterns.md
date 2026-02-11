# NFR Design Patterns — Skills Registry Platform

## 1. 认证与安全模式

### 1.1 API Key 认证模式（MVP）
```
请求流:
  Client → X-API-Key Header → FastAPI Dependency → bcrypt verify → User Context

设计:
  - API Key 格式: "sr_" + token_urlsafe(32)
  - 存储: bcrypt hash（不存储明文）
  - 查找优化: 对 api_key_hash 建索引，遍历活跃用户验证
  - 生命周期: 用户可重新生成（旧 Key 立即失效）
```

### 1.2 RBAC 权限模式
```
角色:
  - user: 浏览、搜索、安装、发布自己的资产
  - admin: 全部权限（管理所有资产、用户管理、外部源配置）

实现:
  - FastAPI Dependency Injection:
    - get_current_user → 所有认证接口
    - require_admin → 管理接口
  - 路由级别权限检查，不在 Service 层重复校验
```

### 1.3 安全防护
```
措施:
  - CORS: 仅允许同源请求（后端托管前端，默认安全）
  - SQL 注入: SQLAlchemy ORM 参数化查询
  - XSS: SKILL.md 渲染使用安全 Markdown 库（禁用 raw HTML 或白名单过滤）
  - Git 操作: 临时目录隔离 + 超时控制（60s）+ 操作后清理
  - 敏感数据: API Key 仅在生成时返回一次，数据库只存 hash
  - 审计日志: InstallLog 记录所有安装行为
```

## 2. 性能模式

### 2.1 搜索性能
```
策略: SQL LIKE + 索引优化（SQLite/PG 通用）

实现:
  - name, description 字段 LIKE 搜索（大小写不敏感通过 LOWER() 实现）
  - tags 字段 JSON string 存储，应用层解析过滤（数据量 < 10K 足够）
  - 默认按 installs DESC 排序（Leaderboard）
  - 分页: OFFSET/LIMIT（数据量 < 10K，无需 cursor 分页）
  - 迁移到 PG 后可启用 GIN 索引 + ILIKE 优化

目标: < 500ms（1000+ 资产规模）
```

### 2.2 Git 操作性能
```
策略: 浅克隆 + 临时目录 + 超时控制

实现:
  - git clone --depth 1（只拉最新 commit）
  - --single-branch（只拉指定分支）
  - 临时目录: tempfile.mkdtemp()
  - 超时: 60 秒硬限制
  - 操作完成后立即清理临时目录

优化:
  - skill-cache volume 缓存已克隆的仓库（Docker 持久化）
  - 安装时复用缓存（如果 commit_hash 未变）
```

### 2.3 数据库连接
```
策略: 双数据库引擎支持

SQLite 模式（开发/测试）:
  - DATABASE_URL=sqlite+aiosqlite:///./skills_registry.db
  - 零依赖，无需安装数据库
  - 单文件存储，方便备份和重置
  - aiosqlite 提供异步支持

PostgreSQL 模式（生产）:
  - DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
  - 异步连接池: pool_size=10, max_overflow=20
  - 连接回收: pool_recycle=3600

切换方式: 只改 DATABASE_URL 环境变量，代码零改动
```

## 3. 可靠性模式

### 3.1 错误处理
```
分层错误处理:
  - API Layer: FastAPI exception_handler 统一格式化错误响应
  - Service Layer: 业务异常（AssetNotFound, DuplicateName, GitCloneError）
  - Data Layer: 数据库异常捕获和转换

HTTP 错误码:
  - 400: 参数校验失败
  - 401: 未认证
  - 403: 权限不足
  - 404: 资源不存在
  - 409: 名称冲突
  - 500: 内部错误（Git 操作失败等）
```

### 3.2 Git 操作容错
```
策略:
  - 克隆失败: 返回明确错误信息（URL 不可达、认证失败、超时）
  - 文件发现失败: 返回空列表 + 警告
  - 临时目录: finally 块确保清理
  - 并发控制: asyncio.Semaphore 限制同时进行的 Git 操作数（默认 5）
```

### 3.3 数据库迁移
```
策略: Alembic 自动迁移

实现:
  - 应用启动时自动运行 alembic upgrade head
  - 迁移脚本版本控制
  - 回滚支持: alembic downgrade
```

## 4. 可观测性模式

### 4.1 日志
```
策略: 结构化日志（MVP 简单方案）

实现:
  - Python logging + structlog（可选）
  - 日志级别: INFO（默认）, DEBUG（开发）
  - 关键操作日志: 注册、安装、导入、认证失败
  - 输出: stdout（Docker 标准实践）
```

### 4.2 健康检查
```
端点:
  - GET /health → { "status": "ok", "db": "connected" }
  - Docker Compose healthcheck 配置
  - 检查数据库连接可用性
```

## 5. 可扩展性模式

### 5.1 Agent Adapter 扩展
```
模式: 简单工厂 + 抽象基类

扩展方式:
  1. 继承 BaseAdapter
  2. 实现 get_skill_path(), get_mcp_config_path(), get_agent_config_path()
  3. 实现 merge_mcp_config(), format_env_var()
  4. 在 AdapterFactory 注册

当前实现: KiroAdapter（MVP）
预留扩展: ClaudeCodeAdapter, CursorAdapter, WindsurfAdapter
```

### 5.2 认证扩展
```
MVP → Phase 2 路径:
  - MVP: API Key（X-API-Key header）
  - Phase 2: OIDC via Authlib
    - FastAPI middleware 切换
    - CLI: OAuth2 Device Flow
    - 向后兼容: API Key 仍可用
```
