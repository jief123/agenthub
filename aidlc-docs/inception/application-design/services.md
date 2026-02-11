# Services - 服务层定义与编排

## API 端点设计（RESTful）

### Skills API
```
GET    /api/v1/skills                  # 搜索/列表（?keyword=&tag=&page=&size=）
GET    /api/v1/skills/top              # Leaderboard（?limit=）
GET    /api/v1/skills/{id}             # 详情
POST   /api/v1/skills                  # 注册新 Skill
PUT    /api/v1/skills/{id}             # 更新
DELETE /api/v1/skills/{id}             # 删除（admin）
GET    /api/v1/skills/{id}/install     # 获取安装包（Git URL + commit + 文件内容）
POST   /api/v1/skills/{id}/install     # 记录安装（统计用）
```

### MCP Server API
```
GET    /api/v1/mcps                    # 搜索/列表
GET    /api/v1/mcps/{id}               # 详情
POST   /api/v1/mcps                    # 注册
PUT    /api/v1/mcps/{id}               # 更新
DELETE /api/v1/mcps/{id}               # 删除（admin）
GET    /api/v1/mcps/{id}/install       # 获取安装配置（mcp.json 片段）
POST   /api/v1/mcps/{id}/install       # 记录安装
```

### Agent Config API
```
GET    /api/v1/agents                  # 搜索/列表
GET    /api/v1/agents/{id}             # 详情
POST   /api/v1/agents                  # 注册
PUT    /api/v1/agents/{id}             # 更新
DELETE /api/v1/agents/{id}             # 删除（admin）
GET    /api/v1/agents/{id}/install     # 获取完整安装包（Skills + MCP + Prompt）
POST   /api/v1/agents/{id}/install     # 记录安装
```

### User API
```
POST   /api/v1/auth/register           # 注册用户
POST   /api/v1/auth/api-key            # 生成/重置 API Key
GET    /api/v1/users/me                # 当前用户信息
GET    /api/v1/users/me/published      # 我发布的资产
GET    /api/v1/users/me/installed      # 我安装的资产
```

### Admin API
```
GET    /api/v1/admin/users             # 用户列表
PUT    /api/v1/admin/users/{id}/role   # 修改角色
PUT    /api/v1/admin/users/{id}/disable # 禁用用户
GET    /api/v1/admin/stats             # 平台统计
POST   /api/v1/admin/import            # 手动导入外部 Skill
GET    /api/v1/admin/sync-sources      # 同步源列表
POST   /api/v1/admin/sync-sources      # 添加同步源
DELETE /api/v1/admin/sync-sources/{id} # 删除同步源
POST   /api/v1/admin/sync-sources/{id}/sync  # 手动触发同步
```

### 搜索 API（统一入口）
```
GET    /api/v1/search?q=&type=&tag=&page=&size=  # 跨资产类型搜索
```

## 核心业务流程

### 流程 1: Skill 注册（CLI → API）
```
CLI: skills publish
  1. CLI 读取当前目录的 SKILL.md
  2. CLI 解析 YAML frontmatter 提取元数据
  3. CLI 获取当前 Git 仓库的 remote URL 和 commit hash
  4. POST /api/v1/skills { name, description, version, tags, git_url, commit_hash, skill_path }
  5. 后端校验数据，存入数据库
  6. 返回注册成功 + Skill ID
```

### 流程 2: Skill 安装（CLI → API → 本地文件操作）
```
CLI: skills add <name>
  1. GET /api/v1/skills?keyword=<name> 搜索
  2. GET /api/v1/skills/{id}/install 获取安装包
  3. 后端返回: { git_url, commit_hash, skill_path, files: {...} }
     - 后端通过 GitService 浅克隆仓库，读取文件内容，返回给 CLI
  4. CLI 通过 AdapterFactory 获取 KiroAdapter
  5. KiroAdapter.install_skill() 将文件写入本地目录
  6. POST /api/v1/skills/{id}/install 记录安装（统计）
  7. 输出安装成功 + 激活提示
```

### 流程 3: Agent 配置安装（整包）
```
CLI: skills agent add <name>
  1. GET /api/v1/agents?keyword=<name> 搜索
  2. GET /api/v1/agents/{id}/install 获取完整包
  3. 后端返回: { prompt, embedded_skills: [...], embedded_mcps: [...] }
  4. CLI 通过 KiroAdapter 依次安装:
     a. 每个 embedded skill → install_skill()
     b. 每个 embedded mcp → install_mcp()
     c. Agent 配置文件 → install_agent_config()
  5. POST /api/v1/agents/{id}/install 记录安装
  6. 输出安装摘要
```

### 流程 4: 外部源导入
```
Admin: Web UI → 导入外部 Skill
  1. POST /api/v1/admin/import { git_url }
  2. ImportService 调用 GitService.clone_shallow()
  3. GitService.discover_skills() 发现仓库中的 SKILL.md
  4. 对每个发现的 Skill:
     a. parse_skill_md() 解析元数据
     b. get_commit_hash() 获取 commit
     c. SkillService.register() 注册到平台
     d. 标记 source = "external"
  5. 返回导入结果列表
```

## 定时任务

### 自动同步
- **触发**: 按配置的间隔定期执行（如每 6 小时）
- **实现**: FastAPI 后台任务 或 APScheduler
- **流程**: 遍历 sync_sources 表，对每个源执行 ImportService 逻辑，检查 commit hash 是否有变化
