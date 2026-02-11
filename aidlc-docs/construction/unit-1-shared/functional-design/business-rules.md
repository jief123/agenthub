# Unit 1: Shared — Business Rules

## SKILL.md 解析规则

| 规则 | 描述 |
|------|------|
| BR-S01 | name 必填，只允许 `[a-z0-9-]`，最长 64 字符 |
| BR-S02 | description 必填，最长 1024 字符 |
| BR-S03 | frontmatter 必须是合法 YAML，以 `---` 包裹 |
| BR-S04 | metadata 字段可选，必须是 key-value 字典 |
| BR-S05 | 解析失败时抛出 SkillParseError，包含行号和原因 |

## Adapter 规则

| 规则 | 描述 |
|------|------|
| BR-A01 | Symlink 安装时，cache 目录为 `.skills-registry/cache/{name}/` |
| BR-A02 | 如果目标目录已存在同名 skill，覆盖安装（更新场景） |
| BR-A03 | MCP 配置合并时，同名 server 覆盖旧配置 |
| BR-A04 | Agent 配置安装时，先装 skills，再装 mcp，最后写 agent json |
| BR-A05 | 创建符号链接前检查目标是否已是 symlink，是则先删除 |
| BR-A06 | 文件写入使用 UTF-8 编码 |
| BR-A07 | 目录不存在时自动创建（mkdir -p 语义） |

## Schema 校验规则

| 规则 | 描述 |
|------|------|
| BR-V01 | git_url 必须是合法的 Git URL（https:// 或 git@ 开头） |
| BR-V02 | commit_hash 必须是 40 字符的十六进制字符串 |
| BR-V03 | tags 列表最多 10 个，每个 tag 最长 32 字符 |
| BR-V04 | MCP transport 只允许 "stdio", "sse", "streamable-http" |
| BR-V05 | 分页参数: page >= 1, size 范围 [1, 100] |
