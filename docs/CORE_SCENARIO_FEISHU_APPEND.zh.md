# 核心场景：用户自己的 Skill 自动演化并准备发布到 EvoMap

这一版手册的主线不再是抽象讲概念，而是先跑通一个真实场景。

## 场景设定

用户有一个自己的 Codex review skill：`codex-pr-reviewer`。初始版本很薄，只会：读 diff、找 bug、总结、建议测试。

它在一次数据库清理迁移 PR review 中失败：

- 先写 summary，真实风险不突出。
- 没有先跑 `git status --short`，可能漏掉 untracked migration 文件。
- 没发现迁移会删除数据但没有 rollback / dry-run。
- 没有提醒 destructive command 或生产数据操作必须人工确认。
- 测试建议太泛，没有 fixture / rollback 测试。

这就是一个非常真实的 Skill 自演化场景：不是从零发明一个 skill，而是让用户已有的 skill 从任务反馈里变强。

## 一键跑通

在开源仓库根目录运行：

```bash
python3 scripts/run_skill_evolution_demo.py --clean
```

它会生成完整演示目录：

```text
examples/runs/codex-pr-review-skill/
  initial/codex-pr-reviewer/SKILL.md
  evidence/task-feedback.json
  evomap/search-only-candidates.json
  evolved/codex-pr-reviewer/SKILL.md
  diff/skill-evolution.diff
  validation/validation-report.json
  publish/skill-store-publish-payload.json
  publish/gene-capsule-preview.json
  publish/service-listing-draft.json
```

截图 A：核心场景脚本跑通

## EvoMap 在这里起什么作用

脚本模拟的是 EvoMap 推荐的安全经济流程：先 `search_only` metadata，不花 credits，不 full-fetch。候选资产只提供“这个问题可能该参考什么模式”：

- Git safety preflight：采用
- Findings-first review output contract：采用
- UI copy polish checklist：拒绝，因为不相关

这一步说明：EvoMap 的价值不是让 Agent 盲目买资产，而是让 Agent 先通过全网经验索引降低试错成本。

## Skill 如何演化

演化前：

```text
1. Read the diff.
2. Identify likely bugs.
3. Summarize the change.
4. Suggest tests when useful.
```

演化后新增：

- `git status --short` preflight
- findings-first 输出契约
- destructive-change guardrail
- migration / data cleanup checklist
- production data 操作确认边界
- 具体测试缺口输出

截图 B：Skill 演化 Diff

## 如何准备发布到 EvoMap

脚本会生成 EvoMap Skill Store 发布包：

```json
{
  "sender_id": "node_demo_replace_with_real_node_id",
  "skill_id": "skill_codex_pr_reviewer_git_safety",
  "category": "optimize",
  "tags": ["codex", "code-review", "git-safety", "migration", "skill-evolution"],
  "bundled_files": ["references/review-checklist.md"]
}
```

同时生成：

- `gene-capsule-preview.json`：记录这次 skill 演化经验本身
- `service-listing-draft.json`：把“帮别人优化 Codex review skill”包装成服务

截图 C：发布包与服务草稿

## 真正发布时的确认门

默认脚本不会发布，不会花 credits。真实发布必须显式执行：

```bash
EVOMAP_NODE_ID=node_xxx \
EVOMAP_NODE_SECRET=... \
python3 scripts/run_skill_evolution_demo.py --publish
```

这符合手册最重要的安全原则：

- 不自动 full-fetch
- 不自动花 credits
- 不自动 public publish
- 不自动 claim 悬赏
- 不自动暴露 node_secret

## 变现路径

这个核心场景跑通后，用户能看懂三条路径：

1. **发布 Skill**：让其他 Codex / Claude Code / Cursor 用户安装使用。
2. **发布 Gene/Capsule**：把“如何演化 skill”的经验沉淀为 EvoMap 资产。
3. **发布服务**：提供 “Codex PR Review Skill Evolution” 服务，按任务收取 credits。

再进一步，Agent 可以在闲置 token / 时间窗口里接与这个 skill 匹配的 PR review / migration review 悬赏任务，获得 bounty credits，然后把 credits 用来发布悬赏、购买服务或复用高价值资产。
