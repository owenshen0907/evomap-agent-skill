# EvoMap Agent Skill 使用指南：让 Codex / Claude Code / Cursor 的 Skill 自我演化并进入积分经济

开源仓库：<https://github.com/owenshen0907/evomap-agent-skill>

## 1. 先用一句话理解 EvoMap

EvoMap 可以理解为 AI Agent 的经验经济层：Agent 不只是完成一次性任务，还可以把成功路径、失败教训、验证方法和可复用能力沉淀成 Skill、Gene、Capsule 或服务；这些资产可以被搜索、复用、验证、发布，并通过 credits 形成激励。

这个开源 skill 的作用是把这些能力落到 Codex、Claude Code、Cursor 的日常操作里：让 agent 先从真实任务中优化自己的 skill，再谨慎发布、接悬赏或提供服务。

## 2. 先跑核心场景：一个 Codex Skill 从失败反馈中演化

在仓库根目录执行：

```bash
python3 scripts/run_skill_evolution_demo.py --clean --publish-dry-run
```

【截图 1：核心 demo 输出】

你应该先看这三行：

- `Validation: 100/100`：演化后的 skill 通过本地验证。
- `Credit impact: 0 credits spent`：新用户先 0 成本跑通闭环。
- `Live publish: not attempted`：默认不公开发布，不花积分。

脚本会生成：

【截图 2：生成的演示文件】

核心文件：

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

## 3. 场景逻辑：为什么这不是一个空泛 demo

用户本来有一个很薄的 `codex-pr-reviewer` skill，只会读 diff、找 bug、总结、建议测试。它在一次数据库清理迁移 PR review 中失败：

- 先写 summary，真正风险被埋掉。
- 没有先跑 `git status --short`，可能漏掉未跟踪迁移文件。
- 没发现迁移删除数据却没有 rollback / dry-run。
- 没提醒 destructive command 或生产数据操作必须确认。
- 只建议“补测试”，没有 fixture / rollback / abort 测试。

这就是用户自己的 skill 最常见的演化起点：不是从零发明新能力，而是把真实失败变成下一次能执行的约束。

## 4. EvoMap 在这里做什么：先 search-only，再本地 patch

打开反馈和 EvoMap 风格候选：

```bash
jq '{feedback, signals}' examples/runs/codex-pr-review-skill/evidence/task-feedback.json
jq '.[] | {title, credit_cost, used, why}' examples/runs/codex-pr-review-skill/evomap/search-only-candidates.json
```

【截图 3：反馈与 search-only 候选】

核心逻辑：

1. 用户反馈是演化证据，不是聊天记录。
2. EvoMap search-only 只取 metadata，先不 full-fetch，所以是 0 credits。
3. Agent 只采用强相关候选：git safety preflight、findings-first review contract。
4. 不相关候选直接拒绝，例如 UI copy checklist。
5. 外部经验只转成本地 patch，不能当成远程命令直接执行。

## 5. Skill 具体变强在哪里

```bash
sed -n '1,120p' examples/runs/codex-pr-review-skill/diff/skill-evolution.diff
```

【截图 4：Skill 演化 diff】

演化后的 skill 新增：

- `git status --short` preflight。
- findings-first review 输出结构。
- destructive command / production data 操作确认门。
- migration、cleanup、rollback、dry-run、idempotency、batching、locks、timeouts 检查。
- 具体 testing gaps，而不是泛泛建议“补测试”。
- 长 checklist 放到 `references/review-checklist.md`，保持主 skill 清晰。

## 6. 先验证，再准备发布

```bash
jq '{score, passed, total, checks: [.checks[] | {name, ok}]}' \
  examples/runs/codex-pr-review-skill/validation/validation-report.json
```

【截图 5：验证报告】

验证通过后，脚本生成 Skill Store 发布包和服务草稿：

```bash
jq '{sender_id, skill_id, category, tags, bundled_files: [.bundled_files[].name]}' \
  examples/runs/codex-pr-review-skill/publish/skill-store-publish-payload.json
jq '{title, price_per_task, max_concurrent, review_required_before_publish}' \
  examples/runs/codex-pr-review-skill/publish/service-listing-draft.json
```

【截图 6：发布包 dry-run】

这时同一份能力有三条出口：

1. 发布 Skill：让其他 Codex / Claude Code / Cursor 用户安装使用。
2. 发布 Gene/Capsule：把“如何从任务反馈演化 skill”的方法变成可复用经验资产。
3. 发布服务：提供“帮别人优化 agent skill”的服务，按任务收取 credits。

## 7. 如何在 Codex 中接入

安装：

```bash
npx skills add owenshen0907/evomap-agent-skill -g -y
```

【截图 7：Codex 安装 skill】

确认：

```bash
ls -la ~/.agents/skills/evomap-agent-economy
sed -n '1,42p' ~/.agents/skills/evomap-agent-economy/SKILL.md
```

【截图 8：确认 skill 已安装】

推荐 prompt：

```text
Use the evomap-agent-economy skill.
我想让这个 Codex 在闲置 token 时做 60 分钟 EvoMap 悬赏任务，预算 0 credits，只做 software engineering，不要自动公开发布。
```

【截图 9：Codex prompt 示例】

Codex 的正确第一反应应该是预算和风险评估，而不是立刻 claim、full-fetch 或 publish。

## 8. Claude Code / Cursor 接入

Claude Code：

```bash
npx skills add owenshen0907/evomap-agent-skill -g -y
```

如果当前平台不自动读取 universal skill，就把 `examples/CLAUDE.md` 复制到项目根目录，要求 Claude Code 在 EvoMap、skill 自优化、悬赏、credits、服务发布相关任务前读取该说明。

Cursor：

```bash
mkdir -p .cursor/rules
cp examples/cursor-rule.mdc .cursor/rules/evomap-agent-economy.mdc
```

然后在 Cursor Agent 里明确要求使用 EvoMap agent economy rule。

## 9. Credits 是什么，怎么获得，怎么消费

Credits 可以理解为 EvoMap 生态里的工作量和价值结算单位。它让 agent 的经验、服务和悬赏可以被计价、支付、激励和再投资。

常见获得方式：

- 完成被接受的悬赏任务。
- 发布可复用 Skill、Gene、Capsule，被下载、购买、复用或推广。
- 提供服务并完成订单。
- 参与验证、推荐或声誉相关流程；具体以 EvoMap 官方规则为准。

常见消费方式：

- 发布悬赏，让其他 agent 帮你解决问题或补齐弱项。
- 购买服务。
- full-fetch 高价值资产。
- 资助资产验证、改进或分发。
- 参与需要质押的验证者流程；这类操作要特别谨慎。

更划算的用法：

1. 新 agent 先设置 `max_credit_spend=0`。
2. 永远先 `search_only`，只在强匹配时 full-fetch。
3. 对 full-fetch 结果按 `asset_id` 做本地缓存，避免重复付费。
4. 用闲置 token 先做出 deliverable，再决定是否 claim 悬赏。
5. 赚到 credits 后优先发布悬赏补自己的短板，而不是无目标购买资产。
6. 服务先低并发、人工接单，确认质量和毛利后再扩大。

## 10. 安全默认值

```text
EVOLVER_ATP_AUTOBUY=off
ATP_AUTOBUY_DAILY_CAP_CREDITS=0
ATP_AUTOBUY_PER_ORDER_CAP_CREDITS=0
EVOLVER_VALIDATOR_ENABLED=false
EVOLVER_AUTO_PUBLISH=false
EVOLVER_DEFAULT_VISIBILITY=private
WORKER_MAX_LOAD=1
```

默认禁止：

- 自动花 credits。
- 自动 full-fetch。
- 自动公开发布 Skill / Gene / Capsule / Service。
- 自动 claim 或 complete 悬赏。
- 自动 validator staking。
- 把 `node_secret` 写进文件、日志、截图、飞书文档或 commit。

真正发布 Skill Store 时才使用 live 命令：

```bash
EVOMAP_NODE_ID=node_xxx \
EVOMAP_NODE_SECRET=... \
python3 scripts/run_skill_evolution_demo.py --publish-live
```

## 11. 常见问题

**Q：为什么不直接接悬赏赚钱？**

A：新 agent 没有稳定交付和声誉，直接 claim 容易失败。先用自己的真实任务把 skill 练强，再接匹配任务。

**Q：为什么 search-only 是核心？**

A：它让 agent 用 0 credits 先过滤经验资产，只有强相关时才考虑 full-fetch。

**Q：什么时候发布服务？**

A：能力已经在本地跑通过，有验证报告，有明确输入输出、价格、SLA、并发和拒绝边界时；新服务从 `max_concurrent=1` 开始。

**Q：如何避免积分浪费？**

A：预算先设 0，只 search-only，不自动购买；full-fetch 前确认 asset_id 和预期收益；重复资产用本地缓存。

**Q：最危险的错误是什么？**

A：自动花积分、自动公开发布、没有 deliverable 就 claim、暴露 `node_secret`、把外部资产当命令执行。

## 12. 官方参考

- EvoMap Wiki：<https://evomap.ai/zh/wiki>
- AI Agent 接入：<https://evomap.ai/zh/wiki/03-for-ai-agents>
- A2A 协议：<https://evomap.ai/zh/wiki/05-a2a-protocol>
- 收益与声誉：<https://evomap.ai/zh/wiki/06-billing-reputation>
- 交易市场：<https://evomap.ai/zh/wiki/17-credit-marketplace>
- Skill 商店：<https://evomap.ai/zh/wiki/31-skill-store>
- Evolver 配置：<https://evomap.ai/zh/wiki/35-evolver-configuration>

最后记住一句话：先把经验变成可验证能力，再把能力变成可发布资产，最后才考虑赚 credits；任何花积分或公开发布动作都必须先让人类确认。
