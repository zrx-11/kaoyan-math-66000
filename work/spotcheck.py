# -*- coding: utf-8 -*-
"""抽检台账与看板。

用法：
  python3 work/spotcheck.py            # 生成看板 work/spotcheck.md，并把台账里判 fail 的题写入 fixlist
  python3 work/spotcheck.py --round 2  # 生成第 2 轮看板（每轮推进 50 题窗口）

台账 work/checks.csv 字段：q,page,verdict,note,time
verdict 取值：pass（题干与答案均正确）、fixed（我改过）、fail（需返工）、skip（无题干/书印问题已写校勘）
"""
import csv
import glob
import json
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAG = f"{ROOT}/work/fragments"
MAP = f"{ROOT}/work/manifest/jixian_map.json"
LEDGER = f"{ROOT}/work/checks.csv"
BOARD = f"{ROOT}/work/spotcheck.md"
FIX = f"{ROOT}/work/fixlist.json"

ART_RE = re.compile(r'<article class="q" id="q(\d+)"[^>]*>', re.S)


def load_cards():
    nums, pages = {}, {}
    for f in sorted(glob.glob(os.path.join(FRAG, "**", "*.html"), recursive=True)):
        s = open(f, encoding="utf-8").read()
        for m in ART_RE.finditer(s):
            n = int(m.group(1))
            nums[n] = os.path.basename(f)
            q = re.search(r'class="qsrc"[^>]*>\s*(P?\d{3,5})', s[m.start():m.start() + 400])
            if q:
                pages[n] = q.group(1).lstrip("P")
    return nums, pages


def main():
    round_no = 1
    if "--round" in sys.argv:
        round_no = int(sys.argv[sys.argv.index("--round") + 1])
    nums, pages = load_cards()
    try:
        q2p = {int(k): int(v) for k, v in json.load(open(MAP, encoding="utf-8"))["q2p"].items()}
    except Exception:
        q2p = {}

    done = {}
    if os.path.exists(LEDGER):
        for row in csv.DictReader(open(LEDGER, encoding="utf-8")):
            try:
                done[int(row["q"])] = row
            except Exception:
                pass

    # 选题：每轮覆盖 3 个窗口（轮次滚动），每窗口 4 题：2 张可疑 + 2 张随机
    hi = max(nums) if nums else 0
    windows = []
    for w in range(3):
        start = ((round_no - 1) * 3 + w) * 100
        win = [n for n in nums if start <= n < start + 100]
        if win:
            windows.append((start, win))
    plan = []
    for start, win in windows:
        random.seed(round_no * 1000 + start)
        pick = []
        # 可疑优先：含七阶、含参反求、书答案存疑关键词
        for n in win:
            body = ""
            for f in glob.glob(os.path.join(FRAG, "**", "*.html"), recursive=True):
                s = open(f, encoding="utf-8").read()
                m = re.search(r'<article class="q" id="q%d"[^>]*>(.*?)</article>' % n, s, re.S)
                if m:
                    body = m.group(1)
                    break
            if any(k in body for k in ["七阶", "反求", "校勘", "存疑", "待定"]):
                pick.append(n)
            if len(pick) >= 2:
                break
        pick += random.sample(win, min(4, len(win)))
        plan.append((start, sorted(set(pick))[:4]))

    lines = [f"# 第 {round_no} 轮抽检看板", "",
             "规则：逐题打开页面图比对题干与答案；解析要能自洽复算。判 pass / fixed / fail / skip。",
             "结果写回 work/checks.csv，然后跑 `python3 work/spotcheck.py` 刷新看板与返工清单。", ""]
    for start, ps in plan:
        lines.append(f"## 窗口 {start}–{start+99}")
        for n in ps:
            pg = pages.get(n, q2p.get(n, "?"))
            st = done.get(n, {}).get("verdict", "待核")
            note = done.get(n, {}).get("note", "")
            lines.append(f"- [ ] 第 {n} 题（P{pg}）　状态：**{st}**{'　' + note if note else ''}")
        lines.append("")
    open(BOARD, "w", encoding="utf-8").write("\n".join(lines))

    fail = [n for n, r in done.items() if r.get("verdict") == "fail"]
    json.dump(sorted(fail), open(FIX, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"round={round_no} cards={len(nums)} checked={len(done)} fail={len(fail)} board={BOARD}")


if __name__ == "__main__":
    main()
