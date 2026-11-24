# -*- coding: utf-8 -*-
"""生成全书生产计划（waves.json / waves.md）。

设计原则：**计划由磁盘事实推导，不维护人工状态文件。**
每次重跑都会重新扫描 manifest 与现有分片，已完成的部分自动变 done，
所以计划永远不会因为「忘了更新状态」而腐烂。

用法：
    python3 work/plan/build_plan.py                 # 重新生成
    python3 work/plan/build_plan.py --chunk 5       # 改每单元页数（默认 10）

产出：
    work/plan/waves.json   机器可读：单元清单 + 汇总
    work/plan/waves.md     人可读：按册/专题列出进度

单元（unit）= 一个页段（默认 10 页）+ 一个专题。这是派活的最小粒度。
"""
import argparse
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANI = os.path.join(ROOT, "work", "manifest")
FRAG = os.path.join(ROOT, "work", "fragments")
OUT = os.path.join(ROOT, "work", "plan")

SLUG = {
    1: "01-tixing-6000", 2: "02-gaoshu-15000", 3: "03-xiandai-6600", 4: "04-weilai-3000",
    5: "05-liming-2000", 6: "06-gaoshu-2600", 7: "07-xiandai-1200", 8: "08-gailv-950",
    9: "09-gaoshu-9000", 10: "10-xiandai-2500", 11: "11-gailv-2900", 12: "12-kaoti-3030",
    13: "13-kaoti-2310", 14: "14-kaoti-2450", 15: "15-kaoti-2500", 16: "16-kaoti-1650",
}

SEG_RE = re.compile(r"seg-(\d+)-(\d+)")
TOPICS_FILE = os.path.join(OUT, "topics.json")


def freeze_topics(vols, force=False):
    """专题编号冻结表。

    为什么需要：专题编号 tNN 决定 fragments/<slug>/tNN/ 目录路径。
    如果每次构建都从标题重新解析，一旦改了解析规则，已建好的 6 万题卡全部路径错位。
    所以首次生成后**只读不重算**；人工可以改 name/page，但不要改 t。

    --refreeze 会重算（危险，仅在没有已建卡目录时使用）。
    """
    if os.path.exists(TOPICS_FILE) and not force:
        return json.load(open(TOPICS_FILE, encoding="utf-8"))

    data = {"_note": "专题编号冻结表。t 不得改动（决定目录路径）；name/page 可人工修正。",
            "volumes": {}}
    for v in vols:
        idx, slug = v["idx"], SLUG.get(v["idx"], f"{v['idx']:02d}")
        ts = topics_of(v)
        if not ts:
            # 兜底：整册作为一个专题，避免某些册（结构特殊）在计划里彻底消失
            name = re.sub(r"^[\d.、\s]+", "", v["title"]).strip(" -_·")
            ts = [{"name": name[:30] or f"第{idx}册", "page": v["start"]}]
        starts = [t["page"] for t in ts]
        items = []
        for i, t in enumerate(ts):
            lo = max(v["start"], t["page"])
            hi = (starts[i + 1] - 1) if i + 1 < len(starts) else v["end"]
            items.append({"t": i + 1, "name": t["name"], "page": lo,
                          "page_end": max(lo, hi), "count": t.get("count")})
        data["volumes"][slug] = {"idx": idx, "start": v["start"], "end": v["end"],
                                  "topics": items}
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(TOPICS_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return data


def topics_of(v):
    """与 build_site.py 的 parse_topics 完全同规则（否则 tNN 编号会错位）：
    书名号项 ≥2 用它；否则回退 level-2 标题项；同名项加「（二）（三）」。"""

    def clean(n):
        n = re.sub(r"[（(]\s*(副本|已自动恢复|修复的)\s*[)）]", "", n)
        n = re.sub(r"\s*[-–]\s*副本\s*(?:[（(]\s*\d+\s*[)）])?", "", n)
        n = re.sub(r"[（(]\s*\d+\s*[)）]", "", n)
        n = re.sub(r"\s*(副本|已自动恢复|修复的)\s*$", "", n)
        return n.strip(" -_·")

    named, seen = [], set()
    for s in v["sections"]:
        ms = re.findall(r"《([^《》]{2,40})》", s["title"])
        if not ms:
            continue
        name = ms[-1].strip()
        k = re.sub(r"\s+", "", name)
        if not k or k in seen:
            continue
        seen.add(k)
        named.append({"name": name, "page": s["page"]})

    counts, lvl2 = {}, []
    for s in v["sections"]:
        if s.get("level") != 2:
            continue
        name = clean(re.sub(r"^[\d.、\s]+", "", s["title"]))
        if len(name) < 4:
            continue
        k = re.sub(r"\s+", "", name)
        counts[k] = counts.get(k, 0) + 1
        lvl2.append({"name": name if counts[k] == 1 else f"{name}（{counts[k]}）",
                     "page": s["page"]})

    if len(named) >= 2:
        return named
    if len(lvl2) >= 2:
        return lvl2
    return named or lvl2


def done_ranges():
    """扫描现有分片，返回 {slug: [(lo, hi), ...]}。文件名 seg-<起页>-<止页> 即页范围。"""
    out = {}
    for f in glob.glob(os.path.join(FRAG, "**", "*.html"), recursive=True):
        b = os.path.basename(f)
        m = SEG_RE.search(b)
        if not m:
            continue
        slug = os.path.relpath(f, FRAG).split(os.sep)[0]
        # 目录形如 02-gaoshu-15000/t01/seg-xxx.html 或 jixian/...
        parts = os.path.relpath(f, FRAG).split(os.sep)
        if parts[0] == "jixian":
            slug = "02-gaoshu-15000"
        out.setdefault(slug, []).append((int(m.group(1)), int(m.group(2))))
    return out


def uncovered(lo, hi, ranges):
    """该块里还没被任何分片覆盖的页。"""
    return [p for p in range(lo, hi + 1) if not any(a <= p <= b for a, b in ranges)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunk", type=int, default=10)
    ap.add_argument("--refreeze", action="store_true", help="重算专题编号（危险：会让已建卡的 tNN 目录错位）")
    args = ap.parse_args()

    vols = json.load(open(os.path.join(MANI, "volumes.json"), encoding="utf-8"))["volumes"]
    done = done_ranges()
    waived = {}
    wf = os.path.join(OUT, "waived.json")
    if os.path.exists(wf):
        waived = json.load(open(wf, encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)

    units, summary = [], {"done_units": 0, "pending_units": 0, "pages_pending": 0,
                          "pages_done": 0, "cards_existing": 0}
    md = ["# 全书生产计划（由磁盘事实推导）", "",
          f"单元粒度：{args.chunk} 页 / 单元。已完成 = 该单元每一页都已被现有分片覆盖。",
          "状态为自动判定，重跑 `python3 work/plan/build_plan.py` 即刷新。", ""]

    plan = freeze_topics(vols, force=args.refreeze)
    for slug, vv in plan["volumes"].items():
        idx = vv["idx"]
        for t in vv["topics"]:
            i = t["t"] - 1
            lo, hi = t["page"], t["page_end"]
            if hi < lo:
                hi = lo
            md.append(f"## 第 {idx} 册 `{slug}` 专题 {t['t']:02d}《{t['name']}》 P{lo}–{hi}")
            md.append("")
            md.append("| 单元 | 页段 | 状态 |")
            md.append("|---|---|---|")
            for a in range(lo, hi + 1, args.chunk):
                b = min(a + args.chunk - 1, hi)
                uid = f"V{idx:02d}-t{i+1:02d}-{a:05d}-{b:05d}"
                miss = uncovered(a, b, done.get(slug, []))
                # 边界页豁免：专题首页/章节页常无题，缺 1 页不算缺口；人工豁免清单直接算完成
                is_done = len(miss) <= 1 or uid in waived
                units.append({"id": uid, "vol": idx, "slug": slug, "topic": i + 1,
                              "topic_name": t["name"], "pages": [a, b],
                               "status": "done" if is_done else "pending"})
                if is_done:
                    summary["done_units"] += 1
                    summary["pages_done"] += b - a + 1
                else:
                    summary["pending_units"] += 1
                    summary["pages_pending"] += b - a + 1
                tag = "done" if is_done else f"pending（缺 {len(miss)} 页）"
                if uid in waived:
                    tag = "done（人工豁免）"
                md.append(f"| `{uid}` | {a}–{b} | {tag} |")
            md.append("")

    summary["cards_existing"] = None
    payload = {"generated_by": "work/plan/build_plan.py", "chunk_pages": args.chunk,
               "summary": summary, "units": units}
    json.dump(payload, open(os.path.join(OUT, "waves.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    md.insert(3, f"汇总：单元 {summary['done_units']} done / {summary['pending_units']} pending；"
                 f"页 {summary['pages_done']} done / {summary['pages_pending']} pending"
                 f"（按每页约 5.6 题估算待生产约 {int(summary['pages_pending']*5.66/100)*100} 题）。")
    md.append("")
    md.append("## 怎么用")
    md.append("")
    md.append("```bash")
    md.append("python3 work/plan/next_batch.py 4        # 取接下来 4 个可派单元（含页图命令与目标分片路径）")
    md.append("python3 work/plan/build_plan.py          # 生产推进后重跑，done 会自动变多")
    md.append("```")
    open(os.path.join(OUT, "waves.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")

    print(f"units: {len(units)}  待生产单元 {summary['pending_units']}  待生产页 {summary['pages_pending']}")
    print(f"→ {OUT}/waves.json  {OUT}/waves.md")


if __name__ == "__main__":
    main()
