# Enhancement Services - 增量 API 变更（Iteration 2）

## 新增/修改 API 端点

### Auth API [MOD]
```
POST   /api/v1/auth/register           # [NEW] 密码注册（username + email + password）
POST   /api/v1/auth/login              # [NEW] 密码登录（email + password → API Key）
POST   /api/v1/auth/api-key            # [---] 已有，重新生成 API Key
GET    /api/v1/users/me                # [---] 已有
```

### Profile API [NEW]
```
GET    /api/v1/users/me/published      # 我发布的资产（按类型分组）
GET    /api/v1/users/me/installed      # 我安装的资产
GET    /api/v1/users/me/stats          # 发布统计（我的资产总安装次数）
POST   /api/v1/users/me/api-key/regenerate  # 重新生成 API Key
```

### Admin API [MOD]
```
GET    /api/v1/admin/assets            # [NEW] 所有资产列表（跨类型，分页）
DELETE /api/v1/admin/assets/{type}/{id} # [NEW] 删除任意资产（type: skill/mcp/agent）
GET    /api/v1/admin/sync-sources      # [---] 已有
POST   /api/v1/admin/sync-sources      # [---] 已有
DELETE /api/v1/admin/sync-sources/{id} # [---] 已有
POST   /api/v1/admin/sync-sources/{id}/sync  # [---] 已有
GET    /api/v1/admin/users             # [---] 已有
```

### 现有资产 API [MOD — 响应格式增强]
所有资产列表/详情 API 的响应中确保包含 `author` 对象：
```json
{
  "id": 1,
  "name": "example-skill",
  "description": "...",
  "author": {
    "id": 1,
    "username": "admin",
    "display_name": "Admin"
  },
  ...
}
```

### 资产 Top/Leaderboard API [MOD]
```
GET    /api/v1/skills/top?limit=       # [---] 已有
GET    /api/v1/mcps/top?limit=         # [NEW] MCP Server 排行
GET    /api/v1/agents/top?limit=       # [NEW] Agent 配置排行
```

## 新增业务流程

### 流程: 用户密码注册
```
Web UI: 注册页
  1. 用户填写 username + email + password
  2. POST /api/v1/auth/register
  3. 后端校验唯一性，hash 密码，创建 User（role=user）
  4. 自动生成 API Key
  5. 返回 User 信息 + API Key（明文，仅此一次）
  6. 前端保存 API Key 到 localStorage
```

### 流程: 用户密码登录
```
Web UI: 登录页
  1. 用户填写 email + password
  2. POST /api/v1/auth/login
  3. 后端验证密码
  4. 返回 User 信息 + API Key
  5. 前端保存 API Key 到 localStorage
  6. AuthContext 更新登录状态
```

### 流程: 普通用户发布资产
```
与 Admin 发布流程相同，区别仅在于 author_id 为当前登录用户
权限校验：已登录即可发布（无需 Admin）
编辑/删除：只能操作自己的资产（author_id == current_user.id）
```

## 权限矩阵更新

| 操作 | 未登录 | User | Admin |
|------|--------|------|-------|
| 浏览/搜索资产 | ✓ | ✓ | ✓ |
| 查看资产详情 | ✓ | ✓ | ✓ |
| 注册/登录 | ✓ | - | - |
| 发布资产（所有类型） | ✗ | ✓ | ✓ |
| 编辑/删除自己的资产 | ✗ | ✓ | ✓ |
| 删除他人资产 | ✗ | ✗ | ✓ |
| 个人中心 | ✗ | ✓ | ✓ |
| API Key 管理 | ✗ | ✓ | ✓ |
| Admin Portal | ✗ | ✗ | ✓ |
| 同步源管理 | ✗ | ✗ | ✓ |
| 用户管理 | ✗ | ✗ | ✓ |
