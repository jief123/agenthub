# Unit E3: 公共页面重构 — 业务逻辑模型

## 1. Home 首页

```
状态:
  - activeTab: "skills" | "mcps" | "agents"（默认 "skills"）
  - items: 当前 Tab 的排行数据
  - query: 搜索关键词

数据加载:
  - Tab 切换时调用对应 API:
    - skills → getTopSkills(20)
    - mcps → getTopMcps(20)
    - agents → getTopAgents(20)

布局:
  - 顶部: 标题 + 搜索栏
  - 中部: AssetTypeTabs
  - 下部: 资产列表（使用 AssetCard 或增强表格）
    - 每行显示: 名称、描述、标签 badges、安装量、owner 用户名、版本
```

## 2. SearchPage 搜索页

```
状态:
  - query: URL 参数 q
  - type: 筛选类型（all / skill / mcp / agent）
  - results: 搜索结果
  - page: 当前页

数据加载:
  - GET /search?q={query}&type={type}&page={page}

布局:
  - 顶部: 搜索栏（预填 query）
  - 筛选栏: 类型筛选按钮（All / Skills / MCP Servers / Agents）
  - 结果列表: AssetCard 列表
    - 每个结果显示 owner 用户名
  - 底部: 分页
```

## 3. SkillDetail 资产详情页

```
数据加载:
  - GET /skills/{id}（或 /mcps/{id} 或 /agents/{id}，根据路由）

布局:
  - 顶部元信息区:
    - 资产名称（大标题）
    - 描述
    - 元信息行: by {owner} · v{version} · {installs} installs
    - 标签 badges
    - 安装命令框（可复制）: uvx skills-registry add {name}
  - 主体: MarkdownRenderer 渲染 readme_content
    - GitHub-style 排版
    - 代码高亮
    - 表格、图片支持
```

## 4. Login 登录页

```
状态:
  - email, password
  - error: 错误信息
  - isLoading: 提交中

流程:
  - 提交 → AuthContext.login(email, password)
  - 成功 → 跳转到之前的页面（或首页）
  - 失败 → 显示错误信息

布局:
  - 居中卡片
  - Email + Password 输入框
  - Login 按钮
  - 底部: "Don't have an account? Register" 链接
```

## 5. Register 注册页 [NEW]

```
状态:
  - username, email, password, confirmPassword
  - error: 错误信息
  - isLoading: 提交中

校验:
  - password === confirmPassword
  - username 3-64 字符
  - password >= 8 字符

流程:
  - 提交 → AuthContext.register(username, email, password)
  - 成功 → 显示 API Key（提示用户保存）→ 跳转首页
  - 失败 → 显示错误信息

布局:
  - 居中卡片
  - Username + Email + Password + Confirm Password 输入框
  - Register 按钮
  - 底部: "Already have an account? Login" 链接
```

## 6. 路由配置更新

```
/                    → Home
/search              → SearchPage
/skills/:id          → SkillDetail
/mcps/:id            → MCPDetail（复用 SkillDetail 组件或新建）
/agents/:id          → AgentDetail（复用或新建）
/login               → Login
/register            → Register [NEW]
/profile             → Profile [NEW, ProtectedRoute]
/admin/*             → Admin pages [NEW, AdminRoute]
```
