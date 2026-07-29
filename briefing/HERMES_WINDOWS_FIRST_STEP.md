# Hermes（Windows）——你的第一步怎么做

你的环境是：

- 对话/模型在 **Hermes**（Windows 电脑）
- 模型可能是 **gpt-5.6-sol**
- 飞书是消息入口（另一台电脑也可以，但 **Skill 要装在跑 Hermes 的那台 Windows 上**）

所以：**第一步不是改飞书网页，而是在跑 Hermes 的 Windows 上安装「日销售简报」Skill。**

---

## 第一步（只做这件事）

### 1. 打开跑 Hermes 的那台 Windows

按 `Win + R`，输入 `powershell`，回车。

### 2. 确认 Hermes 能用

```powershell
hermes --version
```

能输出版本号再继续。若提示找不到命令：重开一个 PowerShell，或确认 Hermes 已安装。

### 3. 创建 Skill 目录并拷贝文件

在 PowerShell 里执行（整段复制）：

```powershell
$skillRoot = Join-Path $env:USERPROFILE ".hermes\skills\daily-sales-briefing"
New-Item -ItemType Directory -Force -Path "$skillRoot\scripts" | Out-Null

# 下面把仓库路径改成你本机实际位置
$repo = "D:\cursor-test"   # ← 改成你 clone 的目录

Copy-Item "$repo\briefing\hermes-skill\daily-sales-briefing\SKILL.md" $skillRoot -Force
Copy-Item "$repo\briefing\hermes-skill\daily-sales-briefing\scripts\*" "$skillRoot\scripts\" -Force

dir $skillRoot
dir $skillRoot\scripts
```

你应看到：

- `SKILL.md`
- `scripts\render_pillow.py`
- `scripts\data.example.json`
- `scripts\requirements.txt`

> 若还没有仓库，先：
>
> ```powershell
> cd D:\
> git clone https://github.com/wzz-01/cursor-test.git
> cd cursor-test
> git checkout cursor/liaoning-briefing-png-c78d
> ```
>
> 然后再跑上面的拷贝命令（`$repo = "D:\cursor-test"`）。

### 4. 安装 Pillow（出图依赖，做一次）

```powershell
py -3 -m pip install -r "$env:USERPROFILE\.hermes\skills\daily-sales-briefing\scripts\requirements.txt"
```

若 `py` 不可用，试：

```powershell
python -m pip install pillow
```

### 5. 本机先出一张图（验证 Skill 脚本）

```powershell
py -3 "$env:USERPROFILE\.hermes\skills\daily-sales-briefing\scripts\render_pillow.py" `
  --data "$env:USERPROFILE\.hermes\skills\daily-sales-briefing\scripts\data.example.json" `
  --out "$env:USERPROFILE\Desktop\liaoning.png"
```

去桌面打开 `liaoning.png`。能看到「辽宁省区经营简报」= 第一步的脚本侧 OK。

### 6. 让 Hermes 重新加载 Skill

新开一轮 Hermes 对话（或按你平时的 `/reset`），然后直接说：

```text
用 daily-sales-briefing 技能，把示例 data.example.json 渲染成 PNG 发我
```

或直接业务话术：

```text
给我辽宁省区截至到昨日的销售简报
```

（此时 Hermes 应：查数 → 填 JSON → 跑 `render_pillow.py` → 发图）

---

## 第一步完成的标准

- [ ] `%USERPROFILE%\.hermes\skills\daily-sales-briefing\` 目录存在  
- [ ] 桌面能打开 `liaoning.png`  
- [ ] Hermes 对话里能识别并使用 `daily-sales-briefing`

---

## 第一步之后再做什么（先不用管）

| 顺序 | 做什么 |
|------|--------|
| 第二步 | 确认 Hermes 仍能查你的①～⑤销售结论 |
| 第三步 | 对话里测河南/辽宁「要销售简报」是否出 PNG |
| 第四步 | 若经飞书收消息：确认飞书桥接能发图片 |

---

## 常见问题

**Q：飞书在另一台电脑，Skill 装哪？**  
装在 **跑 Hermes 的那台 Windows**。飞书只是聊天窗口。

**Q：我用的是 gpt-5.6-sol，要换模型吗？**  
不用。Skill 不绑定模型；模型负责查数和填 JSON，脚本负责画 PNG。

**Q：拷贝后 Hermes 看不到技能？**  
确认路径是 `C:\Users\你的用户名\.hermes\skills\daily-sales-briefing\SKILL.md`，然后新开会话。  
也可用：`hermes skills list` 看是否出现 `daily-sales-briefing`。
