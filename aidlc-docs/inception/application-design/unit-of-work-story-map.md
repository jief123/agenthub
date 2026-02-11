# Unit of Work Story Map - 功能需求到工作单元映射

由于跳过了 User Stories 阶段，此文档直接映射功能需求（FR）到工作单元。

## 映射矩阵

| 功能需求 | Unit 1 | Unit 2 | Unit 3 | Unit 4 | Unit 5 |
|---------|--------|--------|--------|--------|--------|
| FR-01.1 Skills 注册 | ✓(schema+parser) | ✓(API+Service+DB) | ✓(发布表单) | ✓(publish 命令) | |
| FR-01.2 MCP 注册 | ✓(schema) | ✓(API+Service+DB) | ✓(发布表单) | ✓(mcp publish) | |
| FR-01.3 Agent 注册 | ✓(schema) | ✓(API+Service+DB) | ✓(发布表单) | ✓(agent publish) | |
| FR-02.1 Web 搜索浏览 | | ✓(搜索 API) | ✓(列表+搜索+详情页) | | |
| FR-02.2 CLI 搜索 | | ✓(搜索 API) | | ✓(find/list 命令) | |
| FR-03.0 Adapter 层 | ✓(核心实现) | ✓(生成安装指令) | | ✓(本地安装执行) | |
| FR-03 Skills 安装 | ✓(adapter) | ✓(install API+Git) | ✓(安装命令展示) | ✓(add 命令) | |
| FR-03 MCP 安装 | ✓(adapter) | ✓(install API) | ✓(安装命令展示) | ✓(mcp add) | |
| FR-03 Agent 安装 | ✓(adapter) | ✓(install API) | ✓(安装命令展示) | ✓(agent add) | |
| FR-04 外部源导入 | | ✓(Import+Sync Service) | ✓(管理后台 UI) | | |
| FR-05 CLI 工具 | | | | ✓(全部命令) | |
| FR-06 管理功能 | | ✓(Admin API) | ✓(管理后台 UI) | | |
| NFR-01 认证 | | ✓(Auth 模块) | ✓(登录页) | ✓(config 命令) | |
| NFR-02 部署 | | | | | ✓(Docker) |

## 每个 Unit 的功能需求覆盖

### Unit 1: Shared
- FR-01.1/1.2/1.3: Pydantic schemas 定义
- FR-03.0: Agent Adapter 核心实现（BaseAdapter + KiroAdapter + Factory）
- FR-01.1: SKILL.md 解析器

### Unit 2: Backend
- FR-01 全部: 三类资产的 CRUD API + Service + Repository + ORM
- FR-02: 搜索 API（ILIKE 查询）
- FR-03: 安装包 API + Git 浅克隆 + 文件读取
- FR-04: 外部源导入 + 自动同步
- FR-06: 管理 API
- NFR-01: API Key 认证 + RBAC

### Unit 3: Frontend
- FR-02.1: 首页 Leaderboard、列表页、搜索、详情页
- FR-01: 资产发布表单（Web 端发布）
- FR-03: 安装命令展示
- FR-06: 管理后台 UI
- NFR-01: 登录/注册页

### Unit 4: CLI
- FR-01.1: `skills publish`
- FR-02.2: `skills find/list`
- FR-03: `skills add/remove/update` + `skills mcp add` + `skills agent add`
- FR-05: 全部 CLI 命令
- NFR-01: `skills config`（API Key 配置）

### Unit 5: Docker
- NFR-02: Dockerfile + docker-compose.yml + 环境配置
