# Unit E1: 后端 API 扩展 — 业务规则

## BR-E1-01: 密码注册校验
- username: 3-64 字符，字母数字下划线连字符，唯一
- email: 有效邮箱格式，唯一
- password: 最少 8 字符
- 注册后 role 默认为 "user"
- 注册后自动生成 API Key

## BR-E1-02: 密码登录
- 通过 email + password 登录
- 被禁用的用户（is_active=False）不能登录，返回 403
- 登录成功返回 API Key（如果没有则自动生成）
- 密码使用 bcrypt hash，与现有 API Key hash 方式一致

## BR-E1-03: 认证兼容
- 保留现有 API Key 认证（X-API-Key header）
- 密码登录是获取 API Key 的途径之一
- CLI 继续使用 API Key 认证，不受影响
- Web 前端登录后将 API Key 存储在 localStorage

## BR-E1-04: 资产发布权限
- 所有已登录用户（user + admin）均可发布 Skills、MCP Server、Agent Config
- 发布时 author_id 自动设为 current_user.id
- 无需审核，发布即上架

## BR-E1-05: 资产编辑/删除权限
- 用户只能编辑/删除自己的资产（author_id == current_user.id）
- Admin 可以删除任何人的资产
- 删除资产时同时清理关联的 install_logs

## BR-E1-06: Admin 资产管理
- 仅 Admin 角色可访问 /api/v1/admin/* 端点
- Admin 可查看所有资产（跨类型）
- Admin 可删除任意资产
- 资产类型通过 URL 参数区分：skill / mcp / agent

## BR-E1-07: 个人中心数据隔离
- 用户只能查看自己的发布资产和安装记录
- 发布统计只统计自己资产的安装量
- API Key 管理只能操作自己的 Key

## BR-E1-08: API Key 重新生成
- 重新生成会使旧 Key 立即失效
- 新 Key 明文仅在生成时返回一次
- CLI 用户需要更新本地配置
