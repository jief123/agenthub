# Unit E5: 个人中心 — 业务逻辑模型

## 1. Profile 页面

```
状态:
  - activeTab: "published" | "installed" | "apikey" | "stats"
  - publishedAssets: { skills: [], mcps: [], agents: [] }
  - installedAssets: InstallLog[]
  - stats: PublishStats
  - apiKeyVisible: boolean
  - newApiKey: string | null（重新生成后显示）

数据加载（按 Tab 懒加载）:
  - published → GET /users/me/published
  - installed → GET /users/me/installed
  - stats → GET /users/me/stats
  - apikey → 不需要额外加载（API Key 在 AuthContext 中）
```

## 2. 我发布的资产 Tab

```
布局:
  - 按类型分组显示:
    - Skills 区块: 资产列表（名称、版本、安装量、创建时间）
    - MCP Servers 区块: 资产列表
    - Agent Configs 区块: 资产列表
  - 每个资产可点击跳转到详情页
  - 空状态: "You haven't published any assets yet."
```

## 3. 我安装的资产 Tab

```
布局:
  - 安装记录列表（按时间倒序）:
    - 资产名称 + 类型 badge
    - 安装时间
    - Agent 类型（kiro 等）
  - 空状态: "No installation records."
```

## 4. API Key 管理 Tab

```
布局:
  - 当前 API Key（遮罩显示，点击可复制）
  - "Regenerate API Key" 按钮
    - 确认对话框: "This will invalidate your current key. Continue?"
    - 确认后 → POST /users/me/api-key/regenerate
    - 显示新 Key（提示保存）
    - 更新 AuthContext 和 localStorage
```

## 5. 发布统计 Tab

```
布局:
  - 统计卡片:
    - 发布的 Skills 数量
    - 发布的 MCP Servers 数量
    - 发布的 Agent Configs 数量
    - 总安装次数（所有资产的安装量之和）
```
