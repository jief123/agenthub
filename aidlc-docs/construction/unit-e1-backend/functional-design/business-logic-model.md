# Unit E1: 后端 API 扩展 — 业务逻辑模型

## 1. 密码注册流程

```
输入: username, email, password
  │
  ├─ 校验 username 唯一性 → 冲突则返回 409
  ├─ 校验 email 唯一性 → 冲突则返回 409
  ├─ 校验 password 长度 >= 8（由 Pydantic schema 保证）
  │
  ├─ bcrypt hash password → password_hash
  ├─ 创建 User(role="user", is_active=True)
  ├─ 自动生成 API Key → hash 存储
  ├─ 创建 JWT token（HS256, 有效期 24 小时, payload: {sub: user_id, exp}）
  │
  └─ 返回 AuthResponse:
       user: 用户信息
       api_key: 明文（仅此一次展示，供 CLI 使用）
       token: JWT（供前端 Web 使用）
       message: 提示安全保存 API Key
```

## 2. 密码登录流程

```
输入: email, password
  │
  ├─ 查找 User by email → 不存在则返回 401
  ├─ 校验 is_active → 禁用则返回 403
  ├─ bcrypt verify password → 不匹配则返回 401
  │
  ├─ 创建 JWT token（HS256, 有效期 24 小时）
  │
  └─ 返回 AuthResponse:
       user: 用户信息
       token: JWT（供前端 Web 使用）
       api_key: None（登录不生成也不覆盖已有 API Key）
```

> 设计要点: 登录只返回 JWT，不触碰 API Key。用户如需 API Key（CLI 场景），
> 可通过 `POST /api/v1/users/me/api-key/regenerate` 单独生成。

## 3. 个人中心 — 我发布的资产

```
输入: current_user.id
  │
  ├─ 查询 skills WHERE author_id = user_id
  ├─ 查询 mcp_servers WHERE author_id = user_id
  ├─ 查询 agent_configs WHERE author_id = user_id
  │
  └─ 返回 { skills: [...], mcps: [...], agents: [...] }
```

## 4. 个人中心 — 我安装的资产

```
输入: current_user.id
  │
  ├─ 查询 install_logs WHERE user_id = user_id, ORDER BY installed_at DESC
  ├─ 关联查询资产名称和类型
  │
  └─ 返回 [{ asset_type, asset_name, installed_at, agent_type }, ...]
```

## 5. 个人中心 — 发布统计

```
输入: current_user.id
  │
  ├─ SUM(installs) FROM skills WHERE author_id = user_id
  ├─ SUM(installs) FROM mcp_servers WHERE author_id = user_id
  ├─ SUM(installs) FROM agent_configs WHERE author_id = user_id
  ├─ COUNT 各类型资产数量
  │
  └─ 返回 { total_installs, skill_count, mcp_count, agent_count }
```

## 6. Admin 跨类型资产列表

```
输入: type(可选), page, size
  │
  ├─ 如果 type 指定 → 查询对应表
  ├─ 如果 type 未指定 → 查询所有表，合并排序
  ├─ 每条记录包含 author 信息
  │
  └─ 返回分页结果
```

## 7. Admin 删除资产

```
输入: asset_type (skill/mcp/agent), asset_id
  │
  ├─ 校验 current_user.role == "admin"
  ├─ 根据 type 定位到对应表
  ├─ 查找资产 → 不存在则返回 404
  ├─ 删除资产记录
  ├─ 删除关联的 install_logs
  │
  └─ 返回 204 No Content
```

## 8. MCP/Agent Top API

```
输入: limit (默认 20)
  │
  ├─ 查询 mcp_servers ORDER BY installs DESC LIMIT limit
  ├─ 查询 agent_configs ORDER BY installs DESC LIMIT limit
  │
  └─ 返回排行列表（包含 author 信息）
```

## 9. 资产 Owner 信息返回

```
所有资产列表/详情 API:
  │
  ├─ SQLAlchemy relationship lazy="joined" 已配置
  ├─ 序列化时包含 author: { id, username, display_name }
  │
  └─ 无需额外查询，ORM 自动 JOIN
```
