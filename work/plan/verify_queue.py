# -*- coding: utf-8 -*-
"""阶段二待核队列：列出所有 note 含 [cover] 的题（只过结构闸门、未做数值核验）。

用法：
    python3 work/plan/verify_queue.py                     # 汇总按册计数
    python3 work/plan/verify_queue.py --vol 2            # 只看第 2 册
    python3 work/plan/verify_queue.py --limit 200        # 输出前 200 个题号
    python3 work/plan/verify_queue.py --limit 50 --vol 2 --topic 3

题号 → 页码：台账 page 字段（stage1 建卡时必须填对，否则这里定位不到页面图）。
"""
import argparse
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.path.join(ROOT, "work")
LEDGER = os.path.join(WORK, "checks.csv")


def volumes():
    vols = json.load(open(os.path.join(WORK, "manifest", "volumes.json"), encoding="utf-8"))["volumes"]
    return [(v["idx"], v["start"], v["end"]) for v in vols]


def which(vols, page):
    for idx, s, e in vols:
        if s <= page <= e:
            return idx
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vol", type=int)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()

    if not os.path.exists(LEDGER):
        print("没有 checks.csv")
        return
    vols = volumes()
    rows = [r for r in csv.DictReader(open(LEDGER, encoding="utf-8"))
            if "[cover]" in (r.get("note") or "")]
    if a.vol:
        rows = [r for r in rows if which(vols, int(r["page"] or 0)) == a.vol]

    cnt = {}
    for r in rows:
        v = which(vols, int(r["page"] or 0))
        cnt[v] = cnt.get(v, 0) + 1
    print(f"待核验（cover）总数: {len(rows)}")
    print("按册:", {k: cnt[k] for k in sorted(cnt)})
    if a.limit:
        print(f"\n前 {a.limit} 个：")
        for r in rows[: a.limit]:
            print(f"  q{r['q']:>5s}  page={r['page']:>5s}  注: {(r.get('note') or '')[:40]}")
    else:
        print("\n加 --limit N 输出具体题号；核验后改判走 work/verify/rerecord.py。")
    print("\n阶段二结束标志：本命令输出 0 条，且 ledger_audit.py 三类告警为 0。")


if __name__ == "__main__":
    main()
