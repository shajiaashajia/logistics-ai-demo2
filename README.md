# logistics-ai-demo2

AI调度演示系统（煤炭 + 指派调度 + 保交付优先）。

## 功能说明

- 订单维度：煤矿、目的地、电厂保供优先级、交付截止时间、吨位。
- 车辆维度：位置、载重能力、可用时间。
- 调度目标：优先保障高优先级订单按时交付；迟到会有较大惩罚。
- 调度策略：按 `priority desc + deadline asc` 排序后，逐单选择最优车辆执行指派。

## 运行演示

```bash
python scheduler_demo.py
```

## 运行测试

```bash
pytest -q
```
