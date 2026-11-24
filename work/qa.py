# -*- coding: utf-8 -*-
"""质检：统计卡片覆盖、重复 id、LaTeX 括号闭合、板块完整性。"""
import glob
import json
import os
import re

ROOT = "/home/user/Doubao/chats/38454435152889602"
FRAG = f"{ROOT}/work/fragments"
OUT = f"{ROOT}/work/qa-report.md"

ART_RE = re.compile(r'<article class="q" id="q(\d+)".*?</article>', re.S)


def check_card(n, html):
    issues = []
    for tag in ["sol", "pit", "trend", "var"]:
        if f'class="block {tag}"' not in html:
            issues.append(f"缺 {tag} 板块")
    if 'class="answer"' not in html:
        issues.append("缺答案")
    if 'class="stem"' not in html:
        issues.append("缺题干")
    # LaTeX 括号配对
    for a, b in [("\\(", "\\)"), ("\\[", "\\]")]:
        if html.count(a) != html.count(b):
            issues.append(f"{a} 与 {b} 数量不等")
    # 字数
    text = re.sub(r"<[^>]+>", "", html)
    if len(text) < 260:
        issues.append(f"篇幅偏短（{len(text)} 字）")
    return issues


def main():
    files = sorted(glob.glob(os.path.join(FRAG, "**", "*.html"), recursive=True))
    cards, dup, issues = {}, [], {}
    for f in files:
        s = open(f, encoding="utf-8").read()
        for m in ART_RE.finditer(s):
            n = int(m.group(1))
            if n in cards:
                dup.append((n, os.path.basename(f)))
            cards[n] = m.group(0)
            iss = check_card(n, m.group(0))
            if iss:
                issues[n] = iss
    nums = sorted(cards)
    missing = [n for n in range(1, 2651) if n not in cards]
    # 连续段
    segs, start = [], None
    for i, n in enumerate(nums):
        if start is None:
            start = n
        if i + 1 < len(nums) and nums[i + 1] == n + 1:
            continue
        segs.append((start, n))
        start = None
    lines = ["# 质检报告", ""]
    lines.append(f"- 分片文件：{len(files)} 个")
    lines.append(f"- 卡片总数：{len(cards)}")
    lines.append(f"- 覆盖题号：{nums[0]}–{nums[-1]}" if nums else "- 无卡片")
    lines.append(f"- 重复 id：{'无' if not dup else dup}")
    lines.append(f"- 有问题的卡片：{len(issues)}")
    lines.append("")
    lines.append("## 已覆盖的连续区间")
    for s0, s1 in segs:
        lines.append(f"- {s0}–{s1}（{s1 - s0 + 1} 题）")
    lines.append("")
    lines.append("## 缺口（前 40 个未覆盖题号）")
    lines.append("- " + "、".join(map(str, missing[:40])))
    lines.append("")
    if issues:
        lines.append("## 问题清单")
        for n, iss in sorted(issues.items()):
            lines.append(f"- 第 {n} 题：{'；'.join(iss)}")
    open(OUT, "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines[:8]))
    print("saved", OUT)


if __name__ == "__main__":
    main()
