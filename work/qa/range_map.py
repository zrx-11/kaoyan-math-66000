# -*- coding: utf-8 -*-
"""题号 → 承载文件映射（派活前必跑，防止两段共享同一文件导致写回覆盖）。

用法：
    python3 work/qa/range_map.py 1401 1500
    python3 work/qa/range_map.py 2851 2900

输出：每个分片文件在该区间里承载的题号（压缩成区间串）、张数、
以及「同一题出现在多个文件」的重号清单。

注意：分片文件名是页段（seg-起页-止页），不是题号段，两者不成线性关系；
同一题号可能有旧副本，派活必须按**文件**边界切，而不是按题号边界切。
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRAG = os.path.join(ROOT, "work", "fragments")
ART_RE = re.compile(r'<article class="q" id="q(\d+)"')


def compress(nums):
    nums = sorted(set(nums))
    out = []
    i = 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f"{nums[i]}-{nums[j]}")
        i = j + 1
    return ", ".join(out)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    rows = []
    owner = {}
    for f in sorted(glob.glob(os.path.join(FRAG, "**", "*.html"), recursive=True)):
        if f.endswith(".bak"):
            continue
        txt = open(f, encoding="utf-8", errors="replace").read()
        qs = [int(m.group(1)) for m in ART_RE.finditer(txt) if lo <= int(m.group(1)) <= hi]
        if not qs:
            continue
        rel = os.path.relpath(f, ROOT)
        rows.append((rel, sorted(set(qs))))
        for q in set(qs):
            owner.setdefault(q, []).append(rel)

    if not rows:
        print(f"{lo}-{hi} 区间内没有任何卡片。")
        return

    print(f"区间 {lo}-{hi} 的承载文件：\n")
    for rel, qs in rows:
        print(f"  {rel}\n     {len(qs)} 张  {compress(qs)}")

    dup = {q: fs for q, fs in owner.items() if len(fs) > 1}
    covered = sorted(owner)
    print(f"\n覆盖 {len(covered)} 张" + (f"，缺口 {sorted(set(range(lo, hi+1)) - set(covered))}" if set(range(lo, hi+1)) - set(covered) else "，区间完整"))
    if dup:
        print(f"\n重号 {len(dup)} 个（同题多份，站点取 article 更长者）：")
        for q in sorted(dup)[:30]:
            print(f"  q{q}: {dup[q]}")
        if len(dup) > 30:
            print(f"  …另 {len(dup)-30} 个")
    else:
        print("\n无重号。")


if __name__ == "__main__":
    main()
