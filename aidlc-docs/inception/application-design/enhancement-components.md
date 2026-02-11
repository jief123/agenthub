# Enhancement Components - 增量组件变更（Iteration 2）

## 变更概览

本次增强不改变现有系统架构，而是在现有组件基础上扩展。

```
变更类型图例: [NEW] 新增 | [MOD] 修改 | [---] 不变
```

## 组件变更清单

### C-06: React Frontend [MOD — 大幅重构]

**变更内容**:
1. 引入 Tailwind CSS，移除所有 inline styles
2. 新增 Auth Context（登录状态管理）
3. 新增路由守卫（ProtectedRoute, AdminRoute）
4. 重构所有现有页面样式
5. 新增 Admin 布局组件
6. 新增多个页面

**新增子模块**:
- `contexts/AuthContext.tsx` [NEW] — 登录状态、用户信息、token 管理
- `components/ProtectedRoute.tsx` [NEW] — 需登录才能访问的路由守卫
- `components/AdminRoute.tsx` [NEW] — 需 Admin 角色的路由守卫
- `components/AdminLayout.tsx` [NEW] — Admin Portal 专属布局（侧边栏导航）
- `components/MarkdownRenderer.tsx` [NEW] — GitHub-style Markdown 渲染组件
- `components/AssetCard.tsx` [NEW] — 通用资产卡片组件（Skills/MCP/Agents 复用）
- `components/AssetTypeTabs.tsx` [NEW] — 资产类型 Tab 切换组件

**新增页面**:
- `pages/Register.tsx` [NEW] — 用户注册页
- `pages/Profile.tsx` [NEW] — 个人中心（我的资产 + 安装记录 + API Key + 统计）
- `pages/admin/AdminDashboard.tsx` [NEW] — Admin 首页（概览）
- `pages/admin/AdminSyncSources.tsx` [NEW] — 同步源管理
- `pages/admin/AdminAssets.tsx` [NEW] — 资产管理（查看/删除）
- `pages/admin/AdminUsers.tsx` [NEW] — 用户管理（预留）

**修改页面**:
- `pages/Home.tsx` [MOD] — 分类 Tab + 增强视觉 + Tailwind 样式
- `pages/SearchPage.tsx` [MOD] — 类型筛选 + owner 显示 + Tailwind 样式
- `pages/SkillDetail.tsx` [MOD] — GitHub-style Markdown + 元信息优化 + Tailwind 样式
- `pages/Login.tsx` [MOD] — Tailwind 样式 + 注册链接
- `components/Layout.tsx` [MOD] — Tailwind 样式 + 登录状态显示 + 导航优化
- `api/client.ts` [MOD] — 新增注册/登录/个人中心/Admin API 调用

### C-01: API Layer [MOD — 扩展]

**新增路由**:
- `routes/auth_routes.py` [MOD] — 新增 `POST /register`（密码注册）、`POST /login`（密码登录返回 API Key）
- `routes/profile.py` [NEW] — 个人中心 API
  - `GET /api/v1/users/me/published` — 我发布的资产
  - `GET /api/v1/users/me/installed` — 我安装的资产
  - `GET /api/v1/users/me/stats` — 发布统计
  - `POST /api/v1/users/me/api-key` — 重新生成 API Key
- `routes/admin.py` [MOD] — 新增资产删除（跨类型）、完善同步源管理

### C-02: Service Layer [MOD — 扩展]

**修改**:
- `UserService` [MOD] — 新增密码注册/登录方法
  - `async def register_with_password(username, email, password) -> User`
  - `async def login_with_password(email, password) -> tuple[User, str]` — 返回 User + API Key
- `SkillService` [MOD] — 搜索结果包含 author 信息（已有 relationship，确保序列化）
- `MCPService` [MOD] — 同上
- `AgentConfigService` [MOD] — 同上

**新增**:
- `ProfileService` [NEW] — 个人中心业务逻辑
  - `async def get_published_assets(user_id) -> dict` — 按类型分组的已发布资产
  - `async def get_installed_assets(user_id) -> list` — 安装记录
  - `async def get_publish_stats(user_id) -> dict` — 发布统计（总安装次数等）

### C-03: Data Layer [MOD — 小改]

**修改**:
- `models/user.py` [MOD] — 新增 `password_hash` 字段
- 其他模型不变（author_id 已存在）

### C-08: Auth Module [MOD — 扩展]

**修改**:
- `auth.py` [MOD] — 新增密码验证方法，保留 API Key 认证
  - `def hash_password(password: str) -> str`
  - `def verify_password(password: str, hashed: str) -> bool`

### C-04, C-05, C-07: [---] 不变
- Agent Adapter Layer — 不变
- Git Integration — 不变（同步导入时提取原作者逻辑已在 SKILL.md 解析中）
- CLI Tool — 不变（本次迭代聚焦 Web 端）

## 新增前端依赖

| 包名 | 用途 |
|------|------|
| tailwindcss + postcss + autoprefixer | CSS 框架 |
| react-markdown | Markdown 渲染 |
| remark-gfm | GitHub Flavored Markdown 支持 |
| rehype-highlight | 代码语法高亮 |
| highlight.js | 语法高亮主题 |
