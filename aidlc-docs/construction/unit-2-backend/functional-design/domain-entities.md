# Unit 2: Backend — Domain Entities (ORM Models)

## SQLAlchemy ORM 模型

### Skill
```python
class Skill(Base):
    __tablename__ = "skills"
    
    id: int                      # PK, auto-increment
    name: str                    # unique, indexed
    description: str
    version: str | None
    tags: str                    # JSON string (list[str])，兼容 SQLite/PG
    git_url: str
    git_ref: str | None
    commit_hash: str
    skill_path: str              # Skill 在仓库中的相对路径
    readme_content: str          # SKILL.md 原始内容
    readme_html: str             # 渲染后的 HTML
    source: str                  # "internal" | "external"
    author_id: int               # FK → users.id
    installs: int                # 安装计数，默认 0
    created_at: datetime
    updated_at: datetime
```

### MCPServer
```python
class MCPServer(Base):
    __tablename__ = "mcp_servers"
    
    id: int                      # PK
    name: str                    # unique, indexed
    description: str
    version: str | None
    tags: str                    # JSON string (list[str])
    transport: str               # "stdio" | "sse" | "streamable-http"
    config: str                  # JSON string — 完整 MCP 配置（兼容 SQLite/PG）
    author_id: int               # FK → users.id
    installs: int
    created_at: datetime
    updated_at: datetime
```

### AgentConfig
```python
class AgentConfig(Base):
    __tablename__ = "agent_configs"
    
    id: int                      # PK
    name: str                    # unique, indexed
    description: str
    tags: str                    # JSON string (list[str])
    prompt: str                  # Agent system prompt
    embedded_skills: str         # JSON string — 内嵌 Skills 快照列表（兼容 SQLite/PG）
    embedded_mcps: str           # JSON string — 内嵌 MCP 配置快照列表（兼容 SQLite/PG）
    git_url: str | None
    git_ref: str | None
    commit_hash: str | None
    author_id: int               # FK → users.id
    installs: int
    created_at: datetime
    updated_at: datetime
```

### User
```python
class User(Base):
    __tablename__ = "users"
    
    id: int                      # PK
    username: str                # unique, indexed
    display_name: str | None
    email: str                   # unique
    role: str                    # "user" | "admin"
    api_key_hash: str | None     # bcrypt hash
    is_active: bool              # 默认 True
    created_at: datetime
    updated_at: datetime
```

### InstallLog
```python
class InstallLog(Base):
    __tablename__ = "install_logs"
    
    id: int                      # PK
    asset_type: str              # "skill" | "mcp" | "agent"
    asset_id: int
    user_id: int                 # FK → users.id
    agent_type: str              # "kiro" | "claude-code" | ...
    installed_at: datetime
```

### SyncSource
```python
class SyncSource(Base):
    __tablename__ = "sync_sources"
    
    id: int                      # PK
    git_url: str                 # 外部源 Git URL
    sync_interval: int           # 同步间隔（秒）
    last_synced_at: datetime | None
    last_commit_hash: str | None # 上次同步的 commit
    is_active: bool
    created_by: int              # FK → users.id (admin)
    created_at: datetime
```

## 数据库索引

| 表 | 索引 | 类型 | 用途 | 兼容性 |
|---|------|------|------|--------|
| skills | name | UNIQUE | 按名称查找 | SQLite ✓ PG ✓ |
| skills | (name, description) | - | LIKE 搜索 | SQLite ✓ PG ✓ |
| mcp_servers | name | UNIQUE | 按名称查找 | SQLite ✓ PG ✓ |
| agent_configs | name | UNIQUE | 按名称查找 | SQLite ✓ PG ✓ |
| users | username | UNIQUE | 登录 | SQLite ✓ PG ✓ |
| users | api_key_hash | INDEX | API Key 认证 | SQLite ✓ PG ✓ |
| install_logs | (asset_type, asset_id) | INDEX | 统计查询 | SQLite ✓ PG ✓ |

> **注意**: tags 字段使用 JSON string 存储，不使用 PG ARRAY/GIN 索引。标签筛选通过 JSON 解析 + 应用层过滤实现（数据量 < 10K 足够）。迁移到 PG 后可选择改为 ARRAY + GIN 优化。
