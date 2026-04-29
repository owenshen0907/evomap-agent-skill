# 代码场景：从测试失败到代码修复，再到可复用经验

这个场景专门演示“code 里的进化路径”，不是只改文档或 skill。它把一段真实会失败的代码跑起来，然后走完：测试失败 -> 证据沉淀 -> search_only 候选经验 -> 代码修复 -> 测试通过 -> 生成本地 skill -> 准备 Gene/Capsule 和服务草稿。

## 一键跑通

```bash
python3 scripts/run_code_evolution_demo.py --clean
```

预期输出：

```text
EvoMap code evolution demo complete
- Initial tests passed: False (expected false)
- Fixed tests passed: True
- Validation: 100/100
- Credit impact: 0 credits spent, 0 paid full-fetches, no live publish
```

## 生成文件

```text
examples/runs/checkout-discount-code-evolution/
  initial/checkout_pricing/pricing.py
  initial/checkout_pricing/test_pricing.py
  evidence/initial-test-output.txt
  evidence/task-feedback.json
  evomap/search-only-candidates.json
  evolved/checkout_pricing/pricing.py
  evolved/checkout_pricing/test_pricing.py
  evolved/skills/payment-edge-case-reviewer/SKILL.md
  diff/code-evolution.diff
  validation/fixed-test-output.txt
  validation/validation-report.json
  evolver/evolution-event.json
  publish/gene-capsule-preview.json
  publish/skill-store-publish-payload.json
  publish/service-listing-draft.json
```

## 场景说明

初始代码是一个 checkout coupon 函数：

```python
def price_after_coupon_cents(subtotal_cents: int, coupon_percent: int) -> int:
    discount = int(subtotal_cents * coupon_percent / 100)
    return subtotal_cents - discount
```

它有 4 类真实问题：

- `333` cents 打 15% 折扣时，49.95 cents 被向下截断为 49，用户多付 1 cent。
- `125%` coupon 会产生负数总价。
- 负数 coupon 没有被拒绝。
- 负数 subtotal 没有被拒绝。

测试失败输出保存在：

```text
examples/runs/checkout-discount-code-evolution/evidence/initial-test-output.txt
```

## Evolver 风格的演化路径

1. **失败成为证据**：unittest 输出、用户可见失败、触发信号写入 `evidence/`。
2. **先 search_only**：只看 metadata，不 full-fetch，不花 credits。
3. **采用强相关经验**：money calculation guardrails、user-entered numeric validation。
4. **拒绝不相关经验**：CSS hover checklist 信号不匹配，不 fetch。
5. **修复代码**：使用 `Decimal` + `ROUND_HALF_UP`，校验负数，限制 over-100% coupon。
6. **重新验证**：同一组测试全部通过。
7. **沉淀经验**：生成 `payment-edge-case-reviewer` 本地 skill。
8. **准备发布**：生成 Gene/Capsule、Skill Store payload、service listing draft，但不 live publish。

## 代码 diff 看什么

```bash
sed -n '1,180p' examples/runs/checkout-discount-code-evolution/diff/code-evolution.diff
```

重点不是“修了一个 bug”，而是把代码修复变成了可复用能力：

- 明确金额计算使用 Decimal 和 ROUND_HALF_UP。
- 明确负数输入必须拒绝。
- 明确 over-100% coupon 不能产生负数总价。
- 明确边界测试要覆盖 0%、100%、over-100%、负数、半分 rounding。
- 新增本地 skill：`payment-edge-case-reviewer`。

## 验证项

```bash
cat examples/runs/checkout-discount-code-evolution/validation/validation-report.json
```

验证内容包括：

- 初始测试确实失败，说明问题可复现。
- 修复后测试通过。
- rounding 行为显式。
- over-100% coupon 被限制。
- 负数输入被拒绝。
- 经验被沉淀成本地 skill。
- 候选经验是 search_only，0 credits。
- 没有明显 secret pattern。

## 这条路为什么重要

这才是 code 场景里的“进化”：

```text
一次 bug 修复
  -> 失败输出成为证据
  -> Evolver / EvoMap 借鉴候选经验但不花积分
  -> 代码修复并通过测试
  -> 修复经验沉淀为本地 skill
  -> 形成 Gene/Capsule 和服务草稿
  -> 人工确认后才考虑发布、接单或赚 credits
```

也就是说，EvoMap/Evolver 不只是“帮你修一次 bug”，而是把这次 bug 修复变成下次 agent 能主动复用的能力。
