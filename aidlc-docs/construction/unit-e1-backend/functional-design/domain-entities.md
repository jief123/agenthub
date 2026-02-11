# Unit E1: 后端 API 扩展 — 领域实体变更

## User [MOD]

```python
class User:
    id: int                    # [---] 不变
    username: str              # [---] 不变
    display_name: str | None   # [---] 不变
    email: str                 # [---] 不变
    role: str                  # [---] 不变 ("user" | "admin")
    password_hash: str | None  # [NEW] bcrypt hash，Web 登录用
    api_key_hash: str | None   # [---] 不变
    is_active: bool            # [---] 不变
    created_at: datetime       # [---] 不变
    updated_at: datetime       # [---] 不变
```

**变更说明**: 仅新增 `password_hash` 字段。密码和 API Key 是两种独立的认证方式：
- 密码用于 Web UI 登录
- API Key 用于 API 调用（CLI + Web 前端请求）
- 登录成功后返回 API Key，前端后续请求使用 API Key

## Pydantic Schemas [NEW/MOD]

```python
# 注册请求
class UserRegister(BaseModel):
    username: str          # 3-64 chars
    email: EmailStr
    password: str          # min 8 chars

# 登录请求
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 登录/注册响应
class AuthResponse(BaseModel):
    user: UserPublic
    api_key: str           # 明文 API Key

# 用户公开信息（嵌入到资产响应中）
class UserPublic(BaseModel):
    id: int
    username: str
    display_name: str | None

# 发布统计
class PublishStats(BaseModel):
    skill_count: int
    mcp_count: int
    agent_count: int
    total_installs: int

# Admin 资产删除
class AdminAssetDelete(BaseModel):
    asset_type: Literal["skill", "mcp", "agent"]
    asset_id: int
```

## 其他实体 [---] 不变
- Skill — 不变（已有 author_id + author relationship）
- MCPServer — 不变（已有 author_id + author relationship）
- AgentConfig — 不变（已有 author_id + author relationship）
- InstallLog — 不变
- SyncSource — 不变
