# Skills Registry Platform - 增强需求规格文档（Iteration 2）

## 1. 概述

### 1.1 Intent Analysis
- **用户请求**: 三项平台增强 — UI/UX 改进、Admin Portal 独立化、多用户 Owner 机制
- **请求类型**: Enhancement（现有平台增强）
- **范围**: System-wide（前端全面重构 + 后端权限/API 扩展）
- **复杂度**: Moderate-Complex（UI 重构量大，但后端数据模型基础已在）

### 1.2 用户回答摘要
| 问题 | 用户选择 | 解读 |
|------|---------|------|
| Q1 UI 框架 | "不需要太复杂的，简单一点" | → Tailwind CSS（轻量、灵活、无重组件库依赖） |
| Q2 详情页风格 | "GitHub 风格" | → GitHub-style Markdown 渲染（代码高亮、表格等） |
| Q3 首页布局 | "分类展示 + 增强视觉" | → 分类 Tab（Skills/MCP/Agents）+ 增强卡片/列表视觉 |
| Q4 Admin 独立方式 | "同一前端，独立功能，怎么简单怎么来" | → `/admin/*` 路由 + Admin 专属布局 |
| Q5 Admin 功能 | "同步资源、删除资源、未来用户管理" | → 同步管理 + 资产删除 + 预留用户管理入口 |
| Q6 用户注册 | "现阶段开放注册，未来 SSO/OIDC" | → 开放注册 + API Key 管理 |
| Q7 发布权限 | "自由发布，不需要审核" | → 所有资产类型均可自由发布 |
| Q8 Owner 展示 | "只显示用户名" | → 资产卡片/详情显示 owner 用户名 |
| Q9 个人中心 | "我发布的 + 我安装的 + API Key + 发布统计" | → 四项功能 |
| Q10 同步资产 Owner | "能提取原作者就提取，不稳定就留 Admin" | → 优先从 SKILL.md 提取，fallback 到 Admin |

## 2. 功能需求

### FR-ENH-01: UI/UX 全面改进

**FR-ENH-01.1 引入 Tailwind CSS**
- 移除所有 inline styles，迁移到 Tailwind CSS
- 建立一致的设计语言（颜色、间距、字体）
- 响应式布局支持

**FR-ENH-01.2 首页改进**
- 分类 Tab 展示：Skills / MCP Servers / Agents 三个 Tab
- 每个 Tab 下按安装量排序的 Leaderboard
- 增强视觉：标签 badges、安装量图标、owner 用户名
- 搜索栏视觉优化

**FR-ENH-01.3 资产详情页改进**
- GitHub-style Markdown 渲染（使用 react-markdown + remark-gfm + rehype-highlight）
- 代码块语法高亮
- 表格、图片、链接完整支持
- 元信息区域：版本、标签、安装量、owner、安装命令
- 排版优化：合理的行高、字体大小、间距

**FR-ENH-01.4 搜索页改进**
- 搜索结果增强视觉
- 按资产类型筛选
- 显示 owner 信息

### FR-ENH-02: Admin Portal

**FR-ENH-02.1 Admin 路由与布局**
- `/admin/*` 路由，Admin 角色登录后可访问
- Admin 专属布局（侧边栏导航或顶部 Tab）
- 非 Admin 用户访问 `/admin` 重定向到首页

**FR-ENH-02.2 同步资源管理**
- 外部源列表管理（添加、编辑、删除同步源）
- 手动触发同步
- 同步状态和日志查看

**FR-ENH-02.3 资产管理**
- 查看所有资产列表（跨类型）
- 删除任意资产
- 查看资产详情和统计

**FR-ENH-02.4 预留：用户管理**
- 用户列表查看
- 用户角色修改（预留，后续完善）
- 用户禁用/启用

### FR-ENH-03: 多用户与 Owner 机制

**FR-ENH-03.1 开放注册**
- 任何人可注册账号（用户名 + 邮箱 + 密码）
- 注册后返回 API Key（一次性展示，用于 CLI）+ JWT Token（用于前端会话）
- 登录只返回 JWT Token（24h 有效），不影响已有 API Key
- 未来预留 SSO/OIDC 登录入口

**FR-ENH-03.2 用户发布权限**
- 所有注册用户可自由发布 Skills、MCP Server 配置、Agent 配置
- 发布即上架，无需审核
- 用户只能编辑/删除自己发布的资产
- Admin 可管理所有资产

**FR-ENH-03.3 Owner 信息展示**
- 所有资产显示 owner 用户名（已有 author_id 字段）
- 资产卡片/列表中显示 owner
- 详情页显示 owner
- Admin 同步导入的资产：优先从 SKILL.md frontmatter 提取原作者信息，提取失败则 owner 为执行同步的 Admin

**FR-ENH-03.4 个人中心**
- 我发布的资产列表（按类型分组）
- 我安装的资产列表
- API Key 管理（生成、查看、重新生成）
- 发布统计（我的资产总安装次数）

## 3. 非功能需求变更

### NFR 变更点
- 前端引入 Tailwind CSS，构建流程需更新
- Markdown 渲染需引入 react-markdown 等依赖
- Admin 路由需要前端路由守卫
- 无新的后端 NFR 变更（现有架构足够支撑）

## 4. 技术决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| CSS 框架 | Tailwind CSS | 用户要求简单轻量，不引入重组件库 |
| Markdown 渲染 | react-markdown + remark-gfm + rehype-highlight | GitHub-style 渲染，社区成熟 |
| Admin 路由 | 同应用 `/admin/*` | 用户要求简单，不需要独立应用 |
| 前端状态 | React Context（auth state） | 轻量，不需要 Redux 等重方案 |

## 5. 影响分析

### 前端变更（大）
- 所有页面重写样式（inline → Tailwind）
- 新增 Admin 页面和布局
- 新增个人中心页面
- 新增 Auth Context 和路由守卫
- 新增 Markdown 渲染组件

### 后端变更（小-中）
- 新增用户注册 API（密码认证，当前只有 API Key）
- 新增个人中心相关 API（我的资产、我的安装、统计）
- 资产列表 API 增加 owner 信息返回（已有 author relationship）
- Admin 资产管理 API（部分已有）

### 数据模型变更（小）
- User model：增加 password_hash 字段（Web 登录用）
- 认证架构：JWT Token（前端会话）+ API Key（CLI），双轨互不干扰
- 无其他模型变更（author_id 已存在）
