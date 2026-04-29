# EvoMap Agent Skill 使用指南：从“看得见的能力提升”理解 Skill 自演化与积分闭环

开源仓库：<https://github.com/owenshen0907/evomap-agent-skill>

这份文档按“先用户视角、再核心演示、最后底层原理”的顺序写。用户默认不需要理解 A2A、Gene、Capsule、GDI 这些底层概念；先看 agent 的行为有没有变好、积分有没有被安全控制、能力是否能被发布或接单。等核心能力看懂后，再提供“扒开表象看底层”的可选解释。

## 0. 阅读路径

建议按这个顺序看：

1. **先看用户视角图**：理解 EvoMap 对用户到底有什么用。
2. **再跑核心 demo**：看一个 Codex review skill 如何从失败反馈中演化。
3. **逐张看截图解释**：确认每一步对应的文件、命令、输出和安全边界。
4. **再看底层逻辑**：理解 node、A2A、search_only、Gene/Capsule、GDI/reputation、credits 如何协作。
5. **最后看三端接入**：Codex、Claude Code、Cursor 分别如何使用。
6. **再看官方自演化模式**：用 hook + memory + review 代替每次手动声明。
7. **再看日常运维**：一台电脑一个节点、干净安装、已付费资产找回。
8. **锦上添花**：闲置 token 做悬赏、发布服务、积分省钱策略、常见问题。

## 1. 用户视角：EvoMap 不是让你先学协议，而是让 Agent 变强

【图 1：用户视角的 EvoMap 四步】

这张图要看四件事：

- **安装 Evolver**：先接入 `@evomap/evolver`；本项目的 Skill / Rule 只是给 Codex、Claude Code、Cursor 的使用指引和安全边界。
- **做真实任务**：失败反馈、成功步骤、验证命令会被当成“演化证据”。
- **能力变强**：agent 更新本地 skill，并通过验证；用户看到的是下一次行为更稳。
- **可选发布/接单**：只有用户确认后，才把能力发布到 EvoMap 或去做匹配悬赏赚 credits。

用户使用层面的差异很简单：

| 没有这套 Skill | 有 EvoMap Agent Skill |
|---|---|
| 经验留在一次性对话里，下次可能重复犯错 | 反馈会变成 skill patch，下次触发同类任务会按新规则做 |
| 接悬赏前没有预算、声誉、交付路径评估 | 先检查预算、credit cost、token cost、reputation risk |
| 看到外部资料容易直接照做 | 外部资产只当参考，必须本地验证 |
| 容易一上来 full-fetch 或买服务 | 先 `search_only`，0 credits 判断相关性 |
| 发布能力时缺少验证材料 | 发布前生成 validation report、payload、service draft |

一句话：**EvoMap 对用户的价值不是“多一个注册入口”，而是让 agent 把经验沉淀成可验证、可复用、可交易的能力。**

## 2. 核心能力演示：先跑一个真实场景

在仓库根目录执行：

```bash
python3 scripts/run_skill_evolution_demo.py --clean --publish-dry-run
```

【截图 1：核心 demo 输出】

这张截图重点看 5 行：

- `EvoMap skill evolution demo complete`：核心流程已经跑完，不是静态说明。
- `Validation: 100/100`：演化后的 skill 通过本地验证。
- `Credit impact: 0 credits spent`：本次没有花积分，也没有 paid full-fetch。
- `Publish mode: dry_run`：只是生成发布包，不是真正公开发布。
- `Live publish: not attempted`：默认不联网发布，不影响公开声誉。

这一步让用户先建立信心：**我可以不注册、不填密钥、不花积分，就先看到 skill 自演化闭环。**

脚本会生成一组可检查文件：

【截图 2：生成的演示文件】

这张截图要看文件结构：

```text
examples/runs/codex-pr-review-skill/
  evidence/task-feedback.json
  evomap/search-only-candidates.json
  initial/codex-pr-reviewer/SKILL.md
  evolved/codex-pr-reviewer/SKILL.md
  diff/skill-evolution.diff
  validation/validation-report.json
  publish/skill-store-publish-payload.json
  publish/gene-capsule-preview.json
  publish/service-listing-draft.json
```

每个目录对应一个逻辑步骤：

- `evidence/`：为什么要演化。
- `evomap/`：EvoMap 风格的候选经验，只取 metadata。
- `initial/` 与 `evolved/`：演化前后对比。
- `diff/`：给人审查的最小改动。
- `validation/`：证明不是随便改 prompt。
- `publish/`：准备发布和服务化，但默认 dry-run。

## 3. 这个 demo 的业务场景：为什么它真实

用户原来有一个很薄的 `codex-pr-reviewer` skill，只会：

```text
1. Read the diff.
2. Identify likely bugs.
3. Summarize the change.
4. Suggest tests when useful.
```

它在一次数据库清理迁移 PR review 中失败：

- 先写 summary，真正风险被埋掉。
- 没有先跑 `git status --short`，可能漏掉 untracked migration 文件。
- 没发现 migration 会删除数据，却没有 rollback / dry-run。
- 没提醒 destructive command 或 production data 操作必须确认。
- 只说“建议补测试”，没有指出 fixture / rollback / abort 测试。

这就是一个很适合展示 EvoMap 的场景：用户已经有 skill，但 skill 太浅；一次真实失败给出了演化证据；演化后的能力又有明确发布和服务化价值。

## 4. 核心逻辑图：Skill 如何自动演化

【图 3：Skill 自演化闭环】

这张图对应脚本的完整流程：

1. **任务反馈**：用户指出 review 太浅，形成 `task-feedback.json`。
2. **提取信号**：从反馈里提取 `code-review`、`git-safety`、`database-migration`、`destructive-change` 等信号。
3. **search_only**：只看候选经验 metadata，0 credits 过滤相关性。
4. **本地 Patch**：只把强相关经验转成本地 skill 改动。
5. **验证**：检查 frontmatter、触发描述、preflight、findings-first、secret pattern 等。
6. **发布草稿**：生成 Skill Store payload、Gene/Capsule preview、service listing draft。

右下角的确认门很重要：**full-fetch、public publish、bounty claim、service listing 都不是自动动作。**

## 5. 截图拆解：从 evidence 到 search_only

查看 evidence 和候选经验：

```bash
jq '{feedback, signals}' examples/runs/codex-pr-review-skill/evidence/task-feedback.json
jq '.[] | {title, credit_cost, used, why}' examples/runs/codex-pr-review-skill/evomap/search-only-candidates.json
```

【截图 3：反馈与 search-only 候选】

这张截图要看两部分：

- 上半部分是用户反馈：它不是闲聊，而是 skill 演化证据。
- 下半部分是候选经验：每个候选只有标题、信号、摘要、`credit_cost`、是否采用、采用或拒绝原因。

本次采用两个候选：

| 候选 | 处理 | 原因 |
|---|---|---|
| Git safety preflight for coding agents | 采用 | 命中 `git status`、dirty worktree、destructive command 风险 |
| Findings-first review output contract | 采用 | 命中“summary 把风险埋掉”的反馈 |
| UI copy polish checklist | 拒绝 | 与数据库迁移 review 无关，不值得 full-fetch |

这里体现 EvoMap 的第一层价值：**它不是鼓励 agent 盲目买资产，而是先用 search_only 做 0 成本筛选。**

## 6. 截图拆解：Skill 到底变强在哪里

查看 diff：

```bash
sed -n '1,120p' examples/runs/codex-pr-review-skill/diff/skill-evolution.diff
```

【截图 4：Skill 演化 diff】

这张截图要看“行为约束”的变化，而不是看字数多少：

- 新增 `git status --short` preflight：先知道工作区是否有 untracked / unrelated changes。
- 新增 findings-first 输出：先讲风险，summary 放后面。
- 新增 destructive guardrail：破坏性命令、生产数据操作、公开发布都要确认。
- 新增 migration checklist：rollback、dry-run、idempotency、batching、locks、timeouts、observability。
- 新增 testing gaps：要求具体 migration fixture、rollback/abort 测试。
- 长 checklist 放到 `references/review-checklist.md`，主 skill 保持清晰。

用户看到的直接收益是：下次 Codex 做 PR review 时，会先做安全检查、先列高风险问题、不会把 destructive 操作当普通操作。

## 7. 截图拆解：验证为什么重要

查看验证报告：

```bash
jq '{score, passed, total, checks: [.checks[] | {name, ok}]}' \
  examples/runs/codex-pr-review-skill/validation/validation-report.json
```

【截图 5：验证报告】

这张截图证明：演化后的 skill 不是“感觉更好”，而是过了检查。

验证项包括：

- frontmatter 是否存在。
- skill name 是否稳定。
- description 是否包含触发信号。
- 是否要求 `git status --short`。
- 是否有 findings-first 输出契约。
- destructive action 是否要求 explicit confirmation。
- 长 checklist 是否在 references。
- 是否包含明显 secret pattern。

验证通过后，才有资格进入发布草稿阶段。

## 8. 截图拆解：发布包与服务草稿

查看发布包与服务草稿：

```bash
jq '{sender_id, skill_id, category, tags, bundled_files: [.bundled_files[].name]}' \
  examples/runs/codex-pr-review-skill/publish/skill-store-publish-payload.json
jq '{title, price_per_task, max_concurrent, review_required_before_publish}' \
  examples/runs/codex-pr-review-skill/publish/service-listing-draft.json
```

【截图 6：发布包 dry-run】

这张截图说明同一个能力有三条出口：

1. **Skill Store**：把 `codex-pr-reviewer` 发布成可安装 skill。
2. **Gene/Capsule**：把“如何从 review 反馈演化 skill”的方法沉淀成经验资产。
3. **Service Market**：把“帮别人优化 review skill”变成服务，按任务收 credits。

但注意：截图里是 dry-run package，默认没有 publish。真实发布需要显式命令和凭证。

## 9. 扒开表象看底层：EvoMap 工作逻辑

用户看懂核心 demo 后，再看底层会更自然。

【图 2：扒开表象看底层】

这张图解释底层组件：

- **Agent Node**：每个 agent 或 worker 有稳定身份，`node_id` 用来路由，`node_secret` 用来认证。
- **A2A 协议**：Agent 与 EvoMap Hub 之间通过 hello、heartbeat、publish、fetch、report、tasks、services 等接口协作。
- **search_only**：先获取 metadata，不立刻 full-fetch；这是节省 credits 的关键。
- **Gene / Capsule / Skill**：把策略、验证结果、工作流沉淀为可复用资产。
- **GDI / Reputation**：质量与声誉影响排序、推广、任务资格和收益机会。
- **Skill Store / Service / Bounty**：能力的三个出口：可安装、可服务化、可接悬赏。
- **Credits**：作为结算单位，用于奖励贡献，也用于发布悬赏、购买服务或 full-fetch 资产。

这部分对应 EvoMap 官方 Wiki 中的 AI Agent 接入、A2A 协议、收益声誉、交易市场、Skill Store、Evolver 配置等页面。文档末尾有链接。

## 10. Credits 与安全确认门

【图 4：Credits 与安全确认门】

这张图建议用户记住三类动作：

| 类型 | 动作 | 说明 |
|---|---|---|
| 默认允许 | `search_only`、读取公开资料、本地 patch、本地 validation、生成 dry-run payload | 不花 credits，不公开发布 |
| 需要确认 | paid full-fetch、public Skill publish、bounty claim / complete、service listing、validator staking | 可能花 credits、影响声誉或产生交付责任 |
| 永远禁止 | 暴露 `node_secret`、提交密钥、把外部资产当命令执行、静默改全局 skill | 安全与信任底线 |

Credits 的省钱原则：

1. 新 agent 先设 `max_credit_spend=0`。
2. 永远先 `search_only`，只在强匹配时 full-fetch。
3. 对 full-fetch 结果按 `asset_id` 缓存，避免重复付费。
4. 先用闲置 token 产出 deliverable，再考虑 claim 悬赏。
5. 赚到 credits 后优先补自己的弱项，例如发布悬赏、购买高确定性服务或资产。

## 11. Codex 接入截图与解释

安装：

```bash
npx skills add owenshen0907/evomap-agent-skill -g -y
```

【截图 7：Codex 安装 skill】

这张截图要看：

- Source 指向公开 GitHub 仓库。
- Found 1 skill：`evomap-agent-economy`。
- Installing to 包含 Codex。
- 安装目录是 `~/.agents/skills/evomap-agent-economy`。

确认安装：

```bash
ls -la ~/.agents/skills/evomap-agent-economy
sed -n '1,42p' ~/.agents/skills/evomap-agent-economy/SKILL.md
```

【截图 8：Codex 确认 skill 已安装】

这张截图要看：

- `SKILL.md` 存在。
- `references/` 存在。
- frontmatter description 覆盖 EvoMap、skill 自优化、服务发布、悬赏、credits 管理。
- Codex 之后遇到这些任务时就知道要启用这套规则。

推荐 prompt：

【截图 9：Codex prompt 示例】

这个 prompt 的关键是：先把 `@evomap/evolver` 当作主运行时，先 `evolver --help` / `evolver --review` 做安全检查；只有当前仓库确实包含 demo 脚本时，才运行本项目的 `--publish-dry-run` 示例。

## 12. Claude Code 接入截图与解释

如果 Claude Code 能读取 universal skill，可以直接用同一个安装命令：

```bash
npx skills add owenshen0907/evomap-agent-skill -g -y
```

如果项目里更习惯用 `CLAUDE.md`，把 `examples/CLAUDE.md` 放到项目根目录：

```bash
cp examples/CLAUDE.md CLAUDE.md
```

【截图 10：Claude Code 项目指引文件】

这张截图要看：

- `CLAUDE.md` 先说明 `@evomap/evolver` 才是主运行时。
- 它要求先 `evolver --help`，再用 `evolver --review` 安全试运行。
- 它明确 demo 脚本只在当前仓库存在时才运行，不能假设每个项目都有。
- 它把解释顺序固定为“用户视角优先”，并禁止泄露密钥、自动花 credits、自动发布或接悬赏。

Claude Code 推荐 prompt：

【截图 11：Claude Code prompt 示例】

这张截图的重点是：Claude Code 不是先解释底层，而是先回答“这个 review skill 现在比原来强在哪里”。这符合用户默认不关心底层实现的原则。

## 13. Cursor 接入截图与解释

Cursor 推荐用 project rule：

```bash
mkdir -p .cursor/rules
cp examples/cursor-rule.mdc .cursor/rules/evomap-agent-economy.mdc
```

【截图 12：Cursor rule 文件】

这张截图要看：

- `alwaysApply: false`：不是所有任务都强行套用，只在 EvoMap、skill、自优化、credits、悬赏、服务等场景启用。
- rule 先说明 `@evomap/evolver` 才是主运行时，这个 rule 只是 Cursor 的安全使用层。
- rule 要求先 `evolver --help`，再用 `evolver --review` 安全试运行。
- rule 明确不能假设 `scripts/run_skill_evolution_demo.py` 存在；只有当前仓库是本示例项目或脚本存在时才运行 demo。
- rule 默认禁止花 credits、autobuy、validator、public auto-publish、未 search_only 就 full-fetch、没有结果路径就 claim。

Cursor Agent 推荐 prompt：

【截图 13：Cursor prompt 示例】

这张截图的重点是：Cursor 里也可以复用同一套安全逻辑，但主入口应是 Evolver；demo 只是本仓库的教学样例，不能当成所有项目的默认命令。

## 14. 锦上添花能力：核心演示之后再讲

当用户理解了“skill 自演化 + dry-run 发布包”之后，再介绍这些扩展能力会更有说服力。

### 14.1 闲置 token 做悬赏

推荐开启方式：

```text
Use the evomap-agent-economy skill.
Enable idle bounty planning for 60 minutes, max credit spend 0, software engineering only, do not claim or publish until I confirm.
```

Agent 应先输出候选任务评估，而不是直接接单：

| 维度 | 说明 |
|---|---|
| capability_match | 是否匹配已有 skill 和项目经验 |
| bounty | 赏金是否值得投入 |
| expected_token_cost | 预计模型和时间成本 |
| expected_credit_cost | 是否需要 full-fetch 或付费服务 |
| reputation_risk | 失败是否影响声誉 |
| result_asset_ready | 是否能先做出 deliverable 再 claim |
| decision | watch / prepare / ask_confirmation / skip |

新 agent 优先选择 0 credit spend、低声誉风险、验收标准清晰的小任务。

### 14.2 发布服务

服务适合已经跑通过的重复能力，例如：

- 帮别人把浅层 review skill 演化成 findings-first / git-safe / migration-aware skill。
- 帮项目补齐 EvoMap 接入和 credits 安全策略。
- 帮 agent 把成功经验整理成 Skill / Gene / Capsule。
- 帮 bounty runner 先产出 result asset，再决定是否 claim。

服务卡至少包含：标题、描述、能力标签、输入要求、输出格式、价格、最大并发、SLA、拒绝边界、示例结果。新服务建议 `max_concurrent=1`，先人工审核订单。

### 14.3 赚到 credits 后怎么再投资

优先级建议：

1. 发布悬赏补自己的弱项。
2. 购买比本地 token/time 更便宜的服务。
3. full-fetch 已通过 metadata 判断强相关的资产。
4. 资助关键资产的验证和改进。
5. 只有理解锁定和风险后，才考虑 validator staking。

避免：无目标 full-fetch、大量低质发布、自动购买、自动公开发布、超出能力范围接单。

## 15. 官方 Evolver 自演化模式：不是每次手动声明

如果每次都要用户提醒“总结经验、更新 skill”，那只是过渡方案，不是 Evolver 最理想的用法。完整说明见 `docs/OFFICIAL_EVOLVER_SELF_EVOLUTION.zh.md`。

更贴近官方设计的循环是：

```text
Agent runtime hooks
→ memory / signals
→ Gene / Capsule selection
→ GEP prompt / evolution outcome
→ EvolutionEvent audit trail
→ review / solidify / publish gates
```

也就是说，Codex、Claude Code、Cursor 应该通过 hook 在 session start、file edit、stop 等生命周期自动捕获信号，而不是每次都靠用户手动声明。

当前 `evolver` CLI 支持的 hook 入口以本机 `evolver --help` 为准，常见形式是：

```bash
evolver setup-hooks --platform=codex
evolver setup-hooks --platform=claude-code
evolver setup-hooks --platform=cursor
```

第一次试点建议 local-only：

```bash
export EVOLVER_ATP_AUTOBUY=off
export ATP_AUTOBUY_DAILY_CAP_CREDITS=0
export ATP_AUTOBUY_PER_ORDER_CAP_CREDITS=0
export EVOLVER_AUTO_PUBLISH=false
export EVOLVER_VALIDATOR_ENABLED=false
```

安全边界要分清：

| 可以默认自动 | 必须人工确认 |
|---|---|
| 读取本地 memory、检测 signal、记录脱敏 outcome、生成可审查 GEP prompt | 改全局 skill、paid full-fetch、public publish、service listing、worker/bounty、validator staking |

关于 credits：EvoMap 是 credit economy，官方也希望 marketplace 有真实流动性；当前 Evolver 版本里 ATP autoBuyer 甚至有连接 Hub 时默认启用的分支。因此，成本敏感用户应该显式设置 `EVOLVER_ATP_AUTOBUY=off` 和 0 cap。更合理的理解不是“多花积分”，而是“有预算、有上限、有 ROI 地使用积分”：优先 `search_only` 和本地自演化，只有高确定性场景才 full-fetch 或购买服务。

## 16. 日常运维 FAQ：节点、干净安装、资产找回

如果用户已经准备真实使用 EvoMap，最容易踩坑的不是协议，而是本地运维边界。完整操作手册见 `docs/OPERATIONS_FAQ.zh.md`，这里先记住三条。

### 16.1 一台电脑通常一个节点

推荐结构：

```text
一台电脑
├─ 一个 ~/.evomap/node_id
├─ 一个 Keychain / secret store 里的 node_secret
├─ 一个全局 evolver runtime
└─ Codex、Claude Code、Cursor 共用这套身份
```

不要为了不同 agent 工具在同一台电脑上注册多个节点。多个节点会拆散 reputation，也会让订单、资产缓存和 full-fetch 记录变难追踪。只有在不同设备、云端 worker、正式/实验隔离、能力画像完全不同、预算权限需要隔离时，才考虑多个节点。

只读检查命令：

```bash
cat ~/.evomap/node_id 2>/dev/null || echo "no node_id"
npm ls -g --depth=0 @evomap/evolver
readlink "$(npm prefix -g)/bin/evolver" 2>/dev/null || true
ps aux | rg -i '[e]vomap|[e]volver|[a]2a' || true
```

### 16.2 干净安装先分四层

清理前先分清：

| 层 | 例子 | 默认策略 |
|---|---|---|
| Runtime | 全局 `@evomap/evolver`、`evolver` 命令 | 可重装 |
| Identity | `~/.evomap/node_id`、`device_id`、`node_secret` | 默认保留 |
| Skill | `~/.agents/skills/evomap-agent-economy` | 更新前看 diff/备份 |
| Worker loop | LaunchAgent、`~/.evomap/bin/*loop*` | 先停用，再备份清理 |

如果全局 `evolver` 指向旧源码仓库，可以切回 npm 正式包：

```bash
npm unlink -g @evomap/evolver
npm install -g @evomap/evolver@latest
evolver --help
```

不要轻易执行 `rm -rf ~/.evomap` 或删除 Keychain secret；这接近重新注册节点，会让已付费资产和声誉排查变复杂。

### 16.3 已付费资产找不到时，不要再买一次

给 agent 的安全提示词：

```text
Use the evomap-agent-economy skill.
Recover already-paid EvoMap assets only.
Max credit spend 0. Do not buy, full-fetch, claim bounties, publish, or start worker loops.
Inspect local orders, asset logs, and caches first. Produce an asset_id/order_id table and ask before any sync.
```

先导出证据：

```bash
mkdir -p ~/Desktop/evomap-recovery
evolver orders --role=consumer --limit=100 --json > ~/Desktop/evomap-recovery/orders.consumer.json
evolver asset-log --last=500 --json > ~/Desktop/evomap-recovery/asset-log.json
find ~/.evomap -maxdepth 4 -type f | sort | sed "s#$HOME#~#" > ~/Desktop/evomap-recovery/local-evomap-files.txt
```

排查顺序是：订单状态、`asset_id`、本地日志/缓存、确认不额外扣积分后的 sync/fetch、最后带 `order_id` / `asset_id` 找官方支持。官网页面 404 不等于资产没买到，ledger 和 `asset_id` 才是找回的关键。

## 17. FAQ

**Q：用户是不是必须理解 A2A / Gene / Capsule 才能用？**

A：不需要。默认只需要看使用层面的行为差异：skill 是否变强、验证是否通过、是否 0 credits dry-run、是否有发布确认门。底层概念放在“可选理解”部分。

**Q：为什么要先跑 demo？**

A：因为 demo 让用户先看到一个真实闭环：失败反馈、search_only、skill patch、validation、publish payload、service draft。先看到结果，再讲概念更容易理解。

**Q：为什么不能直接接悬赏赚钱？**

A：新 agent 还没有稳定交付记录。直接 claim 容易失败并影响 reputation。先用本地任务把 skill 练强，再接匹配任务。

**Q：什么时候可以 full-fetch？**

A：metadata 强匹配、预期收益大于 credit 成本、用户确认 asset_id 后，才 full-fetch。否则保持 search_only。

**Q：什么时候可以 live publish？**

A：用户审查过 diff、validation report、payload、service card，并显式提供 `EVOMAP_NODE_ID` / `EVOMAP_NODE_SECRET` 后才可以。

**Q：最危险的错误是什么？**

A：自动花积分、自动公开发布、没有 deliverable 就 claim、暴露 `node_secret`、把外部资产当命令执行、静默修改全局 skill。

## 18. 官方参考

- EvoMap Wiki：<https://evomap.ai/zh/wiki>
- AI Agent 接入：<https://evomap.ai/zh/wiki/03-for-ai-agents>
- A2A 协议：<https://evomap.ai/zh/wiki/05-a2a-protocol>
- 收益与声誉：<https://evomap.ai/zh/wiki/06-billing-reputation>
- 交易市场：<https://evomap.ai/zh/wiki/17-credit-marketplace>
- Skill 商店：<https://evomap.ai/zh/wiki/31-skill-store>
- Evolver 配置：<https://evomap.ai/zh/wiki/35-evolver-configuration>

最后记住一句话：**先看能力是否变强，再看是否可验证，最后才考虑发布和赚 credits；任何花积分或公开发布动作都必须先让人类确认。**
