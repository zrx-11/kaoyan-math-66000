# -*- coding: utf-8 -*-
"""台账与卡片的一致性审计（只读，绝不写 checks.csv）。

核心口径：**fixed ⇔ caveat**（两向都要核）。四类已知的账实不符：

  1) 记 fixed 却无校勘块      —— 多为「纯变式修正 / 排版修复」被误记成书错
  2) 带校勘块却记 pass        —— 书答确实错了、卡也给了复算值，但台账没升档
  3) 带校勘块却记 skip        —— 卡内容是对的，判档错了（skip 必须无块）
  4) 变式答案栏自误被记 fixed —— 变式 var-ans 与自身解析不一致，被当成书错（本书最高频记账错）

用法：
    python3 work/qa/ledger_audit.py             # 全量
    python3 work/qa/ledger_audit.py 1401 1500   # 只看某区间
"""
import csv
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRAG = os.path.join(ROOT, "work", "fragments")
LEDGER = os.path.join(ROOT, "work", "checks.csv")

ART_RE = re.compile(r'<article class="q" id="q(\d+)".*?</article>', re.S)
CAVEAT_RE = re.compile(r'class="block caveat"')


def load_cards(lo=None, hi=None):
    """按「同目录内 article 更长者胜」取生效份，返回 {q: article_html}。"""
    cards = {}
    for f in sorted(glob.glob(os.path.join(FRAG, "**", "*.html"), recursive=True)):
        if f.endswith(".bak") or "-final" in os.path.basename(f):
            continue
        txt = open(f, encoding="utf-8", errors="replace").read()
        for m in ART_RE.finditer(txt):
            q = int(m.group(1))
            if lo and q < lo:
                continue
            if hi and q > hi:
                continue
            body = m.group(0)
            if q in cards and len(body) <= len(cards[q]):
                continue
            cards[q] = body
    return cards


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 2 else None
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else None

    verdict = {}
    for r in csv.DictReader(open(LEDGER, encoding="utf-8")):
        q = int(r["q"])
        if lo and q < lo:
            continue
        if hi and q > hi:
            continue
        verdict[q] = r["verdict"]

    cards = load_cards(lo, hi)

    fixed_no_block, block_not_fixed, skip_with_block, no_card = [], [], [], []
    for q, v in sorted(verdict.items()):
        body = cards.get(q)
        if body is None:
            no_card.append(q)
            continue
        has = bool(CAVEAT_RE.search(body))
        if v == "fixed" and not has:
            fixed_no_block.append(q)
        elif v != "fixed" and has:
            (skip_with_block if v == "skip" else block_not_fixed).append(q)

    no_ledger = sorted(set(cards) - set(verdict))

    def show(name, arr, hint):
        print(f"\n[{'!' if arr else 'ok'}] {name}: {len(arr)} 张")
        if arr:
            print("    ", arr[:40], "…" if len(arr) > 40 else "")
            print("   →", hint)

    print(f"区间 {'全量' if lo is None else f'{lo}-{hi}'}：台账 {len(verdict)} 行，卡片 {len(cards)} 张")
    print("verdict 分布:", {k: list(verdict.values()).count(k) for k in ("pass", "fixed", "skip", "fail")})
    show("记 fixed 却无校勘块", fixed_no_block, "多为纯变式/排版修复误记，改回 pass 并把 note 写清")
    show("带校勘块却记 pass", block_not_fixed, "书答确实错了就升 fixed；块本身写错则改块")
    show("带校勘块却记 skip", skip_with_block, "skip 必须无块：题面完整就转 fixed，题面不可用就删块")
    show("有账无卡", no_card, "台账指向的卡片不存在，查是否被隔离/删卡")
    show("有卡无账", no_ledger, "新增卡未记账，补跑核实后入账")
    print("\n提示：变式自误要单独看——这类块里通常写的是变式值，不是书印值。"
          "判据是「书给」只认页面图印值，绝不从答案栏或 caveat 正文反抄。")


if __name__ == "__main__":
    main()
