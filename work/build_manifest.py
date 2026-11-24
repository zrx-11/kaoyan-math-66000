# -*- coding: utf-8 -*-
"""扫描 PDF 书签，生成 16 分册 / 子册 / 页码区间 的结构清单。"""
import json
import os
import re

import pymupdf

PDF = "/home/user/Doubao/chats/38454435152889602/冯建轩《考研数学66000》最后一舞.pdf"
OUT = "/home/user/Doubao/chats/38454435152889602/work/manifest"


def norm(t):
    t = re.sub(r"[\u0000-\u001f]", "", t)
    return t.strip()


def main():
    os.makedirs(OUT, exist_ok=True)
    doc = pymupdf.open(PDF)
    toc = doc.get_toc(simple=False)  # [level, title, page, dest]
    entries = [(lv, pg, norm(ti)) for lv, ti, pg, _ in toc if "空白" not in ti]
    entries = [e for e in entries if e[2]]

    total = doc.page_count
    tops = [e for e in entries if e[0] == 1]
    vols = []
    for i, (lv, start, title) in enumerate(tops):
        end = tops[i + 1][1] - 1 if i + 1 < len(tops) else total
        kids = [e for e in entries if e[0] >= 2 and start <= e[1] <= end]
        vols.append(
            {
                "idx": i + 1,
                "title": title,
                "start": start,
                "end": end,
                "pages": end - start + 1,
                "sections": [
                    {"level": k[0], "title": k[2], "page": k[1]} for k in kids
                ],
            }
        )

    data = {"pdf_pages": total, "volumes": vols}
    with open(os.path.join(OUT, "volumes.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    for v in vols:
        print(f"{v['idx']:>2}. p{v['start']}-{v['end']} ({v['pages']}p)  {v['title']}  子项{len(v['sections'])}")
    print("total pages", total)


if __name__ == "__main__":
    main()
