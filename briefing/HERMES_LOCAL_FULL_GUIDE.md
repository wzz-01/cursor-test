# Hermes 本机完整改造方案（WSL）

适用环境：Windows 上的 **WSL Ubuntu** 跑 Hermes（profile：`default` / `synear-report` / `syneardata`），飞书只是对话入口。

目标：智能体能输出「销售经营晨报」PNG，且版式/字体满足：

- 标题「销售经营晨报」、右上角时间模块、聚焦语 → **楷体加粗加大**
- 其余文字 → **微软雅黑**
- 模块 01：整体 / 基量 四指标网格
- 模块 02：经销组业绩进度表（达成率进度条、低于 90% 标红）

---

## 0. 打开正确的终端

必须打开 **WSL Ubuntu**（提示符类似 `data1@DATA:~$`），不要用 Windows PowerShell 装 Skill。

```bash
# 确认在 Linux 里
uname -a
echo $HOME
# 应类似：/home/data1
```

---

## 1. 安装出图 Skill（不 clone 整个仓库）

```bash
BASE="https://raw.githubusercontent.com/wzz-01/cursor-test/cursor/liaoning-briefing-png-c78d/briefing/hermes-skill/daily-sales-briefing"

install_skill() {
  local root="$1"
  mkdir -p "$root/scripts/fonts"
  curl -fsSL "$BASE/SKILL.md" -o "$root/SKILL.md"
  curl -fsSL "$BASE/scripts/render_pillow.py" -o "$root/scripts/render_pillow.py"
  curl -fsSL "$BASE/scripts/data.example.json" -o "$root/scripts/data.example.json"
  curl -fsSL "$BASE/scripts/data.mock.json" -o "$root/scripts/data.mock.json"
  curl -fsSL "$BASE/scripts/schema.daily_sales.json" -o "$root/scripts/schema.daily_sales.json"
  curl -fsSL "$BASE/scripts/requirements.txt" -o "$root/scripts/requirements.txt"
  echo "OK: $root"
}

install_skill "$HOME/.hermes/skills/daily-sales-briefing"
install_skill "$HOME/.hermes/profiles/default/skills/daily-sales-briefing"
install_skill "$HOME/.hermes/profiles/synear-report/skills/daily-sales-briefing"
install_skill "$HOME/.hermes/profiles/syneardata/skills/daily-sales-briefing"
```

检查：

```bash
ls -la ~/.hermes/skills/daily-sales-briefing/scripts/
```

---

## 2. 准备 Python（不要 sudo apt）

Ubuntu 24 禁止直接 `pip install` 到系统，用虚拟环境：

```bash
python3 -m venv ~/.venvs/briefing
~/.venvs/briefing/bin/pip install "pillow>=10.0.0"
```

固定使用这个解释器：

```text
/home/data1/.venvs/briefing/bin/python
```

（若用户名不是 `data1`，把路径里的用户名换成你的。）

---

## 3. 字体准备（关键）

### 3.1 优先用 Windows 楷体 + 雅黑

```bash
ls /mnt/c/Windows/Fonts/simkai.ttf \
   /mnt/c/Windows/Fonts/STKAITI.TTF \
   /mnt/c/Windows/Fonts/msyh.ttc \
   /mnt/c/Windows/Fonts/msyhbd.ttc
```

- `simkai.ttf` / `STKAITI.TTF`：楷体（标题/时间/聚焦语）
- `msyh.ttc` / `msyhbd.ttc`：微软雅黑（其余文字）

### 3.2 若没有系统楷体

脚本会**自动下载**开源「霞鹜文楷 Bold」到：

```text
~/.hermes/skills/daily-sales-briefing/scripts/fonts/LXGWWenKai-Bold.ttf
```

也可手动下载：

```bash
mkdir -p ~/.hermes/skills/daily-sales-briefing/scripts/fonts
curl -fL "https://cdn.jsdelivr.net/gh/lxgw/LxgwWenKai@v1.330/fonts/TTF/LXGWWenKai-Bold.ttf" \
  -o ~/.hermes/skills/daily-sales-briefing/scripts/fonts/LXGWWenKai-Bold.ttf
```

并把该字体同步到各 profile：

```bash
for p in default synear-report syneardata; do
  mkdir -p ~/.hermes/profiles/$p/skills/daily-sales-briefing/scripts/fonts
  cp ~/.hermes/skills/daily-sales-briefing/scripts/fonts/LXGWWenKai-Bold.ttf \
     ~/.hermes/profiles/$p/skills/daily-sales-briefing/scripts/fonts/
done
```

---

## 4. 本机先出一张模拟图（验证版式+字体）

```bash
~/.venvs/briefing/bin/python ~/.hermes/skills/daily-sales-briefing/scripts/render_pillow.py \
  --data ~/.hermes/skills/daily-sales-briefing/scripts/data.mock.json \
  --out ~/template-preview.png
```

终端必须出现类似：

```text
[font] 楷体已加载: /mnt/c/Windows/Fonts/simkai.ttf @ 44px
```

或：

```text
[font] 楷体已加载: .../LXGWWenKai-Bold.ttf @ 44px
```

Windows 资源管理器打开：

```text
\\wsl$\Ubuntu\home\data1\template-preview.png
```

应看到：

1. 顶栏标题 / 时间徽章 / 聚焦语为楷体风格且更大  
2. 01 业绩追踪：整体/基量四格  
3. 02 表格：濮鹤、安阳、焦济、新乡四行（模拟数据）

---

## 5. 同步到所有 Hermes profile（避免智能体找不到）

```bash
SRC=~/.hermes/skills/daily-sales-briefing
for p in default synear-report syneardata; do
  DEST=~/.hermes/profiles/$p/skills/daily-sales-briefing
  mkdir -p "$DEST/scripts/fonts"
  cp -f "$SRC/SKILL.md" "$DEST/"
  cp -f "$SRC/scripts/"*.py "$DEST/scripts/" 2>/dev/null || true
  cp -f "$SRC/scripts/"*.json "$DEST/scripts/"
  cp -f "$SRC/scripts/"*.txt "$DEST/scripts/" 2>/dev/null || true
  cp -f "$SRC/scripts/fonts/"* "$DEST/scripts/fonts/" 2>/dev/null || true
  echo "synced $DEST"
done
```

---

## 6. 告诉 Hermes 固定路径（新开对话）

把下面整段发给智能体：

```text
请固定使用日销售简报技能：

技能目录：/home/data1/.hermes/skills/daily-sales-briefing
（已同步到 profiles: default / synear-report / syneardata）

出图 Python：
/home/data1/.venvs/briefing/bin/python

示例命令：
/home/data1/.venvs/briefing/bin/python /home/data1/.hermes/skills/daily-sales-briefing/scripts/render_pillow.py --data /home/data1/.hermes/skills/daily-sales-briefing/scripts/data.mock.json --out /home/data1/template-preview.png

规则：
1) 用户要「简报/晨报/PNG」时：查数 → 填 JSON → 用上面命令出 PNG → 发图
2) 标题/时间模块/聚焦语用楷体；其余微软雅黑
3) performance=整体/基量指标；section_01.rows=经销组表格
4) 缺数填 "—"，禁止编造
```

先测：

```text
用 daily-sales-briefing，把 data.mock.json 渲染成 PNG 发我
```

再测业务：

```text
给我河南经销省区截至到昨日的销售简报
```

---

## 7. JSON 填数结构（智能体必须按这个）

### 7.1 顶栏

```json
"meta": {
  "brand_title": "销售经营晨报",
  "scope": "省区经营管理",
  "region": "河南经销省区",
  "as_of_date": "2026-07-24",
  "data_cutoff": "07:30",
  "report_time": "08:00",
  "generated_at": "2026-07-24 08:00",
  "owner": "河南经销省区销售管理"
},
"focus": "聚焦预算进度、客户下单与一线执行"
```

### 7.2 模块 01 业绩追踪

```json
"performance": {
  "overall": {
    "budget": "1280万",
    "sales": "1185万",
    "achieve_rate": "92.6%",
    "growth_rate": "+8.3%"
  },
  "base": {
    "budget": "860万",
    "sales": "792万",
    "achieve_rate": "92.1%",
    "growth_rate": "+5.6%"
  }
}
```

### 7.3 模块 02 经销组表格

```json
"section_01": {
  "title": "分区 / 销售组业绩进度",
  "warn_below": 90,
  "rows": [
    {
      "name": "濮鹤经销组",
      "achieve_rate": 117.0,
      "growth_rate": 34.5,
      "base_achieve_rate": 123.6,
      "order_amount_5d": "43万元"
    }
  ]
}
```

达成率 &lt; `warn_below`（默认 90）整行标红。

---

## 8. 以后改版式 / 改字体，本机怎么改

| 改什么 | 改哪个文件 |
|--------|------------|
| 排版、模块、颜色、字号 | `~/.hermes/skills/daily-sales-briefing/scripts/render_pillow.py` |
| 模拟预览数据 | `.../scripts/data.mock.json` |
| 教智能体如何填 JSON | `~/.hermes/skills/daily-sales-briefing/SKILL.md` |

改完后：

1. 本机 `python ... render_pillow.py --data data.mock.json --out ~/test.png` 看效果  
2. 执行第 5 步同步到三个 profile  
3. **新开** Hermes 对话再测  

从 GitHub 拉最新脚本（推荐）：

```bash
BASE="https://raw.githubusercontent.com/wzz-01/cursor-test/cursor/liaoning-briefing-png-c78d/briefing/hermes-skill/daily-sales-briefing"
curl -fsSL "$BASE/scripts/render_pillow.py" -o ~/.hermes/skills/daily-sales-briefing/scripts/render_pillow.py
curl -fsSL "$BASE/SKILL.md" -o ~/.hermes/skills/daily-sales-briefing/SKILL.md
# 然后重复第 5 步同步
```

---

## 9. 验收清单

- [ ] Skill 存在于 `~/.hermes/skills/` 和三个 profile  
- [ ] `~/.venvs/briefing/bin/python` 可运行 Pillow  
- [ ] 出图日志出现 `[font] 楷体已加载: ...`  
- [ ] 预览图：楷体标题/时间/聚焦语；雅黑正文  
- [ ] 01 网格、02 表格（含你的四组数据模拟）正常  
- [ ] Hermes 对话能发回 PNG  
- [ ] 「只要数字、不要简报」时仍只回文字  

---

## 10. 常见问题

| 现象 | 处理 |
|------|------|
| 智能体说找不到 skill | 做第 5 步同步；新开对话；把绝对路径发给它 |
| 标题不像楷体 | 看日志字体路径；优先保证有 `simkai.ttf` |
| `externally-managed-environment` | 用 venv，不要系统 pip |
| `sudo` 密码错误 | 不要 apt；本方案全程可不 sudo |
| 装到 `C:\Users\...\.hermes` | 错了；Hermes 在 WSL，必须装到 `/home/.../.hermes` |
| 数字被编造 | 强调 SKILL：缺数用 `"—"` |

---

## 一句话流程

```text
WSL 装 Skill → venv 装 Pillow → 确认楷体/雅黑 → mock 出图验证
→ 同步三个 profile → 告诉 Hermes 路径与 Python
→ 对话要简报 → 查数填 JSON → 渲染 PNG → 发图
```
