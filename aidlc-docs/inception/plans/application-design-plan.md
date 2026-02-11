# Application Design Plan

## 设计计划

- [ ] 确认架构设计问题（本文档）
- [ ] 生成 components.md — 组件定义与职责
- [ ] 生成 component-methods.md — 组件方法签名
- [ ] 生成 services.md — 服务层定义与编排
- [ ] 生成 component-dependency.md — 组件依赖关系与通信模式
- [ ] 验证设计完整性和一致性

---

## 架构设计问题

基于需求文档，以下几个设计决策需要确认：

### Question 1 - 前后端部署模式
前端和后端的部署关系？

A) 前后端分离部署：React 前端独立容器（Nginx），通过 API 调用后端
B) 后端托管前端：FastAPI 直接 serve React 构建产物（单容器，简化部署）
C) 开发时分离，生产时合并：开发用 Vite dev server，生产构建后由 FastAPI serve

[Answer]: B

### Question 2 - API 风格
后端 API 设计风格？

A) 纯 RESTful API（资源导向，标准 CRUD）
B) RESTful + 少量 RPC 风格端点（如 `POST /skills/{name}/publish`）
C) GraphQL（灵活查询，前端自由组合字段）

[Answer]: A

### Question 3 - 数据库迁移工具
数据库 schema 管理方式？

A) Alembic（SQLAlchemy 生态，Python 原生，自动生成迁移脚本）
B) 手写 SQL 迁移脚本（简单直接，无额外依赖）
C) 使用 ORM 自动建表（开发快，但生产环境不推荐）

[Answer]: A

### Question 4 - Git 操作方式
平台从 Git 拉取 Skill 文件的方式？

A) 调用系统 `git` 命令（简单，但需要容器内安装 git）
B) 使用 Python Git 库（如 GitPython / pygit2，纯 Python，无系统依赖）
C) 直接通过 Git HTTP API 下载文件（不 clone 整个仓库，只拉取需要的文件，最轻量）

[Answer]: A — 与 skills.sh 一致，使用 `git clone --depth 1` 浅克隆到临时目录，提取所需文件后清理。skills.sh 使用 simple-git 库（Node.js），我们用 GitPython 或直接调用系统 git 命令。容器内需安装 git。

### Question 5 - 搜索实现
全文搜索的实现方式？

A) PostgreSQL 内置全文搜索（`tsvector` + `tsquery`，够用且无额外组件）
B) Elasticsearch / Meilisearch（独立搜索引擎，功能强但增加部署复杂度）
C) 简单 LIKE / ILIKE 查询（最简单，小规模够用，后续可升级）

[Answer]: C

### Question 6 - Agent Adapter 扩展机制
Adapter 的扩展方式？

A) 策略模式 + 注册表：每个 Adapter 是一个 Python 类，实现统一接口，通过配置注册
B) 插件机制：Adapter 作为独立 Python 包，通过 entry_points 发现
C) 简单工厂：硬编码 Adapter 映射，新增 Adapter 改代码即可（MVP 够用）

[Answer]: C

### Question 7 - CLI 与后端的关系
CLI 工具和后端 API 的关系？

A) CLI 是纯 API 客户端：所有操作都通过调用后端 API 完成
B) CLI 混合模式：搜索/发布走 API，安装操作直接本地执行（从 Git 拉取 + 本地文件操作）
C) CLI 完全独立：CLI 直接连数据库和 Git，不依赖后端 API

[Answer]: A

