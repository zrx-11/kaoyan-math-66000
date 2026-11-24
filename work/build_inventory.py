# -*- coding: utf-8 -*-
"""逐页提取文本，统计每册/子册的题量、题号区间，输出题目索引。"""
import json
import os
import re
import sys

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = f"{ROOT}/冯建轩《考研数学66000》最后一舞.pdf"
MAN = f"{ROOT}/work/manifest/volumes.json"
TXT = f"{ROOT}/work/text"

QRE = re.compile(r"(\d{1,4})\s*[.、]?\s*【冯建轩题干】")
STEM = "【冯建轩题干】"
ANS = "【冯建轩简版答案】"
SOL = "【冯建轩解析】"


def main():
    vols = json.load(open(MAN, encoding="utf-8"))
    os.makedirs(TXT, exist_ok=True)
    doc = pymupdf.open(PDF)
    summary = []
    for v in vols["volumes"]:
        vdir = os.path.join(TXT, f"v{v['idx']:02d}")
        os.makedirs(vdir, exist_ok=True)
        nums = []
        per_page = {}
        for p in range(v["start"], v["end"] + 1):
            t = doc[p - 1].get_text()
            with open(os.path.join(vdir, f"p{p:05d}.txt"), "w", encoding="utf-8") as f:
                f.write(t)
            hit = [int(x) for x in QRE.findall(t)]
            per_page[p] = hit
            nums.extend(hit)
        nums_set = sorted(set(nums))
        sections = []
        for s in v["sections"]:
            sections.append({"level": s["level"], "title": s["title"], "page": s["page"]})
        # 每个子册题号区间
        sec_ranges = []
        for i, s in enumerate(v["sections"]):
            end = v["sections"][i + 1]["page"] - 1 if i + 1 < len(v["sections"]) else v["end"]
            qs = []
            for p in range(s["page"], end + 1):
                qs.extend(per_page.get(p, []))
            sec_ranges.append(
                {
                    "title": s["title"],
                    "level": s["level"],
                    "pages": [s["page"], end],
                    "q_count": len(qs),
                    "q_max": max(qs) if qs else 0,
                    "q_min": min(qs) if qs else 0,
                }
            )
        summary.append(
            {
                "idx": v["idx"],
                "title": v["title"],
                "pages": [v["start"], v["end"]],
                "page_count": v["pages"],
                "q_marks": len(nums),
                "q_max": max(nums) if nums else 0,
                "sections": sec_ranges,
            }
        )
        print(f"v{v['idx']:02d} {v['title'][:28]} 题标记{len(nums)} 最大题号{max(nums) if nums else 0}", flush=True)

    out = f"{ROOT}/work/manifest/inventory.json"
    json.dump(summary, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved", out)


if __name__ == "__main__":
    main()
