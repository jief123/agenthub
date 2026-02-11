# Unit of Work Dependency - 依赖矩阵

## 依赖矩阵

```
              Unit 1    Unit 2    Unit 3    Unit 4    Unit 5
              Shared    Backend   Frontend  CLI       Docker
Unit 1         -         -         -         -         -
Unit 2         ✓         -         -         -         -
Unit 3         -         ✓(API)    -         -         -
Unit 4         ✓         ✓(API)    -         -         -
Unit 5         -         ✓         ✓(build)  -         -
```

## 开发顺序

```
Phase 1:  Unit 1 (Shared)
              │
Phase 2:  Unit 2 (Backend)
              │
Phase 3:  Unit 3 (Frontend)  ←── 可与 Unit 4 并行
          Unit 4 (CLI)       ←── 可与 Unit 3 并行
              │
Phase 4:  Unit 5 (Docker)
```

### 关键路径
```
Unit 1 → Unit 2 → Unit 3/4 → Unit 5
```

### 并行机会
- Unit 3 (Frontend) 和 Unit 4 (CLI) 可以并行开发
  - 两者都依赖 Unit 2 的 API 接口定义，但彼此无依赖
  - 可以基于 API 接口文档（OpenAPI spec）独立开发

## 依赖类型说明

| 依赖关系 | 类型 | 说明 |
|---------|------|------|
| Unit 2 → Unit 1 | 代码依赖 | Backend import shared schemas/adapters/parsers |
| Unit 3 → Unit 2 | 接口依赖 | Frontend 调用 Backend REST API |
| Unit 4 → Unit 1 | 代码依赖 | CLI import shared schemas/adapters |
| Unit 4 → Unit 2 | 接口依赖 | CLI 调用 Backend REST API |
| Unit 5 → Unit 2,3 | 构建依赖 | Docker 打包 Backend + Frontend build |

## 集成测试点

| 集成点 | 涉及 Units | 测试内容 |
|--------|-----------|---------|
| API 契约 | 2 + 3 | Frontend 调用 Backend API 正确性 |
| API 契约 | 2 + 4 | CLI 调用 Backend API 正确性 |
| Adapter 共享 | 1 + 4 | CLI 使用 shared Adapter 安装文件正确性 |
| 端到端 | 2 + 3 + 5 | Docker Compose 启动后 Web UI 可用 |
| 端到端 | 2 + 4 | CLI 注册 + 安装完整流程 |
