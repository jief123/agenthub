# Deployment Architecture — Skills Registry Platform

## 1. MVP 部署架构（双模式）

### 开发/测试模式（SQLite，无需 Docker）
```
┌──────────────────────────────────────────────────────┐
│                    开发者本机                          │
│                                                       │
│  ┌─────────┐     HTTP :8000      ┌────────────────┐  │
│  │ 浏览器   │ ──────────────────► │ uvicorn        │  │
│  │ (JWT)   │                     │ FastAPI :8000   │  │
│  └─────────┘                     │ + React static  │  │
│                                  │ + SQLite .db    │  │
│  ┌─────────┐     HTTP :8000      │                 │  │
│  │ CLI     │ ──────────────────► │                 │  │
│  │(API Key)│                     └────────────────┘  │
│  └─────────┘                                         │
│                                                       │
│  ┌──────────────┐                                    │
│  │ 内部 GitLab   │ ◄── Git clone (SSH/HTTPS)         │
│  └──────────────┘                                    │
└──────────────────────────────────────────────────────┘
```

### 生产模式（Docker Compose + PostgreSQL）
```
┌─────────────────────────────────────────────────────────────┐
│                    企业内网环境                                │
│                                                              │
│  ┌─────────┐     HTTP :8000      ┌────────────────────────┐ │
│  │ 开发者   │ ──────────────────► │   Docker Host          │ │
│  │ (浏览器) │                     │                        │ │
│  └─────────┘                     │  ┌──────────────────┐  │ │
│                                  │  │ app container     │  │ │
│  ┌─────────┐     HTTP :8000      │  │  FastAPI :8000    │  │ │
│  │ 开发者   │ ──────────────────► │  │  + React static  │  │ │
│  │ (CLI)   │                     │  │  + Sync worker    │  │ │
│  └─────────┘                     │  │  + SQLite/PG      │  │ │
│                                  │  └────────┬─────────┘  │ │
│                                  │           │             │ │
│                                  │  ┌────────▼─────────┐  │ │
│                                  │  │ appdata volume    │  │ │
│                                  │  │  (SQLite .db)     │  │ │
│                                  │  └──────────────────┘  │ │
│                                  └────────────────────────┘ │
│                                                              │
│  ┌──────────────┐                                           │
│  │ 内部 GitLab   │ ◄── Git clone (SSH/HTTPS)                │
│  │ / Git Server  │                                           │
│  └──────────────┘                                           │
│                                                              │
│  ┌──────────────┐                                           │
│  │ 外部 GitHub   │ ◄── Git clone (HTTPS, 可选)               │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

> **注意**: 当前 `docker-compose.yml` 默认使用 SQLite 单服务模式。生产环境如需 PostgreSQL，
> 需自行添加 db 服务或连接外部 PG 实例，修改 `DATABASE_URL` 即可。


## 2. 分发渠道

### Docker 镜像
- **Docker Hub**: `jief123/agenthub`
- **多架构支持**: amd64 + arm64
- **拉取方式**: `docker pull jief123/agenthub:latest`

### CLI 工具
- **PyPI 包名**: `agenthub-cli`
- **安装方式**: `pip install agenthub-cli` 或 `uvx agenthub-cli`
- **入口命令**: `agenthub-cli`

## 3. 部署流程

### 首次部署

#### 开发/测试模式（推荐先用这个）
```
1. 克隆项目仓库
2. pip install -e ./shared && pip install -e ./backend
3. cd frontend && npm ci && npm run build && cd ..
4. 设置环境变量（SECRET_KEY, ADMIN_API_KEY 等）
5. uvicorn app.main:app --port 8000 --reload
6. 访问 http://localhost:8000
```

#### Docker Compose 模式（默认 SQLite）
```
1. 安装 Docker + Docker Compose
2. 克隆项目仓库
3. 设置环境变量（SECRET_KEY, ADMIN_API_KEY, ADMIN_PASSWORD）
4. docker compose up -d --build
5. 访问 http://<host>:8000
6. 分发 CLI: pip install agenthub-cli
```

#### 使用预构建镜像
```
1. docker pull jief123/agenthub:latest
2. docker run -d -p 8000:8000 \
     -e SECRET_KEY=your-secret \
     -e ADMIN_API_KEY=sr_your-key \
     -e ADMIN_PASSWORD=your-password \
     -v appdata:/app/backend/data \
     jief123/agenthub:latest
```

### 版本更新
```
1. 拉取最新代码
   - git pull

2. 重新构建
   - docker compose up -d --build
   - SQLite: 应用启动时自动 create_all
   - PostgreSQL: 需手动运行 alembic upgrade head

3. 验证
   - docker compose logs -f app（检查启动日志）
   - 访问 /health 确认服务正常
```

### 回滚
```
1. 停止当前版本
   - docker compose down

2. 切换到上一版本
   - git checkout <previous-tag>

3. 重新构建启动
   - docker compose up -d --build

4. 数据库回滚（PostgreSQL，如需要）
   - docker compose exec app alembic downgrade -1
```

## 4. 认证架构

```
双认证模式:

1. JWT Bearer Token（前端 Web UI）
   - 用户登录 → 服务端签发 JWT（HS256, 24h 过期）
   - 前端请求携带 Authorization: Bearer <token>
   - 服务端验证签名 + 过期时间 → 返回 User 对象

2. API Key（CLI / 自动化）
   - 格式: "sr_" + token_urlsafe(32)
   - 请求携带 X-API-Key header
   - 优先匹配 env ADMIN_API_KEY（明文比较）
   - 其次遍历 DB 用户的 api_key_hash（bcrypt 验证）

3. 环境变量 ADMIN_API_KEY（运维快捷通道）
   - 启动时自动创建 admin 用户（如不存在）
   - 该 Key 直接与 ADMIN_USERNAME 用户绑定
   - 适合 CI/CD 和自动化场景

认证优先级: JWT Bearer → API Key → 401
```

## 5. 生产加固建议

### 反向代理（推荐）
```
追加 nginx 服务到 docker-compose.prod.yml:

nginx:
  image: nginx:alpine
  ports: ["80:80", "443:443"]
  volumes:
    - ./nginx.conf:/etc/nginx/conf.d/default.conf
    - ./certs:/etc/nginx/certs  # TLS 证书
  depends_on: [app]

好处:
  - TLS 终止（HTTPS）
  - 静态文件缓存加速
  - 请求限流（rate limiting）
  - 请求体大小限制
  - app 端口不再对外暴露
```

### 安全加固
```
- 修改默认 ADMIN_PASSWORD（默认 admin123 仅用于开发）
- 生产环境设置强 SECRET_KEY（用于 JWT 签名）
- 使用 Docker secrets 管理敏感配置（替代 .env）
- 定期更新基础镜像（安全补丁）
- 限制容器资源（memory, cpus）
- 非 root 用户运行应用
```

### 监控
```
MVP:
  - docker compose logs 查看日志
  - /health 端点监控（返回 {"status": "ok"}）
  - Docker Compose healthcheck（python urllib 检测）

生产建议:
  - 日志收集: Docker logging driver → ELK / Loki
  - 指标监控: Prometheus + Grafana（可选）
  - 告警: 基于 /health 端点的简单告警
```

## 6. SQLite → PostgreSQL 迁移路径

```
当需要从 SQLite 切换到 PostgreSQL 时:

1. 导出 SQLite 数据
   - 自定义 Python 脚本读取 SQLite → 写入 PG
   - 或使用 pgloader 工具自动迁移

2. 启动 PostgreSQL
   - 添加 db 服务到 docker-compose.yml 或使用外部 PG 实例

3. 修改 DATABASE_URL
   - 从: sqlite+aiosqlite:///./data/skills_registry.db
   - 到: postgresql+asyncpg://user:pass@host:5432/skills_registry

4. 运行 Alembic 迁移
   - alembic upgrade head（创建 PG 表结构）

5. 导入数据
   - 运行迁移脚本

6. 验证
   - 检查数据完整性
   - 测试所有 API 端点

代码改动: 零（SQLAlchemy 抽象层处理差异）
可选优化（迁移后）:
  - tags 字段改为 PG ARRAY + GIN 索引
  - config/embedded 字段改为 JSONB
  - 搜索改为 ILIKE
```

## 7. K8s 迁移路径（Phase 2 参考）

```
Docker Compose → Kubernetes 映射:

app service      → Deployment + Service + HPA
db service       → StatefulSet + PVC（或迁移到 RDS）
appdata vol      → PVC (ReadWriteOnce) 或 EFS
nginx            → Ingress Controller + Ingress
.env             → ConfigMap + Secret
healthcheck      → livenessProbe + readinessProbe
sync worker      → CronJob（独立出来）

迁移步骤:
1. 编写 K8s manifests（或 Helm chart）
2. 数据库迁移到 RDS（推荐）或 K8s StatefulSet
3. 数据迁移: pg_dump → pg_restore
4. DNS 切换
```

## 8. CLI 分发架构

```
CLI 通过 Python 包分发，不需要容器化:

公开分发:
  PyPI: agenthub-cli
  安装: pip install agenthub-cli
  运行: agenthub-cli --help

内部分发:
  内部 PyPI mirror → pip install --index-url <internal> agenthub-cli
  或直接 pip install:
  pip install git+https://<internal-git>/agenthub-cli.git

CLI 技术栈:
  - typer >= 0.12（命令行框架）
  - httpx >= 0.27（HTTP 客户端）
  - rich >= 13.0（终端美化输出）

CLI 配置存储:
  ~/.skills-registry/
  ├── config.toml      # registry_url, api_key
  └── cache/           # 已安装资产的本地缓存
      └── <skill-name>/
```
