# Skills Registry 平台 - 需求澄清问题

基于你的初步设计文档和群聊讨论，我需要澄清以下关键问题来完善需求。
请在每个问题的 [Answer]: 后填写你选择的字母。

---

## Question 1
平台的核心定位是什么？

A) 纯 Skills 注册与分发（只管 SKILL.md 配置文件）
B) Skills + MCP Server 配置的统一注册与分发
C) Skills + MCP Server + Agent 配置（prompt + MCP + Skills 组合）的全资产管理
D) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 2
Skills 的源码存储策略是什么？

A) 平台只存元数据，源码始终在用户自己的 Git 仓库中（平台通过 Git URL 引用）
B) 平台提供内置 Git 存储，用户直接推送到平台
C) 两者都支持：可以引用外部 Git，也可以直接上传到平台
D) Other (please describe after [Answer]: tag below)

[Answer]: A,

---

## Question 3
目标客户的 Git 基础设施是什么？

A) 主要是 GitLab（自建）
B) 主要是 Gitea / Gogs
C) 主要是 GitHub Enterprise
D) 需要同时支持多种 Git 服务
E) Other (please describe after [Answer]: tag below)

[Answer]: Github 公开版本(有一些公网公开的skills)， Gitlab

---

## Question 4
认证与用户体系如何设计？

A) 必须对接客户现有 SSO（OIDC/SAML/LDAP），不提供独立用户体系
B) 提供独立用户体系（用户名密码注册），可选对接 SSO
C) 以 SSO 为主，同时支持 API Key 方式供 CLI 和 CI/CD 使用
D) Other (please describe after [Answer]: tag below)

[Answer]: 应该有命令行，所以通过API Key是最合理的。客户已经对接了AWS IDC，客户也有自己的SSO和IDP。具体用哪个下一轮展开讨论一下

---

## Question 5
Skill 发布流程需要审核吗？

A) 不需要审核，发布即上架（适合信任度高的内部团队）
B) 需要管理员审核后才能上架
C) 可配置：管理员可以选择开启或关闭审核流程
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 6
是否需要"外部源同步"功能（从公网 skills.sh 镜像优质 Skills 到内部）？

A) MVP 阶段不需要，后续再考虑
B) 需要，这是核心卖点之一（帮客户把外网好用的 Skills 搬进来）
C) 需要，但只支持管理员手动导入，不做自动同步
D) Other (please describe after [Answer]: tag below)

[Answer]: B\C

---

## Question 7
CLI 工具的兼容性策略是什么？

A) 完全兼容 skills.sh 的 `npx skills` 命令，在其基础上扩展私有 Registry 支持
B) 开发独立的 CLI 工具（如 `npx skill-hub`），不依赖 skills.sh
C) Fork skills.sh 的 CLI，修改为支持私有 Registry
D) Other (please describe after [Answer]: tag below)

[Answer]: 自己构建一套吧，基于Python环境， uvx这样的，第一版要支持Kiro ide 和kiro cli

---

## Question 8
部署形态的优先级是什么？

A) Docker Compose 优先（单机部署，面向中小团队）
B) Kubernetes / Helm 优先（面向大型企业）
C) 两者同等重要，都需要在 MVP 中支持
D) Other (please describe after [Answer]: tag below)

[Answer]: K8S,不过部署不重要，可以打包成docker本地测试运行即可，具体客户那边的落地过程不在这个项目里

---

## Question 9
平台需要支持多租户吗？

A) 不需要，一个平台实例服务一个组织
B) 需要，支持"团队空间"概念（同一平台内不同团队有独立空间）
C) 需要完整的多租户隔离（不同组织共用一个平台实例）
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 10
技术栈偏好？

A) Node.js 全栈（前后端 TypeScript，与 skills.sh 生态一致）
B) Go 后端 + React 前端（更适合私有化部署，二进制分发）
C) Python 后端 + React 前端
D) Java/Kotlin 后端 + React 前端（企业客户更熟悉）
E) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 11
MVP 的交付时间预期是多少？

A) 2 周内（极简 MVP，只有核心功能）
B) 4 周内（标准 MVP，包含基本完整的功能）
C) 8 周内（完整 MVP，包含企业特性）
D) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 12
平台是否需要支持 Skill 的版本管理？

A) 不需要，每次发布覆盖上一版
B) 需要基本版本管理（保留历史版本，可回退）
C) 需要语义化版本管理（semver），支持版本范围安装
D) Other (please describe after [Answer]: tag below)

[Answer]: 版本管理是不是在Git上？哪些数据需要在注册工具上，哪些在Git上，感觉更多的是描述信息对吧，类似于从skill.md里面提取的一些信息。这个信息是否要有版本，或者说skills代码更新了这个版本是不是会自动更新？应该是存在一个问题，这个可能手动管理吧，我看skills.sh上面是有版本的，他是怎么做到版本一致性的？

---

## Question 13
是否需要通知和集成能力？

A) MVP 不需要，后续再加
B) 需要 Webhook 通知（新 Skill 发布时通知到 IM）
C) 需要完整的集成能力（Webhook + CI/CD 触发 + IM 机器人）
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 14
安全扫描的深度？

A) MVP 不做自动扫描，依赖人工审核
B) 基础扫描（检查敏感信息泄露、危险命令）
C) 深度扫描（依赖分析、网络外连检测、代码静态分析）
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 15
这个产品的商业模式是什么？

A) 开源项目，免费提供，靠服务收费
B) 商业软件，按实例/用户数收费
C) 作为现有产品（如智能运维平台）的一个模块
D) 先内部使用验证，再决定商业化路径
E) Other (please describe after [Answer]: tag below)

[Answer]: A
