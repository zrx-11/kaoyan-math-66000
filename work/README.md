# 工作台（work/）

这里是这个项目的**全部生产资产**。站点 `volumes/`、`data.json`、`knowledge/` 都是由这里的
源文件生成的，别手改生成物。

第一次接手，按这个顺序读：

1. **`AGENT-HANDBOOK.md`** —— 现状、口径、命令、坑、下一步。**先读这份。**
2. `spec/CARD-FORMAT.md` —— 一张卡长什么样。
3. `spec/LEDGER.md` —— 台账怎么记、怎么改判。
4. `spec/QC.md` —— 全部校验口径与 15 类复发错误族（最新、最全）。
5. `spec/PIPELINE.md` / `spec/VERIFY.md` —— 流水线总述与复核流程。

---

## 目录

| 路径 | 是什么 | 能不能改 |
|---|---|---|
| `fragments/02-gaoshu-15000/t01/*.html` | **第一册题卡源文件**（78 个分片，q1–q2650） | ✅ 唯一该改内容的地方 |
| `fragments/02-gaoshu-15000/t02/*.html` | 第二册题卡源（8 个分片，Q1–Q200） | ✅ |
| `fragments/jixian/parts/` | 历史空目录（占位，站点构建兼容用） | 勿放新卡 |
| `pages/jixian/p00NNN.png` | 第一册页面图 506 张，**题干唯一来源** | ❌ 只读 |
| `pages/nxh/p-0NNNN.png` | 第二册页面图 38 张 | ❌ 只读 |
| `checks.csv` | 第一册台账（2650 行） | ⚠️ 只经脚本写 |
| `state/` | 历史台账、交叉表、审计样例 | 留档 |
| `manifest/*.json` | 题号↔页码映射（有已知缺陷，见手册 §7.2） | ❌ |
| `content/lectures/02-gaoshu-15000/*.html` | 专题知识讲解页（t01/t02 有真实内容，t03+ 是骨架） | ✅ |
| `content/summary/*.json` | 知识树数据（板块划分） | ✅ 改完重跑 `build_knowledge.py` |
| `templates/gold-1-6.html` | 金标准样板 | 参考 |
| `spec/` | 规范文档 | ✅ 发现新坑就写进 `QC.md` |

## 工具

| 脚本 | 作用 |
|---|---|
| `gate.py` | 全库体检：卡片数、隔离、重复、覆盖率 |
| `gate_one.py` | 单分片结构 + 题号区间 + 六块齐全 |
| `spotcheck.py` | 看板 + 返工清单（写 `spotcheck.md` / `fixlist.json`） |
| `build_site.py` | 建站：排序去重、每 100 题一页、生成目录与进度 |
| `build_knowledge.py` | 建知识树页面 |
| `build_manifest.py` | 从 PDF 书签生成 manifest（需 PDF + pymupdf） |
| `merge_ledger.py` | 台账合并（flock + 优先级） |
| `verify/rerecord.py` | 改判（强制覆盖） |
| `qa/plainlen.py` | 字数三维（**唯一口径**） |
| `qa/find_orphans.py` | 扫 article 外的游离 `<p>` |
| `qa/ledger_audit.py` | 账实一致性审计（fixed ⇔ caveat） |
| `qa/range_map.py` | 题号 → 承载文件（派活前必跑） |
| `publish.sh` | 闸门 → 构建 → 提交 → 推送（必须 `bash` 执行） |
| `audit.py` | ⚠️ 误报高、会无锁重写台账，**并行时禁跑** |

## 五分钟上手

```bash
cd <仓库根>

# 1. 体检：期望 cards=2850 failed=0
python3 work/gate.py

# 2. 看清一段落在哪些文件
python3 work/qa/range_map.py 1621 1675

# 3. 单分片质检
python3 work/gate_one.py work/fragments/02-gaoshu-15000/t01/seg-901-911.html 1621 1675

# 4. 字数三维
python3 work/qa/plainlen.py work/fragments/02-gaoshu-15000/t01/seg-901-911.html 1621 1675

# 5. 账实审计
python3 work/qa/ledger_audit.py

# 6. 本地预览（无需构建）
python3 -m http.server 8000     # 打开 http://localhost:8000/
```

## 不在仓库里的东西

PDF 原文（195 MB，`.gitignore` 排除）、`work/text/`（PDF 文本层抽取，本身不可用）、
`work/drafts/`（历史题干转录稿）、`work/verify/` 的逐段快照备份。
要新开一册时需自备 PDF，并改 `build_manifest.py` 里的路径或设 `PDF_PATH` 环境变量。
