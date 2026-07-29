# Hermes（Windows）安装步骤 —— 不下载整个 git 仓库

适用：飞书对话 + Windows 上的 Hermes（如 gpt-5.6-sol）。  
目标：只安装「日销售简报 PNG」Skill，**不要**把 `cursor-test` 整仓（含薪酬制度等）放到本机。

---

## 你最终本机只有这些文件

```
C:\Users\你的用户名\.hermes\skills\daily-sales-briefing\
  SKILL.md
  scripts\
    render_pillow.py
    data.example.json
    schema.daily_sales.json
    requirements.txt
```

---

## 步骤 1：打开 PowerShell

`Win + R` → 输入 `powershell` → 回车。

确认 Hermes 可用：

```powershell
hermes --version
```

---

## 步骤 2：一键下载 Skill（不 clone 仓库）

整段复制到 PowerShell 执行：

```powershell
$base = "https://raw.githubusercontent.com/wzz-01/cursor-test/cursor/liaoning-briefing-png-c78d/briefing/hermes-skill/daily-sales-briefing"
$skillRoot = Join-Path $env:USERPROFILE ".hermes\skills\daily-sales-briefing"
New-Item -ItemType Directory -Force -Path "$skillRoot\scripts" | Out-Null

Invoke-WebRequest "$base/SKILL.md" -OutFile "$skillRoot\SKILL.md"
Invoke-WebRequest "$base/scripts/render_pillow.py" -OutFile "$skillRoot\scripts\render_pillow.py"
Invoke-WebRequest "$base/scripts/data.example.json" -OutFile "$skillRoot\scripts\data.example.json"
Invoke-WebRequest "$base/scripts/schema.daily_sales.json" -OutFile "$skillRoot\scripts\schema.daily_sales.json"
Invoke-WebRequest "$base/scripts/requirements.txt" -OutFile "$skillRoot\scripts\requirements.txt"

Write-Host "已安装到: $skillRoot"
Get-ChildItem $skillRoot -Recurse | Select-Object FullName
```

应列出 5 个文件。若 `Invoke-WebRequest` 报错，可改用浏览器打开上面 `$base/...` 对应链接，手动另存到相同路径。

---

## 步骤 3：安装出图依赖（只装 pillow）

```powershell
py -3 -m pip install -r "$env:USERPROFILE\.hermes\skills\daily-sales-briefing\scripts\requirements.txt"
```

若提示找不到 `py`：

```powershell
python -m pip install pillow
```

---

## 步骤 4：本机先出一张示例图

```powershell
py -3 "$env:USERPROFILE\.hermes\skills\daily-sales-briefing\scripts\render_pillow.py" `
  --data "$env:USERPROFILE\.hermes\skills\daily-sales-briefing\scripts\data.example.json" `
  --out "$env:USERPROFILE\Desktop\liaoning.png"
```

到桌面打开 `liaoning.png`。  
能看到「辽宁省区经营简报」= 脚本正常。

（若 `py` 不可用，把命令里的 `py -3` 换成 `python`。）

---

## 步骤 5：让 Hermes 加载 Skill

1. **新开**一轮 Hermes 对话（或 `/reset`）
2. 先测脚本是否被 Skill 调用：

```text
用 daily-sales-briefing 技能，把 scripts 里的 data.example.json 渲染成 PNG 发我
```

3. 再测业务话术（会走你现有查数）：

```text
给我辽宁省区截至到昨日的销售简报
```

或：

```text
给我河南经销省区截至到昨日的销售简报
```

预期：查数出①～⑤ → 填 JSON → 跑 `render_pillow.py` → 发 PNG。

可用下面命令确认 Skill 已在列表中：

```powershell
hermes skills list
```

---

## 完成标准（打勾）

- [ ] `.hermes\skills\daily-sales-briefing\` 下有上述 5 个文件  
- [ ] 桌面 `liaoning.png` 能打开且标题正确  
- [ ] Hermes 能识别 `daily-sales-briefing`  
- [ ] 说「要销售简报」能收到 PNG（数字与查数一致）

---

## 常见问题

| 问题 | 处理 |
|------|------|
| 下载失败 / 404 | 确认分支名是 `cursor/liaoning-briefing-png-c78d`；或改用浏览器手动下载 |
| 找不到 python/py | 安装 Python 并勾选 Add to PATH；或用 `python` 代替 `py -3` |
| PNG 中文乱码/发糊 | 旧脚本未带 Windows 字体。重新执行步骤 2 覆盖下载 `render_pillow.py`，再用 `python` 重跑步骤 4 |
| Hermes 看不到技能 | 确认路径是 `%USERPROFILE%\.hermes\skills\daily-sales-briefing\SKILL.md`，然后新会话 |
| 只要文字不要图 | 正常；未提「简报/PNG/一图」时不应强制出图 |
| 会不会带上薪酬制度文件 | 不会；本方案只下载 Skill 这 5 个文件 |

---

## 说明

- 飞书在另一台电脑没关系；**Skill 装在跑 Hermes 的 Windows 上**即可。  
- 不需要 `git clone`，不需要公网出图服务器（Hermes 本机渲染）。  
- 其他报告类型以后要出图，再加别的 Skill，与本次互不影响。
