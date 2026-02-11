# Unit 3: Frontend — Business Logic Model

## 页面路由

| 路由 | 页面 | 认证 |
|------|------|------|
| `/` | 首页（Leaderboard + 搜索） | 否 |
| `/search?q=&type=&tag=` | 搜索结果 | 否 |
| `/skills/:id` | Skill 详情 | 否 |
| `/mcps/:id` | MCP Server 详情 | 否 |
| `/agents/:id` | Agent Config 详情 | 否 |
| `/login` | 登录页 | 否 |
| `/register` | 注册页 | 否 |
| `/me` | 个人中心 | 是 |
| `/me/published` | 我发布的 | 是 |
| `/me/installed` | 我安装的 | 是 |
| `/admin` | 管理后台 | admin |
| `/admin/assets` | 资产管理 | admin |
| `/admin/users` | 用户管理 | admin |
| `/admin/import` | 外部源导入 | admin |
| `/admin/sync` | 同步源管理 | admin |
| `/admin/stats` | 平台统计 | admin |

## 核心页面逻辑

### 首页
- 调用 `GET /api/v1/skills/top?limit=10` 获取 Skills Leaderboard
- 调用 `GET /api/v1/mcps?page=1&size=5` 获取热门 MCP
- 调用 `GET /api/v1/agents?page=1&size=5` 获取热门 Agent
- 搜索框提交跳转到 `/search?q=...`

### 搜索结果页
- 调用 `GET /api/v1/search?q=&type=&tag=&page=&size=`
- 支持按类型筛选（Skill / MCP / Agent）
- 支持按标签筛选
- 分页加载

### 资产详情页
- 调用 `GET /api/v1/skills/{id}` 获取详情
- 渲染 readme_html（Markdown 已在后端渲染）
- 显示安装命令: `uvx skills-registry add <name>`
- 显示版本、作者、安装量、标签
- 显示 Git 仓库链接

### 管理后台 — 外部源导入
- 输入 Git URL，调用 `POST /api/v1/admin/import`
- 显示导入结果（发现的 Skills 列表）
- 导入成功后刷新资产列表

## API 客户端层

```typescript
// api/client.ts
const API_BASE = "/api/v1"

// 请求拦截: 自动添加 X-API-Key header（从 localStorage 读取）
// 响应拦截: 401 → 跳转登录页

// Skills
getSkills(params): Promise<PaginatedResult<Skill>>
getSkillById(id): Promise<Skill>
getTopSkills(limit): Promise<Skill[]>
createSkill(data): Promise<Skill>

// MCP Servers
getMCPs(params): Promise<PaginatedResult<MCPServer>>
getMCPById(id): Promise<MCPServer>

// Agent Configs
getAgents(params): Promise<PaginatedResult<AgentConfig>>
getAgentById(id): Promise<AgentConfig>

// Search
search(params): Promise<PaginatedResult<SearchResult>>

// Auth
register(data): Promise<User>
generateAPIKey(): Promise<APIKeyResponse>
getMe(): Promise<User>

// Admin
importSkill(gitUrl): Promise<Skill[]>
getStats(): Promise<Stats>
getSyncSources(): Promise<SyncSource[]>
```

## 状态管理
- 认证状态: API Key 存 localStorage，用户信息存 React Context
- 无需复杂状态管理库，React Context + useState 足够
