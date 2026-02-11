# Unit E4: Admin Portal — 业务逻辑模型

## 1. Admin Dashboard

```
数据加载:
  - GET /admin/stats（如果已有）或聚合前端已有数据

布局:
  - 概览卡片:
    - 总 Skills 数
    - 总 MCP Servers 数
    - 总 Agent Configs 数
    - 总用户数
    - 总安装次数
  - 快捷操作链接: 同步源管理、资产管理
```

## 2. Admin Sync Sources 同步源管理

```
状态:
  - sources: SyncSource[]
  - showAddForm: boolean
  - syncingId: number | null（正在同步的源 ID）

数据加载:
  - GET /admin/sync-sources

操作:
  - 添加: POST /admin/sync-sources { git_url, sync_interval }
  - 删除: DELETE /admin/sync-sources/{id}（确认对话框）
  - 手动同步: POST /admin/sync-sources/{id}/sync
    - 同步中显示 loading 状态
    - 完成后刷新列表

布局:
  - 顶部: "Add Source" 按钮
  - 添加表单: Git URL + 同步间隔
  - 源列表表格: URL、上次同步时间、状态、操作（同步/删除）
```

## 3. Admin Assets 资产管理

```
状态:
  - assets: Asset[]
  - typeFilter: "all" | "skill" | "mcp" | "agent"
  - page, totalPages

数据加载:
  - GET /admin/assets?type={typeFilter}&page={page}

操作:
  - 删除: DELETE /admin/assets/{type}/{id}（确认对话框）
  - 查看详情: 跳转到对应资产详情页

布局:
  - 顶部: 类型筛选 Tab
  - 资产表格: 名称、类型、Owner、安装量、创建时间、操作（查看/删除）
  - 底部: 分页
```

## 4. Admin Users 用户管理（预留）

```
状态:
  - users: User[]
  - page, totalPages

数据加载:
  - GET /admin/users

操作:
  - 修改角色: PUT /admin/users/{id}/role（预留）
  - 禁用/启用: PUT /admin/users/{id}/disable（预留）

布局:
  - 用户表格: 用户名、邮箱、角色、状态、注册时间、操作
  - 操作列: 角色切换、禁用/启用按钮
```
