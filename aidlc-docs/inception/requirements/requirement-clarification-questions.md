# 平台增强需求 - 澄清问题

请回答以下问题，在每个 [Answer]: 后填写字母选项。如果没有合适的选项，选择最后一个"Other"并描述。

---

## 需求一：UI/UX 改进

## Question 1
前端 UI 框架选择？当前是纯 inline styles，需要引入 UI 框架来提升视觉效果。

A) Tailwind CSS（utility-first，灵活度高，社区大）
B) Ant Design（企业级组件库，开箱即用，中文友好）
C) shadcn/ui + Tailwind（现代感强，可定制性高）
D) Material UI（Google 风格，组件丰富）
E) Other (please describe after [Answer]: tag below)

[Answer]: 我不需要太复杂的，稍微简单一点的

## Question 2
Skill 详情页的 README 渲染，你期望的效果是？

A) 类似 GitHub 的 Markdown 渲染（代码高亮、表格、图片等完整支持）
B) 类似 npm 包详情页的风格（左侧 README + 右侧元信息侧边栏）
C) 简洁卡片式，只展示关键信息，README 折叠展开
D) Other (please describe after [Answer]: tag below)

[Answer]: github吧，我看skills大部分都是host在github上

## Question 3
首页 Leaderboard 的改进方向？

A) 卡片网格布局（类似 VS Code Extension Marketplace）
B) 保持列表但增强视觉（图标、标签、统计数据更突出）
C) 分类 Tab 展示（Skills / MCP Servers / Agents 分开展示排行）
D) Other (please describe after [Answer]: tag below)

[Answer]: 分类展示我觉得是必要的，同时增强视觉。

---

## 需求二：Admin Portal 独立化

## Question 4
Admin Portal 的独立方式？

A) 同一个前端应用内，通过路由 `/admin/*` 区分，登录后根据角色显示不同导航
B) 完全独立的前端应用（单独的 build、单独的入口 URL，如 `admin.example.com`）
C) 同一应用但有独立的 Admin 布局和侧边栏导航（类似 WordPress 后台）
D) Other (please describe after [Answer]: tag below)

[Answer]: 同一个前端，但是有独立的功能，怎么简单怎么来

## Question 5
Admin Portal 需要包含哪些功能？（当前已有：用户管理、外部源导入）

A) 当前功能 + 平台统计仪表盘（资产数量、安装趋势图表）
B) 当前功能 + 统计仪表盘 + 资产审核/管理（编辑、下架、删除任意资产）
C) 当前功能 + 统计仪表盘 + 资产管理 + 系统配置（同步源管理、平台设置）
D) Other (please describe after [Answer]: tag below)

[Answer]: 1. 同步资源，2. 删除资源 3. 未来可能增加用户管理

---

## 需求三：多用户与 Owner 机制

## Question 6
普通用户注册方式？

A) 开放注册（任何人可以注册账号）
B) 邀请制（Admin 创建账号或发送邀请链接）
C) 开放注册 + Admin 审批（注册后需要 Admin 激活）
D) Other (please describe after [Answer]: tag below)

[Answer]: 未来通过SSO登陆的用户会返回SAML，或者OIDC，这些用户都是企业用户都可以使用除Admin之外的全量功能，现阶段任何人都可以注册，每个人应该还有自己的API Key的管理

## Question 7
普通用户发布 Skills 的权限范围？

A) 可以自由发布，发布即上架（与 Admin 相同，只是不能管理他人的资产）
B) 可以发布，但需要 Admin 审批后才上架
C) 可以发布 Skills，但 MCP Server 和 Agent 配置需要 Admin 审批
D) Other (please describe after [Answer]: tag below)

[Answer]: 我之前描述的不太清楚，除了skills,也可以贡献其他资源。因为是企业内部，所以自由发布不需要审核

## Question 8
Owner 信息在 UI 上的展示方式？

A) 在资产卡片/列表中显示 owner 头像 + 用户名，点击可查看该用户的所有资产
B) 只显示 owner 用户名，不可点击
C) 显示 owner 用户名 + 来源标签（如"Admin 同步"、"社区贡献"等）
D) Other (please describe after [Answer]: tag below)

[Answer]: 只显示用户名

## Question 9
用户个人中心需要哪些功能？

A) 我发布的资产 + 我安装的资产 + API Key 管理
B) A 的基础上 + 个人资料编辑（头像、显示名、邮箱）
C) B 的基础上 + 发布统计（我的资产被安装了多少次）
D) Other (please describe after [Answer]: tag below)

[Answer]: A+发布统计

## Question 10
对于 Admin 通过外部源同步导入的 Skills，owner 应该是？

A) 固定为执行同步操作的 Admin 用户
B) 显示为"System"或"Registry"等系统账号，与个人 Admin 区分
C) 保留原始作者信息（从 SKILL.md 提取），同时标记导入者
D) Other (please describe after [Answer]: tag below)

[Answer]: 你能提取到原作者吗，如果可以提取原作者，如果提取原作者不稳定，可以留Admin的用户

