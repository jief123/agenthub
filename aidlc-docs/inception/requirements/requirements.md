# Skills Registry Platform - 需求规格文档

## 1. 项目概述

### 1.1 Intent Analysis
- **用户请求**: 构建一个可私有化部署的 AI Agent 资产注册与分发平台
- **请求类型**: New Project（全新项目）
- **范围**: System-wide（完整平台：Web UI + API Server + CLI + 数据库）
- **复杂度**: Complex（多组件、多集成点、需要兼容外部生态）

### 1.2 产品定位
企业私有化部署的 AI Agent 资产（Skills / MCP Server 配置 / Agent 配置）注册、搜索与分发平台。开发者将 Skills 代码托管在内部 Git，通过 CLI 注册元数据到平台，其他开发者通过 Web UI 浏览搜索、通过 CLI 一键安装到本地 Agent 环境。

三类资产的关系：
- **Skills**：独立资产，可单独注册和安装
- **MCP Server 配置**：独立资产，可单独注册和安装
- **Agent 配置**：组合资产，引用已注册的 Skills + MCP Server + 自定义 Prompt，不能单独构建，依赖前两者存在

### 1.3 核心价值
- 让组织内的 AI 最佳实践可发现、可复用、可分享
- 兼容 Agent Skills 开放标准和 skills.sh 生态
- 纯内网运行，满足企业安全合规要求
- 支持从公网导入优质 Skills 到内部

## 2. 功能需求

### FR-01: 资产注册与管理
平台管理三类 AI Agent 资产：

**FR-01.1 Skills 注册**
- 开发者通过 CLI 将 Skill 注册到平台
- 平台从 SKILL.md 的 YAML frontmatter 自动提取元数据（name, description, version, tags 等）
- 平台存储 Git URL + commit hash 作为版本引用
- 版本号从 SKILL.md 提取作为展示标签，实际一致性靠 Git
- 支持更新：重新发布时更新元数据和 commit hash
- 发布即上架，无需审核流程

**FR-01.2 MCP Server 配置注册**
- 注册 MCP Server 的连接配置（transport, command, args, env）
- 存储描述信息、标签、兼容性信息
- 用户安装时生成本地 mcp.json 配置片段

**FR-01.3 Agent 配置注册**
- Agent 配置是完整打包件：发布者将 Skills + MCP Server 配置 + Prompt 组装为一个整体发布
- 平台存储完整的 Agent 包内容（内嵌的 Skills 列表、MCP 配置快照、Prompt），不做 N:M 引用拆分
- 用户安装时获取完整包，一次性安装所有内容；本地修改是用户自己的事
- 支持 Git URL 引用（Agent 配置文件托管在 Git）或直接在平台上编辑
- 发布即上架，无需审核流程

### FR-02: 搜索与浏览
**FR-02.1 Web UI**
- 首页 Leaderboard：按安装量排序的资产列表
- 分类浏览：按标签、作者、资产类型（Skill / MCP Server / Agent）筛选
- 全文搜索：搜索名称、描述、标签
- 详情页：渲染 SKILL.md 内容、显示安装命令、版本信息、安装统计
- 个人中心：我发布的 / 我安装的资产

**FR-02.2 CLI 搜索**
- `skills find <keyword>` 关键词搜索
- `skills find --tag <tag>` 按标签搜索
- `skills list` 列出已安装的资产

### FR-03: 安装与分发

**FR-03.0 Agent Adapter 层（横切设计）**
- 三类资产（Skills / MCP Server 配置 / Agent 配置）的安装都涉及写入不同 IDE/Agent 的配置目录
- 设计统一的 Agent Adapter 接口，每个 Adapter 负责：
  - Skill 文件的安装路径（如 `.kiro/skills/`、`.claude/skills/`、`.cursor/skills/`）
  - MCP 配置的合并方式（如 `.kiro/settings/mcp.json`、`.claude/mcp.json`）
  - Agent 配置文件的生成与放置（如 `.kiro/agents/`、`.claude/agents/` 等）
- MVP 只实现 Kiro Adapter（Kiro IDE + Kiro CLI），但架构上所有安装操作都通过 Adapter 层
- 后续扩展只需新增 Adapter（Claude Code, Cursor, Windsurf 等），不改核心逻辑

**安装方式（参考 skills.sh）：**
- **Symlink（推荐）**：CLI 将 skill 文件下载到一个 canonical 目录（如 `.skills-registry/cache/<skill-name>/`），然后在各 agent 的 skills 目录下创建符号链接。优点：单一源头，更新时只需更新 cache 目录
- **Copy**：直接复制到各 agent 的 skills 目录。适用于不支持 symlink 的环境（如某些 Windows 配置）

**多 Agent 安装流程（参考 skills.sh）：**
1. CLI 自动检测本地已安装的 agents（通过检查各 agent 的配置目录是否存在）
2. 提示用户选择要安装到哪些 agents（或通过 `--agent <name>` 指定）
3. 将 skill 文件 symlink/copy 到选中的每个 agent 的 skills 目录

**重要设计原则：CLI 只负责"安装"（文件放置），不负责"激活"（修改 agent 配置）。**
- 激活是各 agent 产品自己的机制：
  - Kiro IDE：安装即激活（自动扫描 `.kiro/skills/`）
  - Kiro CLI：用户需在 agent JSON 的 `resources` 中引用 `skill://`（推荐使用通配 `skill://.kiro/skills/**/SKILL.md`）
  - Claude Code：安装即激活（自动扫描 `.claude/skills/`）
  - 其他 agents：各有各的机制
- CLI 安装完成后，输出提示信息告知用户是否需要额外激活步骤

**Kiro Adapter（MVP）— IDE 与 CLI 的差异处理：**

Kiro IDE 和 Kiro CLI 虽然共享 `.kiro/` 目录结构，但在 Skills 加载机制和 MCP 配置格式上存在差异，Adapter 需要分别处理：

| 资产类型 | 路径（workspace / global） | Kiro IDE 行为 | Kiro CLI 行为 |
|---------|--------------------------|--------------|--------------|
| Skills | `.kiro/skills/<name>/` / `~/.kiro/skills/<name>/` | 自动发现，放入目录即生效（progressive disclosure：启动时只加载 name+description） | 需要在 agent 配置的 `resources` 字段中显式引用：`"resources": ["skill://.kiro/skills/**/SKILL.md"]` |
| MCP Config | `.kiro/settings/mcp.json` / `~/.kiro/settings/mcp.json` | 环境变量格式：`${VAR_NAME}` | 环境变量格式：`${env:VAR_NAME}` |
| Agent Config | `.kiro/agents/<name>.json` / `~/.kiro/agents/<name>.json` | IDE 自动发现可用 agents | CLI 通过 `--agent <name>` 指定使用 |

**Kiro Adapter 安装时需要执行的操作：**

Skills 安装（安装 ≠ 激活，平台只负责安装）：

**安装（Install）**= 将 Skill 文件放置到目标 agent 的 skills 目录：
1. 下载 Skill 文件到本地 cache 目录（`.skills-registry/cache/<skill-name>/`）
2. 按用户选择的 agents，symlink/copy 到各 agent 的 skills 目录
3. 支持 workspace 级（`.kiro/skills/`）和 global 级（`~/.kiro/skills/`）

**激活（Activate）**= 各 agent 产品自己的机制，CLI 不干预，只在安装完成后输出提示：
- Kiro IDE：无需额外操作，自动发现
- Kiro CLI：提示用户在 agent 配置的 `resources` 中添加 `"skill://.kiro/skills/**/SKILL.md"`（如尚未配置）
- 其他 agents：按各自文档提示

MCP Server 安装：
1. 读取现有 `.kiro/settings/mcp.json`
2. 合并新的 MCP Server 配置到 `mcpServers` 对象中
3. 处理环境变量格式差异：生成配置时提供两种格式的说明，或使用 IDE 格式（`${VAR}`）并提示 CLI 用户注意

Agent 配置安装（整包安装）：
1. 从 Registry 获取完整 Agent 包（Prompt + 内嵌 Skills + 内嵌 MCP 配置）
2. 一次性安装所有内容：Skills 文件放入 skills 目录，MCP 配置合并到 mcp.json，Agent 配置文件放入 agents 目录
3. 输出安装摘要：列出本次安装的所有内容
4. 用户后续可在本地自行修改已安装的配置

### FR-04: 外部源导入
**FR-04.1 管理员手动导入**
- 在 Web UI 输入外部 Skill 的 Git URL（skills.sh / GitHub 公开仓库）
- 平台拉取并解析 SKILL.md，注册到内部 Registry
- 标记为"外部导入"来源

**FR-04.2 自动同步（可选）**
- 管理员配置外部源列表（Git 仓库 URL）
- 平台定期检查更新，自动同步新版本
- 支持 skills.sh 上的 Skill 和任意 GitHub 公开仓库

### FR-05: CLI 工具
基于 Python 生态，通过 `uvx` 运行：

```bash
# 运行 CLI（无需预装，uvx 自动处理）
uvx agenthub-cli <command>

# 核心命令
agenthub-cli publish                  # 发布到 Registry
agenthub-cli add <name>               # 从 Registry 安装
agenthub-cli find [keyword]           # 搜索
agenthub-cli list                     # 列出已安装
agenthub-cli remove <name>            # 卸载

# MCP 相关
agenthub-cli mcp list                 # 列出可用 MCP Server
agenthub-cli mcp add <name>           # 安装 MCP 配置

# Agent 相关
agenthub-cli agent list               # 列出可用 Agent 配置
agenthub-cli agent add <name>         # 安装 Agent 配置（自动安装关联的 Skills 和 MCP）

# 配置
agenthub-cli config set registry.url <url>
agenthub-cli config set registry.api_key <key>
agenthub-cli config show
```

### FR-06: 管理功能
- 管理员可管理所有资产（编辑、下架、删除）
- 查看平台统计数据（总资产数、安装量趋势）
- 管理外部源同步配置
- 用户管理（查看、禁用）

## 3. 非功能需求

### NFR-01: 认证与安全
- **MVP 阶段**: 双轨认证
  - **API Key**（CLI / 外部 API 调用）：注册时生成，bcrypt hash 存储，通过 `X-API-Key` header 传递，可在个人中心重新生成
  - **JWT Token**（前端 Web 会话）：登录时签发，24h 有效，通过 `Authorization: Bearer <token>` header 传递，不影响 API Key
  - **Admin Env Key**：通过 `ADMIN_API_KEY` 环境变量配置，永久有效，不受前端登录影响
- **后续阶段**: 对接 OIDC（兼容 AWS IAM Identity Center 和企业 SSO/IDP）
  - 推荐使用 Authlib 库实现标准 OIDC 对接
  - CLI 通过 OAuth2 Device Flow 或 API Key 认证
- RBAC 权限：user（浏览/安装/发布自己的）、admin（全部权限）
- 所有操作留审计日志

### NFR-02: 部署
- Docker 容器化，支持 `docker compose up` 一键启动（生产模式）
- 开发/测试模式支持 SQLite 零依赖本地运行
- 目标环境为 Kubernetes，但 MVP 阶段 Docker Compose 即可
- 纯内网运行，不依赖外部服务（外部源导入除外）
- 单组织单实例，不需要多租户

### NFR-03: 性能
- 搜索响应 < 500ms
- Skill 安装（元数据获取）< 1s
- 支持 1000+ 注册资产
- 支持 100+ 并发用户

### NFR-04: 兼容性
- 兼容 Agent Skills 开放标准（SKILL.md 格式）
- Git 适配：GitHub（公开）+ GitLab（内部）
- Agent 适配：统一 Agent Adapter 架构，MVP 实现 Kiro Adapter，后续通过新增 Adapter 扩展（Claude Code, Cursor, Windsurf 等），三类资产安装均走 Adapter 层

### NFR-05: 可维护性
- 开源项目，MIT 或 Apache 2.0 许可
- 清晰的项目结构和文档
- API 文档自动生成（OpenAPI/Swagger）

## 4. 技术决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 后端 | Python + FastAPI | CLI 也是 Python，统一生态 |
| 前端 | React + Vite | 现代轻量，社区成熟 |
| 数据库 | SQLite（开发/测试）+ PostgreSQL（生产） | SQLite 零依赖快速启动，生产切 PG 只改 DATABASE_URL |
| CLI | Python + Click/Typer | uvx 分发，无需预装 |
| 容器 | Docker + Docker Compose | 简单部署 |
| 认证（MVP） | JWT + API Key 双轨 | JWT 给前端会话，API Key 给 CLI，互不干扰 |
| 认证（后续） | OIDC via Authlib | 标准协议，兼容 AWS IDC / 企业 SSO |
| 源码存储 | 外部 Git（不自建） | 平台只存元数据引用 |
| 版本管理 | Git URL + commit hash | 与 skills.sh 一致 |

## 5. 范围边界

### In Scope（MVP）
- Skills / MCP Server 配置 / Agent 配置的注册、搜索、安装
- Agent 配置的整包安装（一次性安装内嵌的 Skills + MCP + Prompt）
- Web UI（列表、搜索、详情、个人中心、管理后台）
- CLI 工具（Python/uvx）
- API Key 认证
- 外部源手动导入
- Docker Compose 部署
- Kiro IDE / Kiro CLI 支持

### Phase 2 规划
- SSO/OIDC 对接
- 自动安全扫描
- Webhook / IM 通知
- 评分与评论系统
- 其他 Agent 产品支持（Claude Code, Cursor, Windsurf 等，架构已预留）

### Out of Scope
- 客户侧 K8S 部署方案（不在本项目范围）
- Skill 运行时托管（平台只分发配置，不运行）

## 6. 数据模型概要

### 核心实体
- **Skill**: name, description, version, git_url, git_ref, commit_hash, skill_path, tags(JSON), agents[], author_id, installs, readme_html
- **MCPServer**: name, description, version, transport, config(JSON), tags(JSON), author_id, installs
- **AgentConfig**: name, description, prompt, embedded_skills(JSON), embedded_mcps(JSON), tags(JSON), git_url(optional), git_ref(optional), commit_hash(optional), author_id, installs
- **User**: username, display_name, email, role, password_hash, api_key_hash
- **InstallLog**: asset_type, asset_id, user_id, agent_type, installed_at

### 关系
- User 1:N Skill / MCPServer / AgentConfig（发布者）
- AgentConfig 内嵌 Skills 和 MCP 配置快照（非引用关系，安装时整包分发）
- InstallLog 记录所有安装行为（统计用）
