# Unit 2: Backend — Business Rules

## 资产注册规则

| 规则 | 描述 |
|------|------|
| BR-B01 | Skill name 全局唯一，同名注册返回 409 Conflict |
| BR-B02 | MCP Server name 全局唯一 |
| BR-B03 | Agent Config name 全局唯一 |
| BR-B04 | 只有资产的 author 或 admin 可以更新/删除资产 |
| BR-B05 | 删除资产为软删除（标记 is_deleted），不物理删除 |
| BR-B06 | 外部导入的 Skill 标记 source="external"，内部发布的标记 source="internal" |

## Git 操作规则

| 规则 | 描述 |
|------|------|
| BR-G01 | git clone 超时 60 秒 |
| BR-G02 | 只支持 HTTPS 和 SSH 协议的 Git URL |
| BR-G03 | 浅克隆（--depth 1）减少网络和磁盘开销 |
| BR-G04 | 克隆失败时清理临时目录，返回明确错误信息 |
| BR-G05 | 临时目录使用系统 tmpdir，前缀 "skills-" |

## 认证规则

| 规则 | 描述 |
|------|------|
| BR-AU01 | API Key 格式: "sr_" + 43 字符 base64url |
| BR-AU02 | API Key 存储为 bcrypt hash，明文仅在生成时返回一次 |
| BR-AU03 | 所有 /api/v1/* 端点需要认证（除 /api/v1/auth/register） |
| BR-AU04 | admin 端点需要 role="admin" |
| BR-AU05 | 禁用用户的 API Key 立即失效 |

## 搜索规则

| 规则 | 描述 |
|------|------|
| BR-SR01 | 搜索使用 ILIKE（大小写不敏感） |
| BR-SR02 | 搜索范围: name + description |
| BR-SR03 | tag 筛选使用 PostgreSQL ANY() 操作符 |
| BR-SR04 | 默认排序: installs DESC（安装量降序） |
| BR-SR05 | 分页默认: page=1, size=20, 最大 size=100 |

## 安装统计规则

| 规则 | 描述 |
|------|------|
| BR-IN01 | 每次安装记录 InstallLog（asset_type, asset_id, user_id, agent_type） |
| BR-IN02 | 同时更新资产的 installs 计数（原子操作） |
| BR-IN03 | 同一用户重复安装同一资产仍计数（不去重） |

## 外部源同步规则

| 规则 | 描述 |
|------|------|
| BR-SY01 | 同步时比较 commit hash，相同则跳过 |
| BR-SY02 | 同步发现新 Skill 时自动注册，已存在的更新元数据 |
| BR-SY03 | 同步失败不影响其他源的同步 |
| BR-SY04 | 记录每次同步的时间和结果 |
