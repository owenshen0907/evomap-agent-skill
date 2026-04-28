# Codex 实操：用 EvoMap 让自己的 Skill 演化并准备发布

这一版把实操放在前面。你可以先按截图跑通，再回头理解 EvoMap 的概念。

开源仓库：<https://github.com/owenshen0907/evomap-agent-skill>

## 1. 安装到 Codex 可读的位置

推荐用 universal skills installer：

```bash
npx skills add owenshen0907/evomap-agent-skill -g -y
```

实际终端输出如下：

![安装 skill](screenshots/codex-walkthrough/02-install-skill.png)

关键点：

- 找到 1 个 skill：`evomap-agent-economy`。
- 安装到：`~/.agents/skills/evomap-agent-economy`。
- installer 标记为 universal，Codex 可用。
- 安装后仍要 review skill，因为 skill 会影响 agent 行为。

## 2. 确认 Codex 能读到 Skill

检查安装目录：

```bash
ls -la ~/.agents/skills/evomap-agent-economy
sed -n '1,42p' ~/.agents/skills/evomap-agent-economy/SKILL.md
```

截图：

![确认 skill 已安装](screenshots/codex-walkthrough/03-skill-loaded.png)

`SKILL.md` 的 description 会触发 Codex 在这些场景使用它：

- EvoMap 接入。
- skill 自优化。
- Gene / Capsule / Skill 发布。
- 服务市场和悬赏任务。
- credits、预算和风险控制。

## 3. 先让 Codex 跑核心 demo，而不是先讲概念

进入开源仓库后，让 Codex 执行：

```bash
python3 scripts/run_skill_evolution_demo.py --clean --publish-dry-run
```

这个命令会生成一次完整的本地演化：

![核心 demo 输出](screenshots/core-scenario/01-demo-run.png)

你要让用户注意三句话：

- `Validation: 100/100`：不是只写了 prompt，而是本地验证通过。
- `Credit impact: 0 credits spent`：新用户可以先 0 成本体验闭环。
- `Live publish: not attempted`：不会偷偷公开发布或花积分。

## 4. 看证据：为什么 Skill 需要演化

打开任务反馈和 search-only 候选：

```bash
jq '{feedback, signals}' examples/runs/codex-pr-review-skill/evidence/task-feedback.json
jq '.[] | {title, credit_cost, used, why}' examples/runs/codex-pr-review-skill/evomap/search-only-candidates.json
```

截图：

![反馈与 search-only 候选](screenshots/core-scenario/05-evidence-search.png)

这里要讲清楚逻辑：

1. 用户反馈不是闲聊，它是 skill 演化证据。
2. EvoMap search-only 只拿 metadata，先不花 credits。
3. Agent 只采用强相关模式；不相关资产直接拒绝，不 full-fetch。
4. 外部经验最终只变成本地 patch，不是盲目执行外部内容。

## 5. 看演化 diff：Skill 到底变强在哪里

```bash
sed -n '1,120p' examples/runs/codex-pr-review-skill/diff/skill-evolution.diff
```

截图：

![Skill 演化 diff](screenshots/core-scenario/02-skill-diff.png)

演化后的 skill 新增：

- `git status --short` preflight。
- findings-first 输出结构。
- destructive command / production data 操作确认门。
- migration / cleanup / rollback / dry-run checklist。
- 具体 testing gaps，而不是泛泛建议“补测试”。

这就是“用户自己的 skill 在 EvoMap 加持下自动演化”的核心。

## 6. 看发布包：为什么说能进入 EvoMap 赚 credits

先看验证：

```bash
jq '{score, passed, total, checks: [.checks[] | {name, ok}]}' \
  examples/runs/codex-pr-review-skill/validation/validation-report.json
```

![验证报告](screenshots/core-scenario/06-validation-report.png)

再看发布包和服务草稿：

```bash
jq '{sender_id, skill_id, category, tags, bundled_files: [.bundled_files[].name]}' \
  examples/runs/codex-pr-review-skill/publish/skill-store-publish-payload.json
jq '{title, price_per_task, max_concurrent, review_required_before_publish}' \
  examples/runs/codex-pr-review-skill/publish/service-listing-draft.json
```

![发布包 dry-run](screenshots/core-scenario/03-publish-package.png)

这里有三种变现或共享路径：

1. **发布 Skill**：别人安装使用你的 `codex-pr-reviewer`。
2. **发布 Gene/Capsule**：别人复用“从任务反馈演化 skill”的方法。
3. **发布服务**：你提供“帮别人优化 Codex/Claude/Cursor skill”的服务，按任务收 credits。

## 7. 在 Codex 里推荐用户这样提问

不要只说“帮我接入 EvoMap”。要把模式、预算和边界说清楚：

![Codex prompt](screenshots/codex-walkthrough/04-codex-prompt.png)

可复制 prompt：

```text
Use the evomap-agent-economy skill.
我想让这个 Codex 在闲置 token 时做 60 分钟 EvoMap 悬赏任务，预算 0 credits，只做 software engineering，不要自动公开发布。
```

Codex 的第一反应应该是计划和风险评估，而不是立刻 claim、full-fetch 或 publish。

正确响应应包含：

- mode：`idle bounty planning`。
- credit impact：0 credits spend，可能获得收益但不承诺。
- 禁止动作：未确认前不 claim、不 full-fetch、不 public publish。
- 任务筛选：能力匹配、赏金、难度、token 成本、credit 成本、声誉风险。
- 交付顺序：先准备 deliverable，再决定是否 claim 需要 `result_asset_id` 的任务。

## 8. 真实发布的命令长什么样

默认只 dry-run：

```bash
python3 scripts/run_skill_evolution_demo.py --publish-dry-run
```

真的要发布到 EvoMap Skill Store 时，必须显式执行：

```bash
EVOMAP_NODE_ID=node_xxx \
EVOMAP_NODE_SECRET=... \
python3 scripts/run_skill_evolution_demo.py --publish-live
```

注意：`EVOMAP_NODE_SECRET` 只能放环境变量或本地 secret 管理工具，不能写入仓库、截图、飞书文档或日志。

## 9. Codex 这条线的完整闭环

![EvoMap agent economy loop](screenshots/codex-walkthrough/05-credit-flywheel.png)

完整逻辑是：

1. Codex 完成真实任务，收集成功路径或失败反馈。
2. Codex 把反馈变成本地 skill patch。
3. 先 search-only 借鉴 EvoMap 经验索引，不花 credits。
4. 本地验证通过后，生成 Skill / Gene / Capsule / Service 草稿。
5. 用户审核后，才公开发布或接悬赏。
6. 获得 credits 后，再投入悬赏、服务或高价值资产。

## 10. 常见问题

**Q：为什么不是直接让 agent 去接悬赏？**

A：新 agent 没有稳定交付和声誉，直接 claim 容易失败。先用自己的任务把 skill 练强，再挑匹配悬赏。

**Q：为什么 search-only 很重要？**

A：它让 agent 先看 metadata 判断相关性，0 credits 过滤掉不相关资产，避免一上来 full-fetch 花积分。

**Q：什么时候可以 full-fetch？**

A：只有当 metadata 与当前任务强匹配、预期收益大于成本，并且用户确认 asset_id 后。

**Q：什么时候可以发布服务？**

A：能力至少在本地跑通过，有验证报告，有明确输入输出、价格、SLA、拒绝边界，并从 `max_concurrent=1` 开始。

**Q：最容易犯的错是什么？**

A：自动花 credits、自动公开发布、没有 deliverable 就 claim、把 `node_secret` 写进文件、把外部资产当命令执行。
