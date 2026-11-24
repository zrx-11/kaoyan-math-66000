# -*- coding: utf-8 -*-
"""修复后改判：把复核台账里的判定**强制覆盖**写回 checks.csv（带 flock）。

merge_ledger.py 的排名规则是 fail 优先，无法把 fail 降回 pass/skip；
返修补完的题必须走本脚本才能重新上线。

用法：python3 work/verify/rerecord.py work/verify/reverify-1001-1200.csv
"""
import csv
import fcntl
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAIN = os.path.join(ROOT, "work", "checks.csv")
FIELDS = ["q", "page", "verdict", "note", "time"]
OK = {"pass", "skip", "fixed"}


def main(paths):
    with open(MAIN, "r+", encoding="utf-8", newline="") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        rows = list(csv.DictReader(fh))
        by_q = {r["q"]: r for r in rows}
        changed = skipped = 0
        for p in paths:
            if not os.path.exists(p):
                print("skip missing", p)
                continue
            for r in csv.DictReader(open(p, encoding="utf-8")):
                q = (r.get("q") or "").strip()
                if not q:
                    continue
                v = (r.get("verdict") or "").strip()
                if v not in OK:
                    print(f"  q{q} 判定为 {v}，保持原状（仍需返修）")
                    skipped += 1
                    continue
                old = by_q.get(q)
                if old and old.get("verdict") == v:
                    continue
                by_q[q] = {k: r.get(k, "") for k in FIELDS}
                changed += 1
        order = sorted(by_q, key=lambda x: int(x))
        fh.seek(0)
        fh.truncate()
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for q in order:
            w.writerow(by_q[q])
    print(f"改判写入 {changed} 条，保留原判 {skipped} 条；总行 {len(order)}")


if __name__ == "__main__":
    main(sys.argv[1:])
