# Enhancement Unit of Work - 工作单元定义（Iteration 2）

## 拆分策略
基于变更影响范围，按 **可独立开发和测试的功能域** 拆分为 5 个工作单元。
开发顺序：后端 API → 前端基础设施 → 公共页面 → Admin Portal → 个人中心。

---

## Unit E1: 后端 API 扩展
- **影响路径**: `backend/`
- **职责**: 扩展后端 API 支持多用户注册/登录、个人中心、Admin 管理
- **内容**:
  - User model 增加 password_hash 字段
  - Auth 模块增加密码注册/登录
  - 新增 Profile API（我的资产、安装记录、统计）
  - 新增 MCP/Agent top API
  - Admin API 增加跨类型资产管理
  - 确保所有资产 API 返回 author 信息
- **依赖**: 无（在现有后端基础上扩展）
- **预估复杂度**: 中

## Unit E2: 前端基础设施
- **影响路径**: `frontend/`
- **职责**: Tailwind CSS 集成、Auth Context、路由守卫、布局组件
- **内容**:
  - 安装配置 Tailwind CSS + PostCSS
  - 创建 AuthContext（登录状态管理）
  - 创建 ProtectedRoute / AdminRoute 路由守卫
  - 重构 Layout.tsx（Tailwind 样式 + 登录状态导航）
  - 创建 AdminLayout.tsx（Admin 侧边栏布局）
  - 创建通用组件（AssetCard, AssetTypeTabs, MarkdownRenderer）
  - 扩展 api/client.ts（新增 API 调用）
- **依赖**: Unit E1（需要后端 API 就绪）
- **预估复杂度**: 中

## Unit E3: 公共页面重构
- **影响路径**: `frontend/src/pages/`
- **职责**: 重构所有面向用户的页面
- **内容**:
  - Home.tsx — 分类 Tab（Skills/MCP/Agents）+ 增强视觉
  - SearchPage.tsx — 类型筛选 + owner 显示
  - SkillDetail.tsx — GitHub-style Markdown 渲染 + 元信息优化
  - Login.tsx — Tailwind 样式 + 注册链接
  - Register.tsx [NEW] — 注册页
  - 更新 App.tsx 路由配置
- **依赖**: Unit E2（需要基础设施组件就绪）
- **预估复杂度**: 中

## Unit E4: Admin Portal 页面
- **影响路径**: `frontend/src/pages/admin/`
- **职责**: Admin 专属管理页面
- **内容**:
  - AdminDashboard.tsx — Admin 首页概览
  - AdminSyncSources.tsx — 同步源管理（列表、添加、删除、手动同步）
  - AdminAssets.tsx — 资产管理（跨类型列表、删除）
  - AdminUsers.tsx — 用户管理（预留，列表 + 角色修改）
  - 更新 App.tsx 添加 `/admin/*` 路由
- **依赖**: Unit E2（需要 AdminLayout 和 AdminRoute）
- **预估复杂度**: 中

## Unit E5: 个人中心页面
- **影响路径**: `frontend/src/pages/`
- **职责**: 用户个人中心
- **内容**:
  - Profile.tsx — 我发布的资产 + 我安装的资产 + API Key 管理 + 发布统计
  - 更新 Layout 导航添加个人中心入口
- **依赖**: Unit E2（需要 AuthContext 和 ProtectedRoute）
- **预估复杂度**: 低

## 依赖矩阵

```
              E1        E2        E3        E4        E5
              Backend   Infra     Pages     Admin     Profile
E1             -         -         -         -         -
E2             ✓         -         -         -         -
E3             ✓         ✓         -         -         -
E4             ✓         ✓         -         -         -
E5             ✓         ✓         -         -         -
```

## 开发顺序

```
Phase 1:  Unit E1 (Backend API)
              │
Phase 2:  Unit E2 (Frontend Infrastructure)
              │
Phase 3:  Unit E3 (Public Pages)    ←── 可与 E4, E5 并行
          Unit E4 (Admin Portal)    ←── 可与 E3, E5 并行
          Unit E5 (Profile)         ←── 可与 E3, E4 并行
```

### 关键路径
```
E1 → E2 → E3/E4/E5（并行）
```
