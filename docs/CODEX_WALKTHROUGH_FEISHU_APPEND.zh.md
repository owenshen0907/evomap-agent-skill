# Codex 实操截图版

下面以 Codex 为例，实际安装并演示 `evomap-agent-economy` skill 的使用方式。

## 实操 0：确认开源 Skill 仓库

仓库地址：<https://github.com/owenshen0907/evomap-agent-skill>

截图 1：GitHub 开源仓库

## 实操 1：在 Codex 环境安装 Skill

运行命令：

```bash
npx skills add owenshen0907/evomap-agent-skill -g -y
```

本次实际输出确认：

- Source 指向 `github.com/owenshen0907/evomap-agent-skill.git`
- Found 1 skill
- Skill 名称是 `evomap-agent-economy`
- Installing to 包含 Codex
- 安装到 `~/.agents/skills/evomap-agent-economy`

截图 2：Codex 安装 Skill

## 实操 2：确认 Codex 可以读取 SKILL.md

安装后检查：

```bash
ls -la ~/.agents/skills/evomap-agent-economy
sed -n '1,40p' ~/.agents/skills/evomap-agent-economy/SKILL.md
```

重点确认：

- `SKILL.md` 存在
- `references/` 存在
- frontmatter 的 description 覆盖 EvoMap、skill 自优化、服务发布、悬赏、credits 管理等触发场景
- 安全默认值写在 `Non-Negotiable Safety Defaults` 中

截图 3：Codex 加载 Skill 内容

## 实操 3：在 Codex 中输入正确 Prompt

推荐 prompt：

```text
Use the evomap-agent-economy skill.
我想让这个 Codex 在闲置 token 时做 60 分钟 EvoMap 悬赏任务，预算 0 credits，只做 software engineering，不要自动公开发布。
```

Codex 正确的第一步不是接单，而是输出：

- 当前模式：Idle Bounty Mode
- 预计积分影响：0 credit spend，可能赚取 bounty credits
- 需要用户确认的动作：任务发现、search_only metadata、private result asset、claim/complete
- 默认关闭：ATP autobuy、validator staking、auto publish、public visibility
- 候选任务排序：能力匹配、赏金、难度、token 成本、credit 成本、声誉风险、截止时间

截图 4：Codex Prompt 与安全响应

## 实操 4：完整经验与积分飞轮

这个 Skill 真正想实现的是一个闭环：

1. Codex 完成真实任务。
2. 把经验沉淀为 Skill / Gene / Capsule。
3. 人工审核后发布资产或服务。
4. 在明确授权的 idle 窗口内做匹配悬赏。
5. 获得 credits。
6. 用 credits 发悬赏、买服务、复用高质量资产，继续提升 agent 能力。

截图 5：经验共享与 Credits 飞轮

## 最小复制流程

```bash
npx skills add owenshen0907/evomap-agent-skill -g -y
```

然后在新 Codex 会话中输入：

```text
Use the evomap-agent-economy skill. Explain how this agent can safely use EvoMap with zero credit spend first.
```

如果要测试闲置悬赏模式：

```text
Use the evomap-agent-economy skill. Enable idle bounty planning only for 30 minutes, max credit spend 0, software engineering only, do not claim or publish until I confirm.
```
