# -*- coding: utf-8 -*-
"""阶段一（覆盖优先）闸门：只查「结构残废」，不查数值对错。

与 work/gate_one.py 的区别：
    gate_one.py  = 精核口径（六块齐全 + 篇幅 301–420 + 整卡 ≥620 + 严格题号区间）
    gate_lite.py = 覆盖口径（六块齐全 + sol ≥150 + 公式 ≥1 + 无禁词 + 答案非空）

用法：
    python3 work/qa/gate_lite.py <分片文件或目录> [起题号 止题号]

输出每张卡的 FAIL 原因；结尾给通过率。阶段一不过关的卡不许进站点。
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# id 允许草稿占位（qTMP / 任意非空串）：并行生产时子智能体不编号，装配后再分配 qN
ART_RE = re.compile(r'<article class="q" id="q([0-9A-Za-z_-]+)".*?</article>', re.S)
QNO_RE = re.compile(r'class="qno">第\s*(\d+)\s*题')
ANS_RE = re.compile(r'<div class="answer">(.*?)</div>', re.S)
SOL_RE = re.compile(r'<div class="block sol">(.*?)(?=<div class="block (?:pit|trend|var|caveat)">|</article>)', re.S)
BAN = ["核对：", "略去", "待补"]
EMPTY_ANS = ["待补充", "见解析", "略", "略。"]


def plain(html):
    html = re.sub(r"\\[\[\]()]", "", html)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html).strip()


def check(body):
    fails = []
    if 'class="stem"' not in body:
        fails.append("缺 stem")
    a = ANS_RE.search(body)
    if not a:
        fails.append("缺 answer")
    else:
        txt = plain(a.group(1)).replace("答案：", "").strip()
        if not txt:
            fails.append("答案为空")
        for e in EMPTY_ANS:
            if txt.startswith(e):
                fails.append(f"答案占位：{e}")
    for cls, label in (("sol", "解析"), ("pit", "易错点"), ("trend", "考向"), ("var", "变式")):
        if f'class="block {cls}"' not in body:
            fails.append(f"缺 {label}")
    s = SOL_RE.search(body)
    if s:
        n = len(plain(s.group(0)))
        if n < 150:
            fails.append(f"sol 仅 {n} 字（阶段一下限 150）")
        if body.count("<p>") < 2:
            fails.append("sol 只有一段")
    if r"\[" not in body:
        fails.append("无行间公式")
    if 'class="var-ans"' not in body:
        fails.append("变式缺 var-ans")
    for b in BAN:
        if b in body:
            fails.append(f"命中禁词「{b}」")
    return fails


def walk(targets):
    for t in targets:
        if os.path.isdir(t):
            for f in sorted(glob.glob(os.path.join(t, "*.html"))):
                if not f.endswith(".bak"):
                    yield f
        else:
            yield t


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    lo = int(args[1]) if len(args) > 2 else None
    hi = int(args[2]) if len(args) > 2 else None

    total = bad = 0
    ids = set()
    for f in walk(args[:1]):
        txt = open(f, encoding="utf-8", errors="replace").read()
        for m in ART_RE.finditer(txt):
            raw = m.group(1)
            # 草稿占位 id（qTMP）不参与题号区间筛选与查重
            q = int(raw) if raw.isdigit() else None
            if q is not None and lo and q < lo:
                continue
            if q is not None and hi and q > hi:
                continue
            total += 1
            if q is not None and q in ids:
                print(f"FAIL q{q}  id 重复（同批次内）")
                bad += 1
                continue
            if q is not None:
                ids.add(q)
            fails = check(m.group(0))
            if QNO_RE.search(m.group(0)) is None:
                fails.append("缺 qno")
            if fails:
                bad += 1
                print(f"FAIL q{q}  " + "；".join(fails[:4]) + (f"（另{len(fails)-4}项）" if len(fails) > 4 else ""))

    ok = total - bad
    print(f"\n{'='*40}\ncards={total}  pass={ok}  fail={bad}")
    if total:
        print(f"通过率 {ok/total*100:.1f}%")
    print("阶段一通过 ≠ 内容正确：数值仍需阶段二逐题复算。")
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
