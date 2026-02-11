# Unit E2: 前端基础设施 — 业务逻辑模型

## 1. AuthContext 状态管理

```
状态:
  - user: UserPublic | null     # 当前登录用户
  - apiKey: string | null       # API Key（存 localStorage）
  - isLoading: boolean          # 初始化加载中
  - isAuthenticated: boolean    # 是否已登录（computed）
  - isAdmin: boolean            # 是否 Admin（computed）

方法:
  - login(email, password) → 调用 POST /auth/login → 保存 apiKey 到 localStorage → 设置 user
  - register(username, email, password) → 调用 POST /auth/register → 保存 apiKey → 设置 user
  - logout() → 清除 localStorage → 设置 user = null
  - refreshUser() → 调用 GET /users/me → 更新 user

初始化:
  - 组件挂载时检查 localStorage 中是否有 apiKey
  - 如果有 → 调用 GET /users/me 验证有效性
  - 如果无效 → 清除 localStorage
```

## 2. 路由守卫

```
ProtectedRoute:
  - 检查 isAuthenticated
  - 未登录 → 重定向到 /login（保存原始路径用于登录后跳回）

AdminRoute:
  - 检查 isAuthenticated + isAdmin
  - 未登录 → 重定向到 /login
  - 已登录但非 Admin → 重定向到 /（首页）
```

## 3. Layout 导航逻辑

```
公共 Layout:
  - Logo + 首页链接
  - Search 链接
  - 右侧:
    - 未登录 → Login / Register 按钮
    - 已登录 → 用户名 + 下拉菜单（Profile, Admin(仅admin), Logout）

Admin Layout:
  - 左侧边栏:
    - Dashboard（概览）
    - Sync Sources（同步源管理）
    - Assets（资产管理）
    - Users（用户管理）
  - 右侧内容区
  - 顶部: 返回主站链接
```

## 4. API Client 扩展

```
新增方法:
  - registerUser(username, email, password) → POST /auth/register
  - loginUser(email, password) → POST /auth/login
  - getCurrentUser() → GET /users/me
  - getMyPublished() → GET /users/me/published
  - getMyInstalled() → GET /users/me/installed
  - getMyStats() → GET /users/me/stats
  - regenerateApiKey() → POST /users/me/api-key/regenerate
  - getTopMcps(limit) → GET /mcps/top
  - getTopAgents(limit) → GET /agents/top
  - getAdminAssets(type?, page, size) → GET /admin/assets
  - deleteAdminAsset(type, id) → DELETE /admin/assets/{type}/{id}
  - getSyncSources() → GET /admin/sync-sources
  - addSyncSource(data) → POST /admin/sync-sources
  - deleteSyncSource(id) → DELETE /admin/sync-sources/{id}
  - triggerSync(id) → POST /admin/sync-sources/{id}/sync

请求拦截:
  - 所有请求自动附加 X-API-Key header（从 localStorage 读取）
  - 401 响应 → 清除登录状态，重定向到 /login
```

## 5. 通用组件

```
AssetCard:
  - 输入: { name, description, type, tags, installs, author_username, version? }
  - 展示: 名称、描述截断、类型 badge、标签、安装量、owner
  - 点击 → 跳转到详情页

AssetTypeTabs:
  - 输入: { activeTab, onTabChange }
  - Tab: Skills | MCP Servers | Agents
  - 切换时触发回调

MarkdownRenderer:
  - 输入: { content: string }
  - 使用 react-markdown + remark-gfm + rehype-highlight
  - GitHub-style 样式（通过 Tailwind prose 类）
  - 代码块语法高亮
```
