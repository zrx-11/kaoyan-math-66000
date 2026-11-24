# -*- coding: utf-8 -*-
"""抽检工序：自动找「可疑卡」+ 生成抽样计划 + 维护检查台账。

三类自动可疑判定：
1. 答案与推导不一致：答案栏的数值，在解析里找不到同值结论（653 题就是这种）。
2. 题干页码错位：卡片标注的 qsrc 页码与该题号在 jixian_map 中的页码相差超过 2 页。
3. 解析高度雷同：不同题号的解析文本相似度 > 0.8，疑似套模板复制。

输出：
- work/audit-report.md   可疑清单 + 抽样建议
- work/checks.csv        台账（q,page,verdict,note,time），人工核对后写回
"""
import csv
import difflib
import glob
import json
import os
import random
import re
import sys

ROOT = "/home/user/Doubao/chats/38454435152889602"
FRAG = f"{ROOT}/work/fragments"
MAP = f"{ROOT}/work/manifest/jixian_map.json"
LEDGER = f"{ROOT}/work/checks.csv"
OUT = f"{ROOT}/work/audit-report.md"

ART_RE = re.compile(r'<article class="q" id="q(\d+)"[^>]*>(.*?)</article>', re.S)
PAGE_RE = re.compile(r'第?P?(\d{3,5})')


def plain(h):
    t = re.sub(r"<[^>]+>", "", h)
    t = re.sub(r"\\[a-zA-Z]+", "", t)
    return re.sub(r"\s+", "", t)


def norm_num(s):
    """把 1/3、−1/30、0.5 之类归一成字符串便于比较。"""
    for _ in range(3):
        s = re.sub(r"\\?[dt]?frac\{([^{}]*)\}\{([^{}]*)\}", r"\1/\2", s)
    s = re.sub(r"\\[()\[\]]", "", s)
    s = s.replace("\\dfrac", "").replace("\\frac", "").replace("\\tfrac", "")
    s = s.replace("\\left", "").replace("\\right", "").replace("\\,", "")
    s = s.replace("\\!", "").replace("$", "").replace("−", "-").replace("－", "-")
    s = re.sub(r"\\+", "", s)
    s = s.replace("{", "").replace("}", "").replace("^", "")
    s = s.strip("()（） ")
    m = re.fullmatch(r"-?\d+/-?\d+", s)
    if m:
        a, b = s.split("/")
        try:
            v = float(a) / float(b)
            return f"{v:.6f}"
        except Exception:
            return s
    m = re.fullmatch(r"-?\d+(\.\d+)?", s)
    if m:
        try:
            return f"{float(s):.6f}"
        except Exception:
            return s
    return s


def answer_of(body):
    m = re.search(r'<div class="answer">(.*?)</div>', body, re.S)
    if not m:
        return ""
    raw = re.sub(r"\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}", r"\1/\2", m.group(1))
    t = plain(raw)
    t = re.sub(r"^答案[：:]*", "", t)
    t = t.replace("\\(", "").replace("\\)", "")
    t = re.sub(r"^\\?[{}]", "", t)
    return t.strip()


def sol_of(body):
    m = re.search(r'<div class="block sol">(.*?)</div>\s*(?:<div class="block|<div class="var|</article>|$)', body, re.S)
    if m:
        return m.group(1)
    i = body.find('class="block sol"')
    return body[i:] if i >= 0 else ""


def claimed_results(sol):
    """从解析里抽出所有形如「为 X」「= X」「\to X」的结果值。"""
    cands = set()
    for pat in [r"极限为\s*(?:\\\(|\\\()?([^，。；\)\s]{1,18})",
                r"\\to\s*(?:\\dfrac|-\s*\\dfrac|\d|\\infty|\\infinity)[^\\\s，。]{0,18}",
                r"=\s*(?:\\dfrac\{[^}]*\}\{[^}]*\}|-?\d+(?:/\d+)?)"]:
        for m in re.finditer(pat, sol):
            cands.add(m.group(1) if m.lastindex else m.group(0))
    out = set()
    for c in cands:
        c = re.sub(r"^=\s*", "", c)
        out.add(norm_num(c))
    return out


def main():
    try:
        q2p = {int(k): v for k, v in json.load(open(MAP, encoding="utf-8"))["q2p"].items()}
    except Exception:
        q2p = {}
    cards, owner = {}, {}
    for f in sorted(glob.glob(os.path.join(FRAG, "**", "*.html"), recursive=True)):
        s = open(f, encoding="utf-8").read()
        for m in ART_RE.finditer(s):
            n = int(m.group(1))
            if n in cards and len(m.group(2)) <= len(cards[n]):
                continue
            cards[n] = m.group(2)
            owner[n] = os.path.basename(f)

    sus = {"ans_mismatch": [], "page_shift": [], "templated": []}
    for n, body in cards.items():
        a = norm_num(answer_of(body))
        if a and re.fullmatch(r"-?\d+(\.\d+)?", a):
            sol = sol_of(body)
            if sol and a not in claimed_results(sol):
                sus["ans_mismatch"].append((n, answer_of(body), owner[n]))
        if n in q2p:
            m = re.search(r'class="qsrc"[^>]*>\s*P?(\d{3,5})', body)
            if m:
                d = abs(int(m.group(1)) - int(q2p[n]))
                if d > 2:
                    sus["page_shift"].append((n, int(m.group(1)), int(q2p[n]), owner[n]))

    # 雷同检测：先按答案分组，只在同答案组内两两比，避免 O(n²) 爆掉
    by_ans = {}
    for n, body in cards.items():
        by_ans.setdefault(norm_num(answer_of(body)), []).append(n)
    for ans, ns in by_ans.items():
        if len(ns) < 2 or len(ns) > 400:
            continue
        texts = {n: plain(sol_of(cards[n]))[:800] for n in ns}
        for i in range(len(ns)):
            for j in range(i + 1, min(len(ns), i + 6)):
                a, b = ns[i], ns[j]
                if len(texts[a]) < 200 or len(texts[b]) < 200:
                    continue
                r = difflib.SequenceMatcher(None, texts[a], texts[b]).quick_ratio()
                if r > 0.8:
                    sus["templated"].append((a, b, round(r, 2)))

    # 抽样：按 50 题一个窗口抽 5 题，优先可疑卡
    nums = sorted(cards)
    plan = []
    for start in range(0, max(nums) + 1, 50):
        win = [n for n in nums if start <= n < start + 50]
        if not win:
            continue
        pick = [n for n in win if any(n in [x[0] for x in v] for v in sus.values())][:3]
        random.seed(start)
        pick += random.sample(win, min(5, len(win)))
        plan.append((f"{start}-{start+49}", sorted(set(pick))[:6]))

    done = 0
    if os.path.exists(LEDGER):
        done = sum(1 for _ in open(LEDGER, encoding="utf-8")) - 1
    lines = ["# 抽检报告", "",
             f"- 卡片：{len(cards)}　台账已核：{done}",
             f"- 可疑：答案与推导不一致 {len(sus['ans_mismatch'])}　页码错位 {len(sus['page_shift'])}　解析雷同 {len(sus['templated'])}",
             "", "## 一、答案与推导不一致（优先复核）"]
    if sus["ans_mismatch"]:
        for n, a, f in sus["ans_mismatch"][:40]:
            lines.append(f"- 第 {n} 题：答案栏 `{a}`，解析里没有同值结论（{f}）")
    else:
        lines.append("- 无")
    lines += ["", "## 二、题干页码错位（可能读错页）"]
    if sus["page_shift"]:
        for n, got, exp, f in sus["page_shift"][:40]:
            lines.append(f"- 第 {n} 题：卡片标 P{got}，映射应为 P{exp}（{f}）")
    else:
        lines.append("- 无")
    lines += ["", "## 三、解析雷同（疑似套模板）"]
    if sus["templated"]:
        for a, b, r in sus["templated"][:40]:
            lines.append(f"- 第 {a} 题 与 第 {b} 题 相似度 {r}")
    else:
        lines.append("- 无")
    lines += ["", "## 四、抽样计划（每 50 题一组，可疑优先）"]
    for w, ps in plan[:60]:
        lines.append(f"- {w}：{('、'.join('第%d题' % p for p in ps)) or '—'}")
    open(OUT, "w", encoding="utf-8").write("\n".join(lines))

    if not os.path.exists(LEDGER):
        with open(LEDGER, "w", newline="", encoding="utf-8") as fp:
            csv.writer(fp).writerow(["q", "page", "verdict", "note", "time"])
    print(f"cards={len(cards)} ans_mismatch={len(sus['ans_mismatch'])} "
          f"page_shift={len(sus['page_shift'])} templated={len(sus['templated'])} ledger={done}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
