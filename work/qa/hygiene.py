#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分片卫生扫描（只读不改）：
- BANNED 禁词（work/gate.py 全表）
- 正文裸 < >（LaTeX 段内 < > 未写 \\lt{} / \\gt{}）
- <p> / </p> 配平、<div> / </div> 配平
- 危险换行 \\[4pt] 之类带尺寸的 \\[...]
- 六块齐、var-ans 齐
- 变式归一化同构（段内两两比对）
用法： python3 work/qa/hygiene.py <文件1> [文件2 ...]
"""
import re
import sys

BANNED = ["核对：", "？核对", "待核", "此处略", "自行补充", "TODO", "略去",
          "过程略", "略繁琐", "以书上答案为准", "需重算", "重新算", "重新审视", "待补"]

ART_RE = re.compile(r'<article class="q" id="q[0-9A-Za-z_-]+".*?</article>', re.S)


def norm_var(txt):
    t = re.sub(r'<[^>]+>', '', txt)
    t = re.sub(r'\\[a-zA-Z]+', '', t)
    t = re.sub(r'[0-9.]+', '', t)
    t = re.sub(r'[\\${}^_()\[\]，。、；：,.;:!?？\s]', '', t)
    return t


def main(paths):
    bad = 0
    vars_seen = {}
    for p in paths:
        s = open(p, encoding="utf-8").read()
        # 禁词
        for b in BANNED:
            if b in s:
                print("BAN %s: %s" % (p, b))
                bad += 1
        # 正文裸尖括号（先剥掉所有标签与 LaTeX 中合法的 \lt \gt 转义产物）
        text = re.sub(r'<[^>]*>', '\x00', s)
        text = text.replace('\\lt', '').replace('\\gt', '')
        hits = re.findall(r'[<>]', text)
        if hits:
            print("ANGLE %s: %d 处裸尖括号" % (p, len(hits)))
            bad += 1
        # 配平
        if s.count('<p>') + s.count('<p class=') != s.count('</p>'):
            print("PTAG %s: <p>=%d </p>=%d" % (p, s.count('<p>') + s.count('<p class='), s.count('</p>')))
            bad += 1
        if s.count('<div') != s.count('</div>'):
            print("DIV %s: <div=%d </div>=%d" % (p, s.count('<div'), s.count('</div>')))
            bad += 1
        m = re.findall(r'\\\\\[[^0-9]', s)
        if m:
            print("BRK %s: 带尺寸换行 %d 处" % (p, len(m)))
            bad += 1
        # 六块 + 变式
        arts = ART_RE.findall(s)
        for i, a in enumerate(arts, 1):
            for cls in ("stem", "sol", "pit", "trend", "var"):
                if 'class="%s"' % cls not in a and 'class="block %s"' % cls not in a:
                    print("BLOCK %s #%d 缺 %s" % (p, i, cls))
                    bad += 1
            if 'class="var-ans"' not in a:
                print("VARANS %s #%d 缺 var-ans" % (p, i))
                bad += 1
            vm = re.search(r'<p><b>变式</b>(.*?)</p>', a, re.S)
            if vm:
                k = norm_var(vm.group(1))
                if k in vars_seen:
                    print("DUPVAR %s #%d 与 %s 同构: %s" % (p, i, vars_seen[k], k[:40]))
                else:
                    vars_seen[k] = "%s#%d" % (p, i)
    print("\n卫生扫描结束：%d 处告警" % bad)
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
