# Component Methods - 组件方法签名

## C-02: Service Layer

### SkillService
```python
class SkillService:
    async def register(self, git_url: str, git_ref: str | None, skill_path: str | None, author_id: int) -> Skill
    async def update(self, skill_id: int, git_url: str, git_ref: str | None) -> Skill
    async def get_by_id(self, skill_id: int) -> Skill | None
    async def get_by_name(self, name: str) -> Skill | None
    async def search(self, keyword: str | None, tag: str | None, page: int, size: int) -> PaginatedResult[Skill]
    async def list_top(self, limit: int) -> list[Skill]  # Leaderboard
    async def get_install_package(self, skill_id: int) -> SkillInstallPackage  # Git URL + commit + 文件内容
    async def delete(self, skill_id: int) -> None
    async def increment_installs(self, skill_id: int) -> None
```

### MCPService
```python
class MCPService:
    async def register(self, data: MCPServerCreate, author_id: int) -> MCPServer
    async def update(self, mcp_id: int, data: MCPServerUpdate) -> MCPServer
    async def get_by_id(self, mcp_id: int) -> MCPServer | None
    async def get_by_name(self, name: str) -> MCPServer | None
    async def search(self, keyword: str | None, tag: str | None, page: int, size: int) -> PaginatedResult[MCPServer]
    async def get_install_config(self, mcp_id: int, agent_type: str) -> dict  # 生成 mcp.json 片段
    async def delete(self, mcp_id: int) -> None
    async def increment_installs(self, mcp_id: int) -> None
```

### AgentConfigService
```python
class AgentConfigService:
    async def register(self, data: AgentConfigCreate, author_id: int) -> AgentConfig
    async def update(self, agent_id: int, data: AgentConfigUpdate) -> AgentConfig
    async def get_by_id(self, agent_id: int) -> AgentConfig | None
    async def search(self, keyword: str | None, tag: str | None, page: int, size: int) -> PaginatedResult[AgentConfig]
    async def get_install_package(self, agent_id: int) -> AgentInstallPackage  # 完整包：Skills + MCP + Prompt
    async def delete(self, agent_id: int) -> None
    async def increment_installs(self, agent_id: int) -> None
```

### UserService
```python
class UserService:
    async def create(self, username: str, email: str, role: str) -> User
    async def get_by_id(self, user_id: int) -> User | None
    async def get_by_api_key(self, api_key: str) -> User | None
    async def generate_api_key(self, user_id: int) -> str  # 返回明文 key，数据库存 hash
    async def list_users(self, page: int, size: int) -> PaginatedResult[User]
    async def update_role(self, user_id: int, role: str) -> User
    async def disable(self, user_id: int) -> None
```

### ImportService
```python
class ImportService:
    async def import_from_url(self, git_url: str, admin_id: int) -> list[Skill]  # 从外部 Git URL 导入
    async def list_imports(self, page: int, size: int) -> PaginatedResult[Skill]  # 列出外部导入的资产
```

### SyncService
```python
class SyncService:
    async def add_source(self, git_url: str, sync_interval: int) -> SyncSource
    async def remove_source(self, source_id: int) -> None
    async def list_sources(self) -> list[SyncSource]
    async def sync_source(self, source_id: int) -> SyncResult  # 手动触发同步
    async def run_auto_sync(self) -> None  # 定时任务入口
```

## C-04: Agent Adapter Layer

### BaseAdapter（抽象基类）
```python
class BaseAdapter(ABC):
    @abstractmethod
    def get_skills_dir(self, scope: Scope) -> Path  # workspace 或 global
    @abstractmethod
    def get_mcp_config_path(self, scope: Scope) -> Path
    @abstractmethod
    def get_agents_dir(self, scope: Scope) -> Path
    @abstractmethod
    def install_skill(self, skill_files: dict[str, str], name: str, scope: Scope, method: InstallMethod) -> None
    @abstractmethod
    def install_mcp(self, config: dict, scope: Scope) -> None
    @abstractmethod
    def install_agent_config(self, package: AgentInstallPackage, scope: Scope, method: InstallMethod) -> None
    @abstractmethod
    def get_post_install_hints(self) -> str  # 安装后提示信息
```

### KiroAdapter
```python
class KiroAdapter(BaseAdapter):
    # Skills: .kiro/skills/<name>/ (workspace) | ~/.kiro/skills/<name>/ (global)
    # MCP: .kiro/settings/mcp.json (workspace) | ~/.kiro/settings/mcp.json (global)
    # Agent: .kiro/agents/<name>.json (workspace) | ~/.kiro/agents/<name>.json (global)
    # 环境变量格式差异：IDE 用 ${VAR}，CLI 用 ${env:VAR}
```

### AdapterFactory
```python
class AdapterFactory:
    @staticmethod
    def get_adapter(agent_type: str) -> BaseAdapter
    @staticmethod
    def detect_installed_agents() -> list[str]  # 检测本地已安装的 agents
    @staticmethod
    def get_supported_agents() -> list[str]  # 返回所有支持的 agent 类型
```

## C-05: Git Integration

### GitService
```python
class GitService:
    async def clone_shallow(self, url: str, ref: str | None) -> Path  # git clone --depth 1 到临时目录
    async def discover_skills(self, repo_dir: Path) -> list[SkillInfo]  # 在仓库中发现 SKILL.md
    async def parse_skill_md(self, skill_md_path: Path) -> SkillMetadata  # 解析 YAML frontmatter
    async def get_commit_hash(self, repo_dir: Path) -> str  # 获取当前 commit hash
    async def cleanup(self, repo_dir: Path) -> None  # 清理临时目录
```

## C-08: Auth Module

### AuthDependency
```python
# FastAPI dependency
async def get_current_user(x_api_key: str = Header()) -> User
async def require_admin(user: User = Depends(get_current_user)) -> User
```
