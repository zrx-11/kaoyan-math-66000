#!/usr/bin/env python3
"""为「阶段一 COVER」新卡补台账行（幂等：已存在 q 号则跳过）。

台账 work/checks.csv 表头 q,page,verdict,note,time。
阶段一的账一律 verdict=pass、note 以 [cover] 开头——这是阶段二队列的唯一筛选依据，
写错前缀等于这批题永远不会被复算。

用法：
  python3 work/qa/add_cover_rows.py work/fragments/01-tixing-6000/t01/seg-20-27.html
  python3 work/qa/add_cover_rows.py --dry-run work/fragments/.../seg-*.html
"""
import argparse
import csv
import datetime
import fcntl
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # work/qa -> work -> ROOT
LEDGER = os.path.join(ROOT, "work", "checks.csv")

ART_RE = re.compile(r'<article class="q" id="q(\d+)".*?</article>', re.S)
PAGE_RE = re.compile(r'class="qsrc">P(\d+)<')
NOTE = "[cover] 结构闸门通过；待阶段二复算"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--note", default=NOTE)
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()

    found = []
    for f in a.files:
        txt = open(f, encoding="utf-8").read()
        for m in ART_RE.finditer(txt):
            q = int(m.group(1))
            p = PAGE_RE.search(m.group(0))
            found.append((q, int(p.group(1)) if p else ""))

    lock = open(LEDGER, "r+", encoding="utf-8", newline="")
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        rows = list(csv.DictReader(lock))
        exist = {int(r["q"]) for r in rows if r.get("q", "").isdigit()}
        new = [(q, p) for q, p in found if q not in exist]
        dup_in_batch = len(found) - len({q for q, _ in found})
        if dup_in_batch:
            sys.exit(f"本批内部有 {dup_in_batch} 个重复 id，先修再入账")
        if not new:
            print("无需入账（全部已存在）")
            return
        if a.dry_run:
            print(f"将入账 {len(new)} 行：q{new[0][0]}–q{new[-1][0]}")
            return
        lock.seek(0, os.SEEK_END)
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        w = csv.writer(lock, lineterminator="\n")
        for q, p in sorted(new):
            w.writerow([q, p, "pass", a.note, ts])
        lock.flush()
        os.fsync(lock.fileno())
        print(f"入账 {len(new)} 行：q{new[0][0]}–q{new[-1][0]}")
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    main()
