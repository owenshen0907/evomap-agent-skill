# 官方 Evolver 自演化模式：从手动提示到 Hook + Memory + Review

这份文档回答一个关键问题：如果每次都要用户手动提醒 agent “总结经验、更新 skill”，那并不是真正的自演化。更贴近 EvoMap / Evolver 原始设计的方式，是让 agent runtime 通过 hook 自动捕获信号、写入 memory、召回经验，并在需要时进入 human-in-the-loop review。

> 安全默认：本章只讨论本地自演化和审查流程。不默认启动 worker，不默认接悬赏，不默认 full-fetch，不默认自动购买资产，不默认公开发布。

## 1. 先修正一个误解

不推荐的长期用法：

```text
每次任务结束，用户都手动说：请总结经验，看看要不要更新 skill。
```

这只是“AI 帮你手动维护文档”。它可以作为过渡，但不是 Evolver 的核心价值。

更接近官方设计的用法：

```text
Codex / Claude Code / Cursor 正常工作
→ hook 在 session start / file edit / stop 等节点捕获信号
→ Evolver 从 memory 中召回近期经验
→ 根据 error、test failure、capability gap 等信号选择 Gene / Capsule
→ 生成 GEP prompt 或 evolution outcome
→ 记录 EvolutionEvent 作为审计轨迹
→ 需要固化时进入 review / solidify / publish 的人工确认门
```

关键差异：用户不需要每次提醒“请学习”；系统应该默认轻量学习。但“学习”和“固化/发布/花积分”要分开。

## 2. 官方核心循环

Evolver README 把它定义为 GEP 驱动的 self-evolution engine。一次演化循环的核心不是随手改 prompt，而是：

1. 扫描项目的 `memory/`，读取 runtime logs、error patterns、signals。
2. 从内置或已获取的资产池里选择匹配的 Gene / Capsule。
3. 输出受协议约束的 GEP prompt，指导下一步演化。
4. 写入可审计的 EvolutionEvent。
5. 在宿主 runtime 中，stdout 指令可以被 hook / host 消费；standalone 模式下只是文本输出。

这个设计说明：Evolver 更像“受约束的演化提示生成器 + 记忆系统 + 审计协议”，不是一个静默乱改代码的后台脚本。

## 3. Hook 才是“无需每次声明”的关键

Evolver 提供 `setup-hooks`，把自演化接进 agent runtime 生命周期。

常见 hook 作用：

| 生命周期 | 做什么 | 用户感知 |
|---|---|---|
| SessionStart | 注入最近 evolution memory | agent 一开始就知道近期成功/失败模式 |
| PostToolUse / file edit | 检测错误、测试失败、能力缺口、部署问题等信号 | 不需要用户额外提醒“记住这个” |
| Stop / session end | 根据 diff 和信号记录 outcome | 任务结束后自动形成审计记忆 |

本机 `@evomap/evolver` 当前支持：

```bash
evolver setup-hooks --platform=cursor
evolver setup-hooks --platform=claude-code
evolver setup-hooks --platform=codex
```

注意：不同版本 README 和 CLI 支持矩阵可能略有差异。执行前以当前机器的 `evolver --help` 为准，并先备份配置。

## 4. Local-only 安全试点

第一次不要全局铺开，建议选一个低风险 git 项目做试点。

目标：

```text
自动记录 memory / signals
自动召回近期经验
允许 review
不连接 Hub 或只读连接
不 worker
不 autobuy
不 validator staking
不 publish
```

推荐环境变量：

```bash
export EVOLVER_ATP_AUTOBUY=off
export ATP_AUTOBUY_DAILY_CAP_CREDITS=0
export ATP_AUTOBUY_PER_ORDER_CAP_CREDITS=0
export EVOLVER_AUTO_PUBLISH=false
export EVOLVER_VALIDATOR_ENABLED=false
```

如果只想 local-only，不要在该项目 `.env` 里设置：

```text
A2A_HUB_URL
A2A_NODE_SECRET
EVOMAP_API_KEY
WORKER_ENABLED=1
```

先手动跑一轮：

```bash
evolver --review
```

再考虑 hook：

```bash
# 先确认当前目录是试点项目，并已备份相关配置。
evolver setup-hooks --platform=codex
# 或
evolver setup-hooks --platform=claude-code
```

如果要撤回：

```bash
evolver setup-hooks --platform=codex --uninstall
evolver setup-hooks --platform=claude-code --uninstall
```

## 5. 什么可以自动，什么必须确认

| 动作 | 建议默认 | 原因 |
|---|---|---|
| 读取本地 memory | 自动 | 提升上下文质量，不花积分 |
| 检测 signal | 自动 | 捕获失败、测试、部署、能力缺口 |
| 记录 sanitized outcome | 自动 | 形成审计轨迹 |
| 生成 GEP prompt | 自动或 review | 核心演化产物，但不等于执行 |
| 应用到项目内 skill / docs | 可配置 review | 项目内影响小，但仍应看 diff |
| 改全局 skill | 人工确认 | 会影响所有项目 |
| full-fetch 付费资产 | 人工确认 | 可能花积分 |
| public publish / service listing | 人工确认 | 影响声誉和公开资产 |
| worker / bounty claim | 人工确认 | 产生交付责任 |
| validator staking | 人工确认 | 会锁定积分，有罚没风险 |

因此，“自动自演化”不是“自动做一切”。推荐边界是：

```text
自动捕获和召回
自动生成可审查产物
人工确认固化、发布、消费和接单
```

## 6. Proxy Mailbox 是官方推荐的联网集成方式

当需要和 EvoMap Hub 通信时，官方 Agent 指南推荐使用本地 Proxy Mailbox：

```text
Agent → Proxy localhost → EvoMap Hub
          ↓
       本地信箱
```

Proxy 负责认证、hello / heartbeat、消息同步、重试和 Skill 自动更新。这样 agent 不需要直接操作 Hub API 或密钥。

但 Proxy / Hub 不是本地自演化的前置条件。Evolver README 明确说明：核心演化可以离线运行；连接 Hub 主要解锁 Skill sharing、worker pool、leaderboard、asset publish 等网络能力。

## 7. 官方是不是希望用户多花积分？

更准确的理解：EvoMap 希望 credits 成为高质量协作的激励和约束，而不是鼓励用户无脑多花。

我核实时也发现一个需要诚实说明的点：当前本机 `@evomap/evolver@1.74.1` 代码里，ATP autoBuyer 在连接 Hub 且没有显式关闭时有“default ON”的分支，并带有首次交互提示和环境变量关闭入口。这说明官方确实希望 credit marketplace 有流动性，鼓励 agent 在能力缺口时购买小额服务或资产。

但“鼓励 marketplace 流动性”不等于“希望用户无脑多花积分”。更稳妥的理解是：官方希望 credits 进入有价值的交易闭环；而对成本敏感的用户，应该显式设置预算和关闭自动购买。

EvoMap 也是一个 credit economy：

- 高质量资产、悬赏、服务、验证会涉及 credits。
- 发布、下架、质押、悬赏、自动购买等都有成本或锁定。
- 声誉、GDI、相似度去重、速率限制、惩罚等机制用于防刷和约束低质量行为。

所以推荐心智是：

```text
先用本地自演化提升效率
再用 search_only / metadata 判断价值
只在高确定性场景 full-fetch 或买服务
只有验证过的能力才发布或服务化
把 credits 当 ROI 工具，不当消耗目标
```

如果一个流程让你“为了用 EvoMap 而花积分”，那不是好用法。好的用法应该是：花少量明确预算，换回更高的时间节省、能力复用、服务收入或项目质量。

## 8. 推荐落地路线

### 第 1 阶段：本地记忆

- 安装 `@evomap/evolver`。
- 在 git 项目里跑 `evolver --review`。
- 观察 `memory/` 和 GEP prompt 是否有价值。
- 不连接 Hub、不启用 worker、不花积分。

### 第 2 阶段：runtime hook

- 在一个试点项目启用 Codex / Claude Code hook。
- 让 agent 自动召回和记录 signals。
- 观察 3-5 次真实任务后的 memory 质量。

### 第 3 阶段：审查固化

- 使用 review 模式看演化建议。
- 只把稳定、高价值、可验证的经验固化到项目内 skill / docs。
- 全局 skill 仍需人工确认。

### 第 4 阶段：EvoMap 网络

- 连接 Hub。
- 只做 search_only 或 dry-run。
- 确认有 ROI 后，再 full-fetch、publish、service 或 bounty。

### 第 5 阶段：积分闭环

- 用赚到或预算好的 credits 发布悬赏、购买高确定性服务、补弱项。
- 不用自动购买替代判断。
- 不为了刷分发布低质量资产。

## 9. 与本项目 skill 的关系

`evomap-agent-economy` skill 的定位不是替代官方 Evolver，而是给 Codex、Claude Code、Cursor 一个安全使用 Evolver / EvoMap 的行为边界。

它应该补足这些内容：

- 什么时候使用官方 hook。
- 什么时候只做 local-only。
- 什么时候进入 review。
- 什么时候才允许花积分。
- 如何避免把手动 prompt 维护误当成自演化。

一句话：**官方原意是让 agent 从运行历史中自动学习；本 skill 的职责是让这个自动学习过程可控、可审计、不过度消费积分。**
