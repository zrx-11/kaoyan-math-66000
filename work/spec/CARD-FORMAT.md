# 卡片结构规范（CARD-FORMAT）

一张卡 = 一个 `<article class="q" id="qN">`。分片文件只放卡片，不含 `<html>`/`<body>`/导航。
站点页面由 `build_site.py` 把卡片按题号排序、每 100 题一页装进模板。

金标准样板：`work/templates/gold-1-6.html`（第 1–6 题）。
任何结构与写法冲突，以本文件 + `work/spec/QC.md` 为准。

---

## 1. 完整骨架

```html
<article class="q" id="q1795">
  <div class="q-head">
    <span class="qno">第 1795 题</span>
    <span class="qtype">给定七阶导数值求极限</span>
    <span class="qsrc">P934</span>
  </div>

  <div class="stem">
    <p>设 \(f(x)\) 在 \(x=0\) 处七阶可导……求 \(\lim\limits_{x\to0}\dfrac{f(x)-x-x^{7}}{x^{8}}\)。</p>
  </div>

  <div class="answer">答案：条件不足，极限不确定（仅凭七阶可导不能推出 \(0\)）</div>

  <div class="block caveat"><div class="block-title">校勘说明</div>
    <p>书给 \(0\)，按题面复算为条件不足……以复算结论为准。</p>
  </div>

  <div class="block sol">
    <div class="block-title">解析</div>
    <p>识别类型：……</p>
    \[ f(x)=x+x^{7}+o(x^{7}). \]
    <p>……</p>
  </div>

  <div class="block pit">
    <div class="block-title">易错点</div>
    <p>① ……</p>
  </div>

  <div class="block trend">
    <div class="block-title">考向</div>
    <p>……</p>
  </div>

  <div class="block var">
    <div class="block-title">变式</div>
    <p><b>变式</b> 设 …… 求 ……</p>
    <p class="var-ans">答案：\(0\)。分子是 \(o(x^{7})\)，除以 \(x^{7}\) 得 \(o(1)\to0\)。</p>
  </div>
</article>
```

选择题在 `stem` 内加一层选项容器：

```html
  <div class="stem">
    <p>题干……</p>
    <div class="opts">
      <p>(A) \(|a_n|>\dfrac{|a|}{3}\)</p>
      <p>(B) ……</p>
      <p>(C) ……</p>
      <p>(D) ……</p>
    </div>
  </div>
```

---

## 2. 字段规则

| 元素 | 规则 |
|---|---|
| `id="qN"` | 必须 `q` + 题号，全库唯一，顺序严格递增；站点按它排序 |
| `qno` | 「第 N 题」，N 与 id 一致 |
| `qtype` | 6–14 字的题型名，尽量复用知识树里的既有分类（见 `content/summary/jixian-types.json`） |
| `qsrc` | 页面图编号，形如 `P934`。**这个 P 号直接对应 `pages/.../p00934.png`，不要再做任何加减** |
| `stem` | 题干，必须与页面图**逐字**一致（数字、下标、括号层级、上下标位置） |
| `answer` | 唯一答案出口，一行 `<div class="answer">答案：…</div>` |
| `block sol` | 完整推导，301–420 字 |
| `block pit` | 易错点，编号 ①②③，每条一句判断 + 一句依据 |
| `block trend` | 考向，讲这题在考研里怎么考、变体方向 |
| `block var` | 变式，至少 1 条，含 `<p class="var-ans">答案：…</p>` |
| `block caveat` | **只在书印值错时出现**，紧跟 `answer` 之后 |

### 数学写法

- 行内 `\( … \)`，行间 `\[ … \]`（display 公式**独占一行**，前后不留句子）。
- 分数 `\dfrac`（行内）`\frac`（行间皆可）；极限 `\lim\limits_{n\to\infty}`。
- 裸 `<` `>` 一律写 `\lt{}` `\gt{}`，否则 HTML 解析会吞段。
- 严禁用 Unicode 字符代替 \frac、\lim、上下标。

---

## 3. 校勘块（caveat）细则

**触发条件**：页面图上书印答案与独立复算不一致。

**位置**：紧接 `<div class="answer">` 之后、`block sol` 之前。**不在解析里、不写成 HTML 注释。**

**固定开头**：`书给 X，按题面复算为 Y。`

**必须包含**：书印值 → 复算值 → 一句为什么书错（漏项/漏权/阶次错位/符号反/取了极限但不该取）。

**篇幅**：40–120 字。只写差异与原因，不重述解析。

真实示例（q1795）：

```html
<div class="block caveat"><div class="block-title">校勘说明</div>
<p>书给 \(0\)，按题面复算为条件不足、极限不确定。题设仅给七阶可导，泰勒余项只能写 \(o(x^{7})\)：\(f(x)=x+x^{7}+o(x^{7})\)，分子 \(f(x)-x-x^{7}=o(x^{7})\)，除以 \(x^{8}\) 得 \(o(1)/x\)，七阶信息不足以定出极限。反例：……三者七阶导数数据均与题设一致。书答 \(0\) 只对应特定光滑模型，不能由题面推出，以复算结论为准。</p></div>
```

**反向规则（同样重要）**：

- 书答**对** → 不许加 caveat。加了会让审计报「带块却记 pass」。
- 判 `skip` → **删掉一切 caveat 块**（skip 的语义是「题面不可用」，没有任何可校勘的对象）。
- 书答对、但**书印解析分步错** → 可保留 caveat，但开头改成「书印解析在……一步写错，结论仍正确」。

---

## 4. 变式（var）细则

- 变式是**自己出的题**，不是书上的。因此变式的答案**永远不进 caveat**。
- `<p class="var-ans">` 必须与同卡变式的解析自洽。**最高频的记账错**就是：变式答案栏写了一个值、解析推的是另一个值，然后整卡被判成 `fixed`（其实是自误）。
- 变式 1–2 条即可；有 3 条以上时确认整卡 plain 仍 ≤ 上限。
- 变式可以改成「只挪分母」「只改符号」「改成参数化」——但结论变了就得如实写，例如「只把分母的 \(n\) 换成 \(n+1\) 时结论是**不存在**，不是原答案」。

---

## 5. 禁用词与硬红线

**禁词（出现即被 `gate.py` 隔离下线）**：

- `核对：` —— 换成「核对后」「经查」
- `略去` —— 换成「省略」
- `待补` —— 换成「留作练习」或直接写全

**红线**：

1. 不许有 `答案：待补充`「见解析」这类空答案。
2. 不许用填充句凑字数（「综上所述」「由此可知本题考察了……」）。
3. 不许把书印值留在答案栏、把复算值塞进 caveat。
4. 不许复制粘贴同族题的解析只改数字（会被同段审计发现重复段落）。

---

## 6. 自检

```bash
# 单分片结构与题号连续性
python3 work/gate_one.py <分片> <起题号> <止题号>

# 篇幅 / 公式三维（唯一字数口径）
python3 work/qa/plainlen.py <分片或目录> [起 止]
# 期望输出形如：
#   q1674  第 1674 题  723  389  282  118  3  46
#   整卡 | sol | pit | trend | 公式数 | var
#   ALL_IN_RANGE

# 账实一致性（fixed ⇔ caveat 双向）
python3 work/qa/ledger_audit.py <起> <止>
```

判定标准：`OK cards=N range=… min_plain=≥620`、`ALL_IN_RANGE`、`FAILED 0`、审计三类告警为 0。

---

## 7. 常见错误写法对照

| 错 | 对 |
|---|---|
| `<div class="answer">答案：1/6</div>`（书错值） | `<div class="answer">答案：1/9</div>` + 紧跟 caveat |
| caveat 塞进 `block sol` 里一段 | 独立 `block caveat`，在 answer 之后 |
| `id="1795"` | `id="q1795"` |
| `<article class="q" id="q1795">` 无 `</article>` | 必须有闭合，缩进不影响解析但要有 |
| `\(x<1\)` | `\(x\lt{}1\)` |
| 变式答案写「见解析」 | 给出具体值 + 一句来源 |
| skip 卡留着 caveat | 删块，note 写明「题面不可用：……」 |
