#!/usr/bin/env python3
"""把若干「草稿分片」按页序装配成一个正式分片，并统一分配全局 id 与专题内 qno。

为什么需要：并行生产时多个子智能体各自写卡，若各自从同一个起始 id 开始必然撞号；
分配 id 区块又会留下空号（破坏「不许跳号」）。正确做法是——
让子智能体只写「内容」，id 一律写成 qTMP（或任意），由本脚本在装配时按
(页号, 文件内位置) 排序后**连续**分配。

用法：
  python3 work/qa/assemble.py --out work/fragments/01-tixing-6000/t01/seg-20-27.html \
      --start 2910 --qno-start 60 \
      work/drafts/tixing-20-23.html work/drafts/tixing-24-27.html

- --start    全局 id 起始值（next_batch.py 会给）
- --qno-start 专题内「第 N 题」起始值（上一片末号 +1）
- 输出文件若已存在则拒绝覆盖（除非 --force），防止误吞已上线内容。
"""
import argparse
import os
import re
import sys

ART_RE = re.compile(r'<article class="q".*?</article>', re.S)
PAGE_RE = re.compile(r'class="qsrc">P(\d+)<')
QNO_RE = re.compile(r'(<span class="qno">第\s*)(\d+)(\s*题</span>)')
ID_RE = re.compile(r'(<article class="q" id="q)([^"]+)(")')


def parse(path):
    txt = open(path, encoding="utf-8").read()
    out = []
    for m in ART_RE.finditer(txt):
        h = m.group(0)
        p = PAGE_RE.search(h)
        page = int(p.group(1)) if p else 10 ** 9
        out.append((page, h))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--qno-start", type=int, required=True)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()

    if os.path.exists(a.out) and not a.force:
        sys.exit(f"目标已存在：{a.out}（加 --force 覆盖）")

    pool = []
    for i, f in enumerate(a.files):
        for page, h in parse(f):
            pool.append((page, i, h))
    pool.sort(key=lambda x: (x[0], x[1]))

    qid, qno, res = a.start, a.qno_start, []
    for _, _, h in pool:
        h = ID_RE.sub(lambda m: f'{m.group(1)}{qid}{m.group(3)}', h, count=1)
        h = QNO_RE.sub(lambda m: f'{m.group(1)}{qno}{m.group(3)}', h, count=1)
        res.append(h)
        qid += 1
        qno += 1

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n\n".join(res) + "\n")
    print(f"装配 {len(res)} 张 → {a.out}")
    print(f"id q{a.start}–q{qid-1}    qno 第{a.qno_start}–{qno-1}题")


if __name__ == "__main__":
    main()
