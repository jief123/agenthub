# Unit 1: Shared — Business Logic Model

## SKILL.md 解析器

### 解析流程
```
输入: SKILL.md 文件路径
  1. 读取文件内容
  2. 检测 YAML frontmatter（以 --- 开头和结尾）
  3. 解析 YAML frontmatter → 提取 name, description, version, metadata 等
  4. 提取 frontmatter 之后的 Markdown body
  5. 校验必填字段（name, description）
  6. 返回 SkillMetadata 对象
输出: SkillMetadata
```

### 解析规则
- frontmatter 必须以 `---` 开头，以 `---` 结尾
- `name` 必填，只允许小写字母、数字、连字符，最长 64 字符
- `description` 必填，最长 1024 字符
- `metadata` 是可选的 key-value 字典
- 如果 frontmatter 不存在或格式错误，抛出 `SkillParseError`

## Agent Adapter 层

### AdapterFactory 逻辑
```
输入: agent_type (str)
  1. 查找内置 Adapter 映射表: {"kiro": KiroAdapter, ...}
  2. 如果找到，返回对应 Adapter 实例
  3. 如果未找到，抛出 UnsupportedAgentError
输出: BaseAdapter 实例
```

### detect_installed_agents 逻辑
```
输入: 无
  1. 遍历所有已知 agent 类型
  2. 对每个 agent，检查其配置目录是否存在:
     - Kiro: 检查 .kiro/ 目录
     - Claude Code: 检查 .claude/ 目录
     - Cursor: 检查 .cursor/ 目录
     - ...
  3. 返回检测到的 agent 类型列表
输出: list[str]
```

### KiroAdapter 安装逻辑

#### install_skill
```
输入: skill_files (dict[str, str]), name (str), scope (Scope), method (InstallMethod)
  1. 确定目标目录:
     - workspace: .kiro/skills/{name}/
     - global: ~/.kiro/skills/{name}/
  2. 如果 method == SYMLINK:
     a. 确保 cache 目录存在: .skills-registry/cache/{name}/
     b. 写入文件到 cache 目录
     c. 创建符号链接: 目标目录 → cache 目录
  3. 如果 method == COPY:
     a. 直接写入文件到目标目录
  4. 返回安装路径
输出: Path
```

#### install_mcp
```
输入: config (dict), scope (Scope)
  1. 确定 mcp.json 路径:
     - workspace: .kiro/settings/mcp.json
     - global: ~/.kiro/settings/mcp.json
  2. 读取现有 mcp.json（如不存在则创建空结构）
  3. 合并新配置到 mcpServers 对象
  4. 写回 mcp.json
输出: None
```

#### install_agent_config
```
输入: package (AgentInstallPackage), scope (Scope), method (InstallMethod)
  1. 对 package.embedded_skills 中的每个 skill:
     调用 install_skill(skill.files, skill.name, scope, method)
  2. 对 package.embedded_mcps 中的每个 mcp:
     调用 install_mcp(mcp.config, scope)
  3. 生成 agent 配置文件:
     - 路径: .kiro/agents/{name}.json (workspace) 或 ~/.kiro/agents/{name}.json (global)
     - 内容: { "name": ..., "prompt": ..., "resources": [...] }
  4. 返回安装摘要
输出: InstallSummary
```

#### get_post_install_hints
```
输出提示信息:
  - Kiro IDE: "Skills 已安装，IDE 会自动发现。"
  - Kiro CLI: "请在 agent 配置的 resources 中添加: skill://.kiro/skills/**/SKILL.md"
```
