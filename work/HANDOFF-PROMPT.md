# 交接提示词（给新 agent 的开场白）

> 用户视角：把这份里的模板复制给任意新 agent，它就能在仓库里把流程接下去。
> 原则：**仓库已经有全部口径与命令**，所以提示词只需要给「它在仓库里看不到的四样东西」+「本轮范围」。

---

## 一、仓库里没有、必须口头给的（就这四样）

| 项 | 为什么必须给 | 怎么给 |
|---|---|---|
| 仓库地址 + 分支 | 它得先 clone | `https://github.com/zrx-11/kaoyan-math-66000`，分支 `main` |
| 写权限凭据 | `publish.sh` 不含 token，只推 `origin main` | 用环境变量注入（`export GH_TOKEN=…`），**不要写进提示词正文** |
| 本轮范围 | 不定范围它会自己乱跑或建空任务 | 题号段 + 承载文件（用 `work/qa/range_map.py` 先查） |
| 额度/节奏约束 | 决定它能派几个子 agent、能不能发布 | 如「本轮只做 100 题、允许发布一次」 |

**不需要给的**：口径、命令、目录结构、雷区、事故处理、卡片格式、台账规则 —— 全在
`work/AGENT-HANDBOOK.md`、`work/spec/*.md` 里。重复给反而会让它以为手册不可信。

---

## 二、通用模板（复制即用，`<>` 处替换）

```
你是考研数学 66000 项目的接手 agent。

项目：冯建轩《考研数学 66000》全书逐题精解的可编辑 HTML 站点，部署在 GitHub Pages。
仓库：https://github.com/zrx-11/kaoyan-math-66000  分支 main
站点：https://zrx-11.github.io/kaoyan-math-66000/

第一步（不要跳过）：
  git clone https://github.com/zrx-11/kaoyan-math-66000 && cd kaoyan-math-66000
  读 work/AGENT-HANDBOOK.md（唯一权威手册，含口径/命令/雷区/事故/待办）
  读 work/README.md（工作台导航）、work/spec/LEDGER.md（台账规则）

现状快照（以你 clone 后的 work/gate.py 输出为准，不要相信旧数字）：
  在线卡片 2850（第一册《极限》2650 + 第二册《n 项和极限》200）
  第一册 q1–q2650 全部已核；checks.csv = pass 2140 / fixed 497 / skip 13 / fail 0
  闸门 python3 work/gate.py → cards=2850 failed=0 dup=117 quarantine=0

本轮任务：<例如：核 q<起>–q<止>，承载文件为 <文件>；或：清 105 张账实不符>

必须守的五条（违反了就要退回重做）：
  1. 题干只认页面图（pages/*.png，150dpi 灰度），PDF 文本层完全不可用
  2. 答案栏是唯一答案出口；书印值错就写复算值 + 紧跟一个 class="block caveat" 校勘块
  3. 「书给」只认页面图印值，不许从答案栏或旧 note 反抄
  4. fixed ⇔ caveat 双向成立；skip 只表示题面不可用，且 skip 卡不许带校勘块
  5. 不可辨的题面不许复原（只写「按原书印出的题面：发散（原书疑漏印一项）」）

禁止：
  - 手改 checks.csv（只经 merge_ledger.py / verify/rerecord.py）
  - 改 volumes/、data.json、knowledge/（生成物）
  - 跑 audit.py（会无锁整表重写台账）
  - 用 python/shell 字符串拼 HTML（反斜杠会被吞）
  - 整文件重建分片（写回基底必须是当前磁盘版本，只按题号块合并）

验收（做完必须贴这 5 条命令的原始输出）：
  python3 work/gate.py
  python3 work/gate_one.py <文件> <起> <止>
  python3 work/qa/plainlen.py <文件> <起> <止>
  python3 work/qa/ledger_audit.py <起> <止>
  git diff --stat <文件>        # 并证明区间外零改动

交付：改动文件与题号清单 + 区间外零改动证明（sha1）+ 闸门输出 + 台账 csv
发布：只在闸门 failed=0 时执行 bash work/publish.sh（必须 bash，不能 sh）
```

---

## 三、四个场景的变体（替换「本轮任务」那一段）

### A. 清账实不符（最省额度、最容易验收，建议第一次就派这个）

```
本轮任务：清账实不符，不要新增内容。
  python3 work/qa/ledger_audit.py     # 预期：fixed 无块 64、带块记 pass 41、带块记 skip 0
  分两类处置：记 fixed 却无块 → 回图确认书值是否真错，是则补 caveat，否则降 pass 并写「自纠/治理」；
  带块却记 pass → 回图确认后升 fixed。改判一律走 work/verify/rerecord.py。
  结束后 ledger_audit 三类告警必须都为 0。
```

### B. 核一个新区段

```
本轮任务：核 q<起>–q<止>（<N> 张）。
  先跑 python3 work/qa/range_map.py <起> <止> 确认承载文件，按文件边界切分片，不要跨文件抢活。
  每 50 题一片派执行体，subtask 里必须写清题号区间 + 文件路径（否则会造空任务）。
  开工先跑 python3 work/qa/find_orphans.py <文件> 扫游离 <p>。
  判定按 work/spec/LEDGER.md 的矩阵；写卡按 work/spec/CARD-FORMAT.md。
  参考期望：该段历史书错率约 <X>%（见手册 §8.2）。基线 fixed 很少时先怀疑漏判。
```

### C. 开新一册

```
本轮任务：启动第 <N> 册《<册名>》的专题 <tNN>，共 <M> 题。
  PDF 原文在 <路径>（不在仓库，195MB，需自备）；先 export PDF_PATH=<路径>。
  流程照 work/AGENT-HANDBOOK.md §7：pdftoppm 出 150dpi 灰度页图 → build_manifest.py → 按页段切片 →
  先出题干转录稿 work/drafts/stems-<段>.md → 再写卡 → gate_one → 建站。
  新专题必须先有讲解页骨架 work/content/lectures/<册>/t<NN>.html（标题形如「《专题名》M 题」），
  否则 build_site.py 不会把它挂上站点。
```

### D. 只维护与发布

```
本轮任务：不新增内容，只做维护。
  python3 work/qa/ledger_audit.py 全量审计 → 报告三类告警数字
  python3 work/qa/find_orphans.py → 报告游离段落
  python3 work/gate.py → 必须 failed=0
  然后 python3 work/build_site.py && bash work/publish.sh，并核对
  git ls-remote origin refs/heads/main 与本地 HEAD 一致。
```

---

## 四、让它自证的六个输出（交接质量就看这六条）

1. `work/gate.py` 原始输出（`cards`、`failed`、`dup`）
2. `work/qa/ledger_audit.py` 的三类数字（fixed 无块 / 带块记 pass / 带块记 skip）
3. 改动清单：文件 + 题号 + 每张改了什么（判档/加厚/改块）
4. **区间外零改动证明**：区间外 article 的 sha1 与开工前一致（用 `git diff --stat` 不够，要哈希）
5. `plainlen.py` 的 `ALL_IN_RANGE` + 行间公式 ≥3 + `min_plain≥620`
6. 台账 csv 路径（能被人逐行复核）

少任何一条，就说明它没按手册做。

---

## 五、五个最容易交接失败的坑（提前在提示词里点掉）

1. **不 clone 只读文档** → 它没有页面图，只能凭记忆或猜，题面必错。**必须 clone。**
2. **相信旧数字** → 提示词里的「2850 卡 / pass 2140」只是快照，真实值以它自己跑的 `gate.py` 为准，要写明。
3. **派活不给范围** → 会建空任务子智能体，白烧额度。
4. **整文件重建分片** → 会覆盖别线改动（`seg-799-807`、`seg-867-878` 都出过事）。写回基底必须是当前磁盘版本。
5. **把「篇幅在区间」当验收** → 614 张卡的公式缺口全藏在后面。必须同时验「行间公式 ≥3」。

---

## 六、如果对方是「人」而不是 agent

同样的模板可以用，但把「验收贴输出」换成「跑这五条命令并截图/粘结果」；
再说清一句：**所有改动都会进 git，所以任何时候都能看 `git log -1 --stat` 知道上一轮改了什么。**

---

## 七、要铺满 6 万题时，用两阶段模式（不是逐段精核）

背景与机制见 **`work/plan/README.md`**。一句话：先把每道题都有一张结构完整的卡，
全部铺完后再统一核验。计划由磁盘事实推导，`python3 work/plan/build_plan.py` 随时刷新。

### 模板 A · 阶段一（覆盖，只求结构完整）

```
本轮任务：推进阶段一（覆盖）。只保证结构完整，不做数值核验、不判 fixed/skip。

  python3 work/plan/next_batch.py <N> [--vol <X>]      # 取 N 个单元，含页图命令与目标分片路径
  python3 work/plan/scaffold_topic.py <slug> <t>        # 仅当讲解页缺失时跑
  pdftoppm -png -r 150 -gray -f <起> -l <止> "$PDF_PATH" work/pages/<slug>/p
  # 先出题干转录稿 work/drafts/stems-<起>-<止>.md，再按 work/spec/CARD-FORMAT.md 写卡
  python3 work/qa/gate_lite.py work/fragments/<slug>/t<NN>/seg-<起>-<止>.html
        # 必须 fail=0；这是阶段一闸门（六块齐/答案非空/无禁词/sol≥150/有行间公式）
  台账：verdict 一律 pass，note 写「[cover] 结构闸门通过；待阶段二复算」
  python3 work/plan/build_plan.py && python3 work/build_site.py && bash work/publish.sh

禁止：不要 --refreeze（会让专题编号全部错位）；不要按题号切派活范围（按分片文件切）；
      不要跳号或重号（id 全局连续，从 next_batch 给的起始 id 起；qno 是专题内编号）。
```

### 模板 B · 阶段二（核验）

```
本轮任务：核验阶段一的 cover 卡。

  python3 work/plan/verify_queue.py --limit <N> [--vol <X>]
  逐题回页面图核题干 → 独立复算 → 按 work/spec/LEDGER.md 判 pass / fixed / skip
  改判一律走 work/verify/rerecord.py；结束 python3 work/qa/ledger_audit.py 三类告警必须为 0

验收：verify_queue.py 输出条数下降（最终为 0）、ledger_audit 无告警、gate.py failed=0。
```

**怎么区分两阶段**：台账 note 里带 `[cover]` 的是「只过结构闸门」；不带的是核过的。
`verify_queue.py` 就是按这个标记取的，所以阶段一入账时**必须写这个前缀**，否则那道题永远不会被核。
