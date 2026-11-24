# -*- coding: utf-8 -*-
"""单分片自检（无副作用，可并行跑）。

用法：python3 work/gate_one.py <分片绝对路径> [期望起始题号] [期望结束题号]
退出码 0 = 通过，1 = 有缺陷。
判定口径与 work/gate.py 一致，另加：题号连续、题号区间校验、六块齐全。
"""
import re
import sys

BLOCKS = ["sol", "pit", "trend", "var"]
MIN_TEXT = 520
BANNED = ["核对：", "？核对", "待核", "此处略", "自行补充", "TODO", "略去",
          "过程略", "略繁琐", "以书上答案为准", "存疑", "待补"]
ART_RE = re.compile(r'<article class="q" id="q(\d+)"[^>]*>(.*?)</article>', re.S)


def plain(html):
    t = re.sub(r"<[^>]+>", "", html)
    t = re.sub(r"\\[a-zA-Z]+", "", t)
    t = re.sub(r"[\\${}^_]", "", t)
    return re.sub(r"\s+", "", t)


def check(n, body):
    bad = []
    for tag in BLOCKS:
        if f'class="block {tag}"' not in body:
            bad.append(f"缺{tag}")
    if 'class="stem"' not in body:
        bad.append("缺题干")
    if 'class="answer"' not in body:
        bad.append("缺答案")
    for a, b in [("\\(", "\\)"), ("\\[", "\\]")]:
        if body.count(a) != body.count(b):
            bad.append(f"{a}{b}不配对")
    for w in BANNED:
        if w in body:
            bad.append(f"禁用「{w}」")
    if len(plain(body)) < MIN_TEXT:
        bad.append(f"篇幅{len(plain(body))}字")
    # 变式必须有答案
    if 'class="block var"' in body and 'var-ans' not in body:
        bad.append("变式缺答案")
    return bad


def main():
    if len(sys.argv) < 2:
        print("用法: python3 gate_one.py <file> [startq] [endq]")
        return 1
    path = sys.argv[1]
    start = int(sys.argv[2]) if len(sys.argv) > 2 else None
    end = int(sys.argv[3]) if len(sys.argv) > 3 else None
    s = open(path, encoding="utf-8").read()
    if "<html" in s.lower() or "<body" in s.lower():
        print("FAIL 含 html/body 外壳")
        return 1
    arts = ART_RE.findall(s)
    ids = [int(a[0]) for a in arts]
    probs = []
    if len(ids) != len(set(ids)):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        probs.append(f"重复题号 {dup}")
    if ids != sorted(ids):
        probs.append("题号非递增")
    if ids and ids != list(range(ids[0], ids[0] + len(ids))):
        gaps = [i for i in range(ids[0], ids[-1] + 1) if i not in set(ids)]
        probs.append(f"题号不连续，缺 {gaps[:10]}")
    if start and ids and ids[0] != start:
        probs.append(f"起始题号 {ids[0]} != {start}")
    if end and ids and ids[-1] != end:
        probs.append(f"结束题号 {ids[-1]} != {end}")
    for a in arts:
        b = check(int(a[0]), a[1])
        if b:
            probs.append(f"第{a[0]}题：" + "；".join(b))
    if probs:
        print(f"FAIL cards={len(ids)}")
        for p in probs[:40]:
            print("  -", p)
        return 1
    print(f"OK cards={len(ids)} range={ids[0]}-{ids[-1]} min_plain={min(len(plain(a[1])) for a in arts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
