# 考研数学 66000 · 逐题精解

冯建轩《考研数学 66000》全书逐题的**可编辑 HTML 解析站点**。每题一张卡片，六块内容：
题干 / 答案 / 完整推导 / 易错点 / 考向分析 / 变式训练。

**在线站点**：https://zrx-11.github.io/kaoyan-math-66000/

---

## 现状

| 项 | 值 |
|---|---|
| 在线卡片 | 2850 张 |
| 已启动 | 第一册《高等数学习题集 15000》专题 01《极限》2650 题；第二册专题《n 项和极限》200 题 |
| 分册总数 | 16 册，其余 14 册待启动 |
| 闸门 | `python3 work/gate.py` → `cards=2850 failed=0` |
| 书答错误率 | 全册 18.2%（带校勘块口径）；后半册 1201–2850 为 20.4% |

---

## 目录

```
index.html / progress.html / knowledge/     # 站点页面（生成物）
volumes/                                    # 各册各专题分页（生成物）
data.json                                   # 站点索引（生成物）
assets/site.css                             # 全站样式（唯一手改的站点文件）

work/                                       # ★ 工作台：源文件、页面图、台账、工具、规范
├── AGENT-HANDBOOK.md                       # ★★ 接手从这里开始
├── README.md                               # 工作台导航
├── spec/                                   # 规范：PIPELINE / QC / CARD-FORMAT / LEDGER / VERIFY
├── fragments/02-gaoshu-15000/{t01,t02}/    # 题卡源文件（站点内容真源）
├── pages/{jixian,nxh}/                     # 页面图（题干唯一来源）
├── checks.csv                              # 台账
├── manifest/                               # 题号↔页码
├── content/                                # 讲解页与知识树数据
├── templates/gold-1-6.html                 # 金标准样板
└── *.py, publish.sh                        # 工具
```

**改内容**：编辑 `work/fragments/.../*.html`，再 `python3 work/build_site.py`。
**改样式**：`assets/site.css`。
**别手改** `volumes/`、`data.json`、`knowledge/` —— 下次构建会覆盖。

---

## 接手（给 agent 或人）

完整流程写在 **[`work/AGENT-HANDBOOK.md`](work/AGENT-HANDBOOK.md)**，包含：
现状快照、十条硬口径、命令速查、推进一段的九步、新开一册从 PDF 到上线、
15 类复发错误族、五起真实事故与修复、待办优先级。

最短路径：

```bash
python3 work/gate.py                      # 体检：cards=2850 failed=0
python3 work/qa/ledger_audit.py           # 账实审计：查 fixed⇔caveat 三类告警
python3 work/qa/range_map.py 1401 1500    # 题号 → 承载文件（派活前必跑）
python3 work/qa/find_orphans.py           # 扫 article 外的游离 <p>
python3 work/qa/plainlen.py <文件> 起 止  # 篇幅与公式三维（唯一字数口径）
python3 work/build_site.py                # 建站
bash    work/publish.sh                   # 发布（必须 bash）
```

### 三条必须守住的口径

1. **题干只认页面图**（150 dpi 灰度 PNG）。PDF 文本层会丢 π、∞、∫、∈，完全不可用。
2. **答案栏是唯一答案出口**。原书给错 → 写复算值 + 紧跟一个 `class="block caveat"` 校勘块。
3. **`fixed ⇔ caveat` 双向成立；`skip` 只表示题面不可用，且不许带校勘块。**

### 现在最有价值的下一步

- 清 105 张账实不符（`ledger_audit.py` 直接列出）：64 张「记 fixed 却无块」、41 张「带块却记 pass」。
- 清 117 张重复卡（5 段真副本：q4–6、q254–264、q501–530、q1338–1360、q1901–1950）。
- 14 册生产未启动（约 6.3 万题），需按额度排期，别自行大规模开工。

---

## 技术说明

- 纯静态 HTML，无构建框架；公式由 MathJax 3（CDN）渲染。
- **路径自适应**：所有脚本的项目根从 `__file__` 推导；站点目录若 `ROOT/kaoyan66000/` 不存在则
  取 `ROOT` 本身。因此同一套脚本既能在「站点在子目录」的开发布局跑，也能在本仓库直接跑。
- `publish.sh` 只推 `origin main`，不含任何凭据；需要你自己的远端与 token。
- GitHub Pages 通过 `.nojekyll` 关闭 Jekyll 处理。

---

## 版权

题干与答案为原书的引用，用于个人学习与研究；解析、易错点、考向与变式为二次创作的原创内容。
如涉版权问题请联系删除。
