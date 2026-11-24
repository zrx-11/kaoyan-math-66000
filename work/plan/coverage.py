# -*- coding: utf-8 -*-
"""按册/专题统计覆盖率（页口径 + 卡片口径）。

用法：python3 work/plan/coverage.py
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.path.join(ROOT, "work")
FRAG = os.path.join(WORK, "fragments")
PLAN = os.path.join(WORK, "plan")

SEG_RE = re.compile(r"seg-(\d+)-(\d+)")
ID_RE = re.compile(r'<article class="q" id="q(\d+)"')


def main():
    topics = json.load(open(os.path.join(PLAN, "topics.json"), encoding="utf-8"))["volumes"]
    waves = json.load(open(os.path.join(PLAN, "waves.json"), encoding="utf-8"))

    # 按 slug 统计卡片与页覆盖
    ids, segs = {}, {}
    for f in glob.glob(os.path.join(FRAG, "**", "*.html"), recursive=True):
        parts = os.path.relpath(f, FRAG).split(os.sep)
        slug = parts[0]
        if slug == "jixian":
            slug = "02-gaoshu-15000"
        txt = open(f, encoding="utf-8", errors="replace").read()
        for hit in ID_RE.findall(txt):
            ids.setdefault(slug, set()).add(int(hit))
        m = SEG_RE.search(os.path.basename(f))
        if m:
            segs.setdefault(slug, []).append((int(m.group(1)), int(m.group(2))))

    bu = {}
    for u in waves["units"]:
        bu.setdefault((u["vol"], u["topic"]), []).append(u["status"])
    print(f"{'册':6s} {'页':>6s} {'覆盖页':>7s} {'页率':>7s} {'卡片':>7s} {'专题(完成/总)':>14s}")
    tot_cards = 0
    for slug, vv in topics.items():
        pages = vv["end"] - vv["start"] + 1
        rng = segs.get(slug, [])
        cov = sum(1 for p in range(vv["start"], vv["end"] + 1) if any(a <= p <= b for a, b in rng))
        c = len(ids.get(slug, ()))
        tot_cards += c
        done_t = sum(1 for t in vv["topics"]
                     if all(s == "done" for s in bu.get((vv["idx"], t["t"]), [])))
        print(f"V{vv['idx']:<5d} {pages:6d} {cov:7d} {cov/pages*100:6.1f}% {c:7d} {done_t:6d}/{len(vv['topics']):<6d}")
    print(f"\n总卡片 {tot_cards}；待生产单元 {sum(1 for u in waves['units'] if u['status']=='pending')}")


if __name__ == "__main__":
    main()
