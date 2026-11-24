# -*- coding: utf-8 -*-
"""四张目标卡的真实 sol 边界统计 + 整卡 plain + 公式处数 + 未改块核对。"""
import re, sys

def plain(html):
    t = re.sub(r"<[^>]+>", "", html)
    t = re.sub(r"\\[a-zA-Z]+", "", t)
    t = re.sub(r"[\\${}^_]", "", t)
    return re.sub(r"\s+", "", t)

ART_RE = re.compile(r'<article class="q" id="q(\d+)"[^>]*>(.*?)</article>', re.S)
SOL_RE = re.compile(r'<div class="block sol">(.*?)</div>\s*(?=<div class="block )', re.S)

files = {
    "q1": "/home/user/Doubao/chats/38454435152889602/work/fragments/02-gaoshu-15000/t01/seg-590-591.html",
    "q343": "/home/user/Doubao/chats/38454435152889602/work/fragments/02-gaoshu-15000/t01/seg-654-662.html",
    "q352": "/home/user/Doubao/chats/38454435152889602/work/fragments/02-gaoshu-15000/t01/seg-662-670.html",
    "q373": "/home/user/Doubao/chats/38454435152889602/work/fragments/02-gaoshu-15000/t01/seg-662-670.html",
}

targets = ["q1", "q343", "q352", "q373"]
arts = {}
for f in set(files.values()):
    s = open(f, encoding="utf-8").read()
    for qid, body in ART_RE.findall(s):
        arts["q" + qid] = body

for t in targets:
    body = arts[t]
    m = SOL_RE.search(body)
    sol = m.group(1) if m else ""
    sol_n = len(plain(sol))
    card_n = len(plain(body))
    eq = sol.count("\\[")
    ans = re.search(r'<div class="answer">(.*?)</div>', body, re.S).group(1)
    print(f"{t}: sol_plain={sol_n}  card_plain={card_n}  display_math={eq}  answer={plain(ans)}")
    # 未改块存在性核对
    for blk in ["stem", "answer", "pit", "trend", "var"]:
        print(f"    block {blk}: {'OK' if f'class=\"block {blk}\"' in body or blk=='stem' else 'MISSING'}")
    if t == "q343":
        cav = re.search(r'<div class="block caveat">(.*?)</div>\s*<div class="block pit">', body, re.S)
        print("    caveat 保留:", "OK" if cav and "书给答案" in cav.group(1) else "CHECK")
