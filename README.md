# cursor-test

## 经营简报 PNG（多省区）

飞书智能体查数后，按统一晨报模板输出任意省区的日销售 PNG 简报。

- 逐步操作：[`briefing/STEP_BY_STEP.md`](briefing/STEP_BY_STEP.md)
- 接入说明：[`briefing/MULTI_REGION.md`](briefing/MULTI_REGION.md)
- 快速开始：[`briefing/README.md`](briefing/README.md)

```bash
python3 briefing/render_pillow.py \
  --data briefing/data.example.json \
  --out briefing/output/liaoning-2026-07-27.png
```
