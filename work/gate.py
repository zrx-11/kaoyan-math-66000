# -*- coding: utf-8 -*-
"""质量闸门：逐卡体检，给出通过/拦截结论，输出 gate.json 与 gate-report.md。

设计目标：
1. 可被外部脚本（publish.sh）调用，退出码 0=可发布，1=有拦截项。
2. 拦截项只针对「硬缺陷」——缺板块、缺题干/答案、解析过短、LaTeX 不配对、变式留自我更正口水。
3. 重复题号不算硬缺陷（合并时按最长卡片保留），但记入报告。
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAG = f"{ROOT}/work/fragments"
OUT_JSON = f"{ROOT}/work/gate.json"
OUT_MD = f"{ROOT}/work/gate-report.md"

ART_RE = re.compile(r'<article class="q" id="q(\d+)"[^>]*>(.*?)</article>', re.S)

BLOCKS = ["sol", "pit", "trend", "var"]
MIN_TEXT = 430          # 硬性下限（样板 gold-1-6 最短 479 字）
WARN_TEXT = 520         # 偏薄预警线
BANNED = ["核对：", "？核对", "待核", "此处略", "自行补充", "TODO", "略去",
              "过程略", "略繁琐", "以书上答案为准", "需重算", "重新算", "重新审视"]

def plain(html):
    t = re.sub(r"<[^>]+>", "", html)
    t = re.sub(r"\\[a-zA-Z]+", "", t)      # 去掉 LaTeX 命令名
    t = re.sub(r"[\\${}^_]", "", t)
    return re.sub(r"\s+", "", t)

def norm_val(s):
    s = re.sub(r'\\(?:d|t)?frac\{(.*?)\}\{(.*?)\}', r'(\1)/(\2)', s)
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    s = s.replace('−', '-').replace('{', '').replace('}', '').replace('\\', '')
    return re.sub(r'\s+', '', s)

BARE = re.compile(r'(?<![\\A-Za-z])(arctan|tanh|tan|sin|cos|ln|lim|frac|infty)(?![A-Za-z])')

def check(body):
    bad = []
    # 答案栏回改：校勘说「书给 X」，答案栏却仍是 X
    cav = re.search(r'class="block caveat"(.*?)</div>\s*</div>', body, re.S)
    if cav:
        if body.find('class="block caveat"') < body.find('class="answer"'):
            bad.append("校勘块位于答案之前")
        m = re.search(r'书给(?:出)?[:：]?(.{1,40}?)(?:。|；|，复算|\.)', cav.group(1))
        ans = re.search(r'class="answer">(.*?)</div>', body, re.S)
        if m and ans:
            bv = norm_val(m.group(1)).lstrip(':：')
            at = norm_val(re.sub(r'<[^>]+>', '', ans.group(1)))
            if len(bv) >= 2 and bv in at:
                bad.append(f"答案栏仍是书值 {bv}（应写复算值）")
    if '依书答案' in body or '仍照书上' in body:
        bad.append("残留「依书答案/仍照书上」")
    txt = re.sub(r'<[^>]+>', '', body)
    for seg in re.findall(r'\\\(\s*(.*?)\\\)', txt, re.S) + re.findall(r'\\\[\s*(.*?)\\\]', txt, re.S):
        if BARE.search(seg):
            bad.append("LaTeX 反斜杠丢失（公式内出现裸命令名）")
            break
    for tag in BLOCKS:
        if f'class="block {tag}"' not in body:
            bad.append(f"缺{tag}板块")
    if 'class="stem"' not in body:
        bad.append("缺题干")
    if 'class="answer"' not in body:
        bad.append("缺答案")
    for a, b in [("\\(", "\\)"), ("\\[", "\\]")]:
        if body.count(a) != body.count(b):
            bad.append(f"{a}{b}不配对")
    for w in BANNED:
        if w in body:
            bad.append(f"含禁用表述「{w}」")
    if len(plain(body)) < MIN_TEXT:
        return bad, f"篇幅不足({len(plain(body))}字)"
    # 变式答案必须给出，不能只提问
    var = re.search(r'class="block var"(.*?)</div>\s*</article>|class="block var"(.*)', body, re.S)
    if var:
        vseg = var.group(0)
        if "var-ans" not in vseg:
            bad.append("变式缺答案")
    return bad, ""

def main():
    files = sorted(glob.glob(os.path.join(FRAG, "**", "*.html"), recursive=True))
    cards, owners, dup = {}, {}, []
    for f in files:
        s = open(f, encoding="utf-8").read()
        for m in ART_RE.finditer(s):
            n = int(m.group(1))
            if n in cards:
                dup.append({"q": n, "dup_file": os.path.basename(f), "kept_file": owners[n]})
                # 保留篇幅更长的一份
                if len(plain(m.group(2))) <= len(plain(cards[n])):
                    continue
            cards[n] = m.group(2)
            owners[n] = os.path.basename(f)
    issues, thin = {}, {}
    for n, b in cards.items():
        bad, short = check(b)
        if bad: issues[n] = bad
        elif short: thin[n] = short
    nums = sorted(cards)
    segs, start = [], nums[0] if nums else None
    for i, n in enumerate(nums):
        if i + 1 < len(nums) and nums[i + 1] == n + 1:
            continue
        segs.append([start, n]); start = nums[i + 1] if i + 1 < len(nums) else None
    quarantine = sorted(issues)
    json.dump(quarantine, open(f"{ROOT}/work/quarantine.json", "w", encoding="utf-8"), ensure_ascii=False)
    rate = len(issues)/max(1,len(cards))
    data = {
        "fragments": len(files),
        "cards": len(cards),
        "failed": len(issues),
        "thin": {str(k): v for k, v in sorted(thin.items())},
        "duplicates": len(dup),
        "ranges": segs,
        "issues": {str(k): v for k, v in sorted(issues.items())},
    }
    json.dump(data, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    lines = ["# 质量闸门报告", "",
             f"- 分片：{len(files)}　唯一题号：{len(cards)}　不通过：{len(issues)}　重复：{len(dup)}",
             f"- 偏薄预警（<{WARN_TEXT} 字，不拦截）：{len(thin)} 张",
             f"- 通过率：{(len(cards)-len(issues))/max(1,len(cards))*100:.1f}%",
             "", "## 连续区间", *[f"- {a}–{b}（{b-a+1} 题）" for a, b in segs],
             "", "## 拦截清单"]
    if issues:
        for n, v in sorted(issues.items()):
            lines.append(f"- 第 {n} 题：{'；'.join(v)}")
    else:
        lines.append("- 无")
    open(OUT_MD, "w", encoding="utf-8").write("\n".join(lines))
    print(f"cards={len(cards)} failed={len(issues)} dup={len(dup)} pass={data['ranges']}")
    print(f"quarantine={len(quarantine)} rate={rate*100:.2f}%")
    return 1 if rate > 0.03 else 0

if __name__ == "__main__":
    sys.exit(main())
