# -*- coding: utf-8 -*-
"""只统计每张卡 sol 块的 plain 字数（口径同 gate_one.plain），不修改任何文件。"""
import re, sys

def plain(html):
    t = re.sub(r"<[^>]+>", "", html)
    t = re.sub(r"\\[a-zA-Z]+", "", t)
    t = re.sub(r"[\\${}^_]", "", t)
    return re.sub(r"\s+", "", t)

ART_RE = re.compile(r'<article class="q" id="q(\d+)"[^>]*>(.*?)</article>', re.S)
SOL_RE = re.compile(r'<div class="block sol">(.*?)</div>\s*<div class="block pit">', re.S)

for path in sys.argv[1:]:
    s = open(path, encoding="utf-8").read()
    print("==", path.split("/")[-1])
    for qid, body in ART_RE.findall(s):
        m = SOL_RE.search(body)
        n = len(plain(m.group(1))) if m else -1
        flag = " <<<" if n < 310 or n > 440 else ""
        print(f"  q{qid}: sol={n}{flag}")
