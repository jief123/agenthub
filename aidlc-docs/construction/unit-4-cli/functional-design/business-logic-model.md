# Unit 4: CLI — Business Logic Model

> 包名: `agenthub-cli` (PyPI) · 可执行文件: `agenthub-cli` · 推荐运行方式: `uvx agenthub-cli`
> 版本: 0.1.1 · 依赖: typer, httpx, rich, agenthub-shared · Python ≥ 3.11

## 配置管理

### 配置文件位置
`~/.agenthub/config.toml`

```toml
[registry]
url = "http://localhost:8000"
api_key = ""
```

首次运行任何命令时自动创建 `~/.agenthub/` 目录和默认配置文件。

### 环境变量覆盖
- `SKILLS_REGISTRY_URL` — 覆盖 `registry.url`
- `SKILLS_REGISTRY_API_KEY` — 覆盖 `registry.api_key`

### config 命令
```
agenthub-cli config set registry.url <url>     # 设置 Registry URL
agenthub-cli config set registry.api_key <key>  # 设置 API Key
agenthub-cli config show                        # 显示当前配置（API Key 自动脱敏，仅显示前6位）
```

## 命令结构

```
agenthub-cli
├── publish          # 发布 Skill
├── add <name>       # 安装 Skill
├── find [keyword]   # 搜索（Skills / MCPs / Agents 全局搜索）
├── list             # 列出本地已安装的 Skills
├── remove <name>    # 删除本地 Skill
├── mcp
│   ├── list         # 列出可用 MCP Servers
│   └── add <name>   # 安装 MCP Server 配置
└── agent
    ├── list         # 列出可用 Agent Configs
    └── add <name>   # 安装 Agent Config（完整包）
```

## 命令逻辑

### agenthub-cli publish
```
输入: 当前目录（包含 SKILL.md）
  1. 检查当前目录是否有 SKILL.md → 没有则报错退出
  2. 解析 SKILL.md（使用 agenthub-shared 的 parse_skill_md_file）
  3. 获取 git remote URL（origin）和当前 commit hash → 失败则报错 "Not a git repository or git not installed"
  4. 计算 skill_path（SKILL.md 所在目录相对于 git 仓库根目录的路径，根目录时为空字符串）
  5. 读取 SKILL.md 完整内容作为 readme_content
  6. POST /api/v1/skills { name, description, version, tags, git_url, git_ref: null, commit_hash, skill_path, readme_content }
  7. 输出: "✓ Published {name} (id: {id})"
```

### agenthub-cli add \<name\>
```
参数: name（必填）, --agent kiro, --method copy, --scope workspace
  1. GET /api/v1/skills?keyword=<name> 搜索
  2. 无结果 → 报错退出
  3. 取第一个匹配结果，GET /api/v1/skills/{id}/install 获取安装包
  4. AdapterFactory.get_adapter(agent) 获取适配器（默认 kiro）
  5. adapter.install_skill(files, name, scope, method) 执行安装
  6. POST /api/v1/skills/{id}/install?agent_type=<agent> 记录安装
  7. 输出: "✓ Installed {name} → {path}"
  8. 输出 adapter.get_post_install_hints()
```

### agenthub-cli find \[keyword\]
```
输入: 关键词（可选，默认空字符串）
  1. 如果有 keyword: GET /api/v1/search?q=<keyword>（全局搜索，返回 skills / mcps / agents）
  2. 如果无 keyword: GET /api/v1/skills（仅搜索 skills）
  3. 遍历结果中的每个资产类型（skills / mcps / agents），用 Rich Table 输出:
     列: Name | Description（截断60字符）| Installs
     每类最多显示 20 条
  4. 无结果时输出提示
```

### agenthub-cli list
```
输入: 无
  1. 扫描本地已安装的 skills:
     - .kiro/skills/*/SKILL.md (workspace scope)
     - ~/.kiro/skills/*/SKILL.md (global scope)
  2. 用 Rich Table 输出: Name | Scope | Path
```

### agenthub-cli remove \<name\>
```
输入: skill 名称
  1. 依次在 .kiro/skills/ 和 ~/.kiro/skills/ 中查找匹配目录
  2. 如果是 symlink → unlink
  3. 如果是普通目录 → shutil.rmtree
  4. 清理缓存目录 .skills-registry/cache/{name}（如果存在）
  5. 输出: "✓ Removed {name}"
  6. 未找到 → 输出提示
```

### agenthub-cli mcp list
```
  1. GET /api/v1/mcps 获取所有 MCP Servers
  2. Rich Table 输出: Name | Description（截断60字符）| Transport
```

### agenthub-cli mcp add \<name\>
```
参数: name（必填）, --scope workspace
  1. GET /api/v1/mcps?keyword=<name> 搜索
  2. 无结果 → 报错退出
  3. 取第一个匹配结果，GET /api/v1/mcps/{id}/install 获取配置
  4. AdapterFactory.get_adapter("kiro") 获取适配器
  5. 从 config["config"]["mcpServers"] 提取 MCP 配置
  6. adapter.install_mcp(config, scope) 写入 mcp.json
  7. POST /api/v1/mcps/{id}/install?agent_type=kiro 记录安装
  8. 输出: "✓ Added MCP Server {name} to mcp.json"
  9. 如果有 env_vars_needed → 提示用户需要配置的环境变量列表
```

### agenthub-cli agent list
```
  1. GET /api/v1/agents 获取所有 Agent Configs
  2. Rich Table 输出: Name | Description（截断60字符）| Skills（数量）| MCPs（数量）
```

### agenthub-cli agent add \<name\>
```
参数: name（必填）, --scope workspace, --method copy
  1. GET /api/v1/agents?keyword=<name> 搜索
  2. 无结果 → 报错退出
  3. 取第一个匹配结果，GET /api/v1/agents/{id}/install 获取完整包
  4. 反序列化为 AgentInstallPackage（来自 agenthub-shared）
  5. AdapterFactory.get_adapter("kiro") 获取适配器
  6. adapter.install_agent_config(package, scope, method) 执行安装
  7. POST /api/v1/agents/{id}/install?agent_type=kiro 记录安装
  8. 输出:
     "✓ Installed Agent: {name}"
     "  Skills: {n} installed"
     "  MCP Servers: {n} configured"
     + summary.hints
```

## API 客户端

```python
class RegistryClient:
    """从 ~/.agenthub/config.toml 读取 base_url 和 api_key，支持环境变量覆盖。"""

    def __init__(self):
        self._client = httpx.Client(
            base_url=get_registry_url(),
            headers={"X-API-Key": get_api_key()},
            timeout=30.0,
        )

    def _handle(self, resp) -> dict | list | None:
        """统一响应处理: 204→None, 非成功→RuntimeError, 成功→json"""
        ...

    # Skills
    def search_skills(keyword=None, tag=None)  # GET /api/v1/skills
    def get_skill_install(skill_id)             # GET /api/v1/skills/{id}/install
    def create_skill(data)                      # POST /api/v1/skills
    def record_skill_install(skill_id, agent_type="kiro")  # POST /api/v1/skills/{id}/install

    # MCPs
    def search_mcps(keyword=None)               # GET /api/v1/mcps
    def get_mcp_install(mcp_id)                 # GET /api/v1/mcps/{id}/install
    def record_mcp_install(mcp_id, agent_type="kiro")      # POST /api/v1/mcps/{id}/install

    # Agents
    def search_agents(keyword=None)             # GET /api/v1/agents
    def get_agent_install(agent_id)             # GET /api/v1/agents/{id}/install
    def record_agent_install(agent_id, agent_type="kiro")  # POST /api/v1/agents/{id}/install

    # Search
    def search_all(keyword)                     # GET /api/v1/search?q=<keyword>
```

## 错误处理

所有命令共享统一的 `_handle_error` 逻辑:

| 异常类型 | 输出 |
|---------|------|
| `httpx.ConnectError` | "✗ Cannot connect to registry at {url}" + 提示检查服务器 |
| `httpx.TimeoutException` | "✗ Request timed out..." |
| `RuntimeError("API error ...")` | 直接输出 API 返回的错误详情 |
| 其他异常 | 输出异常消息 |

所有错误均通过 `typer.Exit(1)` 退出，Rich Console 输出到 stderr。
