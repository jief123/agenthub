# Unit 1: Shared — Domain Entities

## Pydantic Schemas（API 请求/响应模型）

### Skill Schemas
```python
class SkillCreate(BaseModel):
    name: str                    # 从 SKILL.md frontmatter 提取
    description: str             # 从 SKILL.md frontmatter 提取
    version: str | None          # 从 metadata.version 提取
    tags: list[str]              # 用户指定或从 SKILL.md 提取
    git_url: str                 # Git 仓库 URL
    git_ref: str | None          # 分支/tag，默认 main
    commit_hash: str             # 当前 commit hash
    skill_path: str              # Skill 在仓库中的相对路径
    readme_content: str          # SKILL.md 完整内容

class SkillResponse(BaseModel):
    id: int
    name: str
    description: str
    version: str | None
    tags: list[str]
    git_url: str
    git_ref: str | None
    commit_hash: str
    skill_path: str
    readme_html: str             # 渲染后的 HTML
    author: UserBrief
    installs: int
    source: str                  # "internal" | "external"
    created_at: datetime
    updated_at: datetime

class SkillInstallPackage(BaseModel):
    name: str
    git_url: str
    commit_hash: str
    skill_path: str
    files: dict[str, str]        # 相对路径 → 文件内容
```

### MCP Server Schemas
```python
class MCPServerCreate(BaseModel):
    name: str
    description: str
    version: str | None
    tags: list[str]
    transport: str               # "stdio" | "sse" | "streamable-http"
    command: str                 # 如 "uvx"
    args: list[str]             # 如 ["awslabs.aws-documentation-mcp-server@latest"]
    env: dict[str, str]         # 环境变量
    auto_approve: list[str]     # 自动批准的工具列表

class MCPServerResponse(BaseModel):
    id: int
    name: str
    description: str
    version: str | None
    tags: list[str]
    transport: str
    config: dict                 # 完整 MCP 配置
    author: UserBrief
    installs: int
    created_at: datetime
    updated_at: datetime

class MCPInstallConfig(BaseModel):
    name: str
    config: dict                 # mcp.json 片段: { "mcpServers": { name: {...} } }
    env_vars_needed: list[str]   # 需要用户配置的环境变量列表
```

### Agent Config Schemas
```python
class AgentConfigCreate(BaseModel):
    name: str
    description: str
    tags: list[str]
    prompt: str                  # Agent 的 system prompt
    embedded_skills: list[EmbeddedSkill]   # 内嵌的 Skills 快照
    embedded_mcps: list[EmbeddedMCP]       # 内嵌的 MCP 配置快照
    git_url: str | None          # 可选，Agent 配置文件的 Git URL
    git_ref: str | None
    commit_hash: str | None

class EmbeddedSkill(BaseModel):
    name: str
    description: str
    files: dict[str, str]        # 相对路径 → 文件内容

class EmbeddedMCP(BaseModel):
    name: str
    config: dict                 # 完整 MCP Server 配置

class AgentConfigResponse(BaseModel):
    id: int
    name: str
    description: str
    tags: list[str]
    prompt: str
    embedded_skills: list[EmbeddedSkill]
    embedded_mcps: list[EmbeddedMCP]
    author: UserBrief
    installs: int
    created_at: datetime
    updated_at: datetime

class AgentInstallPackage(BaseModel):
    name: str
    prompt: str
    embedded_skills: list[EmbeddedSkill]
    embedded_mcps: list[EmbeddedMCP]
```

### User Schemas
```python
class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str | None
    email: str
    role: str                    # "user" | "admin"
    created_at: datetime

class UserBrief(BaseModel):
    id: int
    username: str
    display_name: str | None

class APIKeyResponse(BaseModel):
    api_key: str                 # 明文，仅在生成时返回一次
    message: str
```

### Common Schemas
```python
class PaginatedResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int

class SearchRequest(BaseModel):
    q: str | None
    type: str | None             # "skill" | "mcp" | "agent"
    tag: str | None
    page: int = 1
    size: int = 20
```

## Adapter 接口定义

```python
class Scope(str, Enum):
    WORKSPACE = "workspace"
    GLOBAL = "global"

class InstallMethod(str, Enum):
    SYMLINK = "symlink"
    COPY = "copy"
```

## SKILL.md 解析器输出

```python
class SkillMetadata(BaseModel):
    name: str
    description: str
    version: str | None
    license: str | None
    compatibility: str | None
    metadata: dict[str, Any]     # 其他 key-value（author, tags 等）
    body: str                    # frontmatter 之后的 Markdown 内容
```
