# 生产工作流（plan/）：先覆盖，后核验

这是本项目**规模化推进**的入口。原则只有一条：

> **先把 6.4 万题全部有一张结构完整的卡（阶段一），再统一做数值核验与账实审计（阶段二）。**
> 反过来做（边写边精核）在 6 万题规模上跑不完，且每段的返修都会打断后面。

## 1. 三个状态文件，机制各不相同

| 文件 | 谁维护 | 说明 |
|---|---|---|
| `topics.json` | **人工/首次自动生成后冻结** | 专题编号表。`t` 决定 `fragments/<册>/tNN/` 路径，**不得改动**；`name`/`page` 可人工修正 |
| `waves.json` / `waves.md` | `build_plan.py` 自动 | 单元清单。**状态由磁盘事实推导**：分片存在即 done。重跑即刷新，永不腐烂 |
| `waived.json` | 人工 | 已确认「这一段没有题」（空白页/答案页）的单元 id 白名单，避免假缺口 |

时间花在维护人工状态文件上的项目都会腐烂。这里只有 `waived.json` 和 `topics.json` 需要人管，其余全自动。

## 2. 阶段一：覆盖（COVER）

单个单元（默认 10 页 ≈ 50–60 题）的标准动作：

```bash
# ① 取下一个可派单元（含页图命令、目标分片路径、全局起始 id）
python3 work/plan/next_batch.py 4

# ② 讲解页缺失就先补骨架（否则站点挂不出该专题目录）
python3 work/plan/scaffold_topic.py <slug> <t>

# ③ 出页面图（150dpi 灰度，唯一题干来源）
export PDF_PATH=/path/to/冯建轩《考研数学66000》最后一舞.pdf
mkdir -p work/pages/<slug>
pdftoppm -png -r 150 -gray -f <起页> -l <止页> "$PDF_PATH" work/pages/<slug>/p

# ④ 先出题干转录稿，再写卡（照 work/spec/CARD-FORMAT.md）
#    work/drafts/stems-<起页>-<止页>.md

# ⑤ 写卡 → 阶段一闸门
python3 work/qa/gate_lite.py work/fragments/<slug>/t<NN>/seg-<起>-<止>.html

# ⑥ 入账：note 前缀写 [cover]，表示「只过结构闸门，未做数值核验」
#    verdict 一律 pass（阶段一不做判定），note 例：　[cover] 结构闸门通过；待阶段二复算

# ⑦ 推进后刷新计划、建站、发布
python3 work/plan/build_plan.py && python3 work/build_site.py && bash work/publish.sh
```

阶段一闸门 `gate_lite.py` 只判「结构残废」：六块齐、答案非空、无禁词、`sol≥150` 字、
至少一处行间公式、变式有 `var-ans`。**它不判数值对错**——那正是阶段二的事。

### 阶段一的硬约定

- **id 全局连续分配**：新卡从当前最大 id + 1 开始（`next_batch.py` 会算给你）。
- **qno 是专题内编号**：卡面「第 N 题」从 1 起，与 id 无关。
- **不许跳号、不许重号**：`gate_lite.py` 会报同批次重复。
- 一批做完立刻入账，别攒；入账用 `merge_ledger.py`。

## 3. 阶段二：核验（VERIFY）

```bash
# 取出所有「只过结构闸门」的题
python3 work/plan/verify_queue.py                    # 全量
python3 work/plan/verify_queue.py --vol 2 --limit 200 # 按册、限量
```

核验口径与现有已核段完全一致（`work/spec/QC.md` + `LEDGER.md`）：
逐题回页面图核题干 → 独立复算 → 判 `pass`/`fixed`/`skip` → 改判走 `rerecord.py`
→ `ledger_audit.py` 三类告警为 0。

**阶段二结束的标志**：`verify_queue.py` 输出为空，且 `ledger_audit.py` 无告警。

## 4. 命令总表

| 命令 | 作用 |
|---|---|
| `python3 work/plan/build_plan.py` | 重算计划（不碰 topics.json，除非 `--refreeze`） |
| `python3 work/plan/next_batch.py N [--vol X]` | 取 N 个可派单元 + 页图命令 |
| `python3 work/plan/scaffold_topic.py <slug> [t]` | 补讲解页骨架 |
| `python3 work/plan/coverage.py` | 按册覆盖率（页口径 + 去重卡片数） |
| `python3 work/plan/verify_queue.py` | 阶段二待核队列 |
| `python3 work/qa/gate_lite.py <文件\|目录>` | 阶段一闸门 |
| `python3 work/qa/range_map.py 起 止` | 题号 → 承载文件 |
| `python3 work/qa/find_orphans.py` | 扫游离 `<p>` |
| `python3 work/qa/ledger_audit.py` | 账实审计（fixed ⇔ caveat） |

## 5. 现在的账（快照）

- 16 册全部进入计划，共 **1235 个单元**，已完成 **67**，待生产 **1168** 单元 / **11392 页**。
- 按每页约 5.7 题估算，待生产约 **6.4 万题**（含已上线 2850 题则总量约 6.7 万，与全书题量吻合）。
- 第一册《极限》与第二册《n 项和极限》已全部完成并**已过阶段二**（不属于 cover 队列）。

## 6. 不能用错的三件事

1. **不要 `--refreeze`**：会让所有 `tNN` 重新编号，已建卡的目录全部错位。
2. **不要按题号切派活范围**：一律按分片文件切，`range_map.py` 先查。两段共享一个文件时只按块合并。
3. **不要把阶段一的 `pass` 当成「已核」**：`note` 里没有 `[cover]` 的才是核过的。审计与统计都按这条区分。
