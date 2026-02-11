# Unit 2: Backend — Business Logic Model

## SkillService

### register
```
输入: git_url, git_ref, skill_path, author_id
  1. GitService.clone_shallow(git_url, git_ref)
  2. GitService.get_commit_hash(repo_dir)
  3. 定位 SKILL.md: repo_dir / skill_path / SKILL.md
  4. 解析 SKILL.md → SkillMetadata
  5. 渲染 Markdown body → HTML（用 markdown 库）
  6. 检查 name 是否已存在（同名则拒绝，需用 update）
  7. 创建 Skill 记录，source = "internal"
  8. GitService.cleanup(repo_dir)
  9. 返回 SkillResponse
```

### get_install_package
```
输入: skill_id
  1. 从数据库获取 Skill 记录
  2. GitService.clone_shallow(skill.git_url, skill.git_ref)
  3. 读取 skill_path 目录下所有文件（SKILL.md + scripts/ + references/ + assets/）
  4. 构建 files dict: { 相对路径: 文件内容 }
  5. GitService.cleanup(repo_dir)
  6. 返回 SkillInstallPackage
```

### search
```
输入: keyword, tag, page, size
  1. 构建查询:
     - 如果 keyword: WHERE LOWER(name) LIKE '%keyword%' OR LOWER(description) LIKE '%keyword%'
     - 如果 tag: 从 JSON string tags 字段中过滤（应用层 json.loads + 匹配）
     - 两者可组合
  2. ORDER BY installs DESC（默认按安装量排序）
  3. 分页: OFFSET (page-1)*size LIMIT size
  4. 返回 PaginatedResult[SkillResponse]
```

## MCPService

### register
```
输入: MCPServerCreate, author_id
  1. 校验 transport 值合法
  2. 构建完整 config JSONB:
     { "command": ..., "args": [...], "env": {...}, "autoApprove": [...] }
  3. 检查 name 是否已存在
  4. 创建 MCPServer 记录
  5. 返回 MCPServerResponse
```

### get_install_config
```
输入: mcp_id, agent_type
  1. 从数据库获取 MCPServer 记录
  2. 通过 AdapterFactory 获取对应 Adapter
  3. 根据 agent_type 调整环境变量格式（如 Kiro CLI 用 ${env:VAR}）
  4. 构建 mcp.json 片段: { "mcpServers": { name: config } }
  5. 提取需要用户配置的环境变量列表
  6. 返回 MCPInstallConfig
```

## AgentConfigService

### register
```
输入: AgentConfigCreate, author_id
  1. 校验 name 唯一
  2. 存储完整包（prompt + embedded_skills + embedded_mcps）到 JSONB
  3. 创建 AgentConfig 记录
  4. 返回 AgentConfigResponse
```

### get_install_package
```
输入: agent_id
  1. 从数据库获取 AgentConfig 记录
  2. 构建 AgentInstallPackage（直接从 JSONB 字段读取）
  3. 返回 AgentInstallPackage
```

## UserService

### register_with_password
```
输入: username, email, password
  1. 校验 username 唯一性 → 冲突则返回 409
  2. 校验 email 唯一性 → 冲突则返回 409
  3. bcrypt hash password → password_hash
  4. 生成 API Key: "sr_" + secrets.token_urlsafe(32)，bcrypt hash 后存储
  5. 创建 User(role="user", is_active=True, password_hash, api_key_hash)
  6. 创建 JWT token（有效期 24 小时）
  7. 返回 AuthResponse(user, api_key=明文, token=JWT)
```

### login_with_password
```
输入: email, password
  1. 查找 User by email → 不存在则返回 401
  2. 校验 is_active → 禁用则返回 403
  3. bcrypt verify password → 不匹配则返回 401
  4. 创建 JWT token（有效期 24 小时）
  5. 返回 AuthResponse(user, token=JWT)
     注意: 登录不会生成或覆盖 API Key，api_key 字段为 None
```

### regenerate_api_key
```
输入: user_id
  1. 查找 User → 不存在则返回 404
  2. 生成随机 API Key: "sr_" + secrets.token_urlsafe(32)
  3. 计算 bcrypt hash
  4. 更新 user.api_key_hash
  5. 返回 APIKeyResponse(api_key=明文)（仅此一次展示）
```

## ImportService

### import_from_url
```
输入: git_url, admin_id
  1. GitService.clone_shallow(git_url)
  2. GitService.discover_skills(repo_dir) → 发现所有 SKILL.md
  3. 对每个发现的 Skill:
     a. parse_skill_md() → SkillMetadata
     b. get_commit_hash()
     c. 检查 name 是否已存在（已存在则跳过或更新）
     d. 创建 Skill 记录，source = "external"
  4. GitService.cleanup(repo_dir)
  5. 返回导入的 Skill 列表
```

## GitService

### clone_shallow
```
输入: url, ref (可选)
  1. 创建临时目录: tempfile.mkdtemp(prefix="skills-")
  2. 执行: git clone --depth 1 [--branch ref] url tempdir
  3. 超时: 60 秒
  4. 失败处理: 清理临时目录，抛出 GitCloneError
  5. 返回临时目录路径
```

### discover_skills
```
输入: repo_dir
  1. 搜索模式（与 skills.sh 一致）:
     - 根目录 SKILL.md
     - skills/**/SKILL.md
     - .kiro/skills/**/SKILL.md
     - .claude/skills/**/SKILL.md
     - .agents/skills/**/SKILL.md
  2. 对每个找到的 SKILL.md，提取其所在目录的相对路径
  3. 返回 list[SkillInfo]（路径 + 基本信息）
```

## Auth 模块

认证采用双通道机制: JWT（前端 Web）+ API Key（CLI / 管理员环境变量）。
依赖 PyJWT 库，JWT 使用 HS256 算法，有效期 24 小时。

### create_jwt_token
```
输入: user_id
  1. 构建 payload: { sub: str(user_id), exp: now + 24h }
  2. jwt.encode(payload, SECRET_KEY, algorithm="HS256")
  3. 返回 JWT token 字符串
```

### decode_jwt_token
```
输入: token
  1. jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
  2. 提取 payload["sub"] → user_id
  3. 过期或无效 → 返回 None
```

### get_current_user (FastAPI Dependency)
```
输入: X-API-Key header (可选), Authorization header (可选)
  │
  ├─ 路径 1: JWT Bearer Token（前端）
  │   1. 检查 Authorization header 是否以 "Bearer " 开头
  │   2. 提取 token，调用 decode_jwt_token → user_id
  │   3. 查询 User(id=user_id, is_active=True)
  │   4. 找到则返回 User 对象
  │
  ├─ 路径 2: API Key（CLI / 环境变量管理员）
  │   1. 检查 X-API-Key header
  │   2. 优先匹配环境变量 ADMIN_API_KEY（直接字符串比较，始终有效）
  │      → 匹配则查找 ADMIN_USERNAME 对应的 admin 用户并返回
  │   3. 否则遍历所有活跃用户，bcrypt.verify(api_key, user.api_key_hash)
  │      → 匹配则返回 User 对象
  │
  └─ 两条路径都未匹配 → 401 Unauthorized
```

### get_optional_user (FastAPI Dependency)
```
输入: X-API-Key header (可选), Authorization header (可选)
  1. 如果两个 header 都缺失 → 返回 None（匿名访问）
  2. 否则调用 get_current_user
  3. 认证失败不抛异常，返回 None
```

### require_admin
```
输入: current_user (来自 get_current_user)
  1. 如果 user.role != "admin" → 403 Forbidden
  2. 返回 User 对象
```
