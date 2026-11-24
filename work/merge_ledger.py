# -*- coding: utf-8 -*-
"""台账合并器（带文件锁，避免多条校对线并发覆盖 checks.csv）。

用法：
    python3 work/merge_ledger.py work/verify/ledger-<range>.csv

规则：
1. 分片台账字段必须与 checks.csv 一致（q,page,verdict,note,time）。
2. 同题号冲突时按可信度取：fixed < pass < skip < fail（fail 优先，宁可下线不漏错）。
3. 合并全程持 flock，禁止并发写。
"""
import csv
import fcntl
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "work", "checks.csv")
FIELDS = ["q", "page", "verdict", "note", "time"]
RANK = {"fixed": 0, "pass": 1, "skip": 2, "fail": 3}


def main(paths):
    with open(MAIN, "r+", encoding="utf-8", newline="") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        rows = list(csv.DictReader(fh))
        by_q = {r["q"]: r for r in rows}
        added = replaced = protected = 0
        for p in paths:
            if not os.path.exists(p):
                print("skip missing", p)
                continue
            for r in csv.DictReader(open(p, encoding="utf-8")):
                if not r.get("q"):
                    continue
                old = by_q.get(r["q"])
                if old is None:
                    by_q[r["q"]] = {k: r.get(k, "") for k in FIELDS}
                    added += 1
                elif old["verdict"] == "fixed" and r["verdict"] == "fail":
                    # 已修好的卡不允许被后到的 fail 打回（否则每轮返修白干）
                    protected += 1
                    continue
                elif RANK.get(r["verdict"], 0) >= RANK.get(old["verdict"], 0):
                    by_q[r["q"]] = {k: r.get(k, "") for k in FIELDS}
                    replaced += 1
        fh.seek(0)
        fh.truncate()
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for q in sorted(by_q, key=lambda x: int(x)):
            w.writerow(by_q[q])
        fcntl.flock(fh, fcntl.LOCK_UN)
    print(f"merged: {len(by_q)} rows (added {added}, replaced {replaced}, protected {protected})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    main(sys.argv[1:])
