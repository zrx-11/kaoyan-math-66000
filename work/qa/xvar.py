#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨文件变式归一化查重（只读不改）。
与 work/qa/hygiene.py 共用同一套 norm_var 口径（去标签、去 LaTeX 命令、去数字、去标点），
在传入的全部文件之间两两比对，报告"归一化后全等"的变式组。

用法：
  python3 work/qa/xvar.py <文件1> [文件2 ...]
    例：python3 work/qa/xvar.py work/drafts/parts/tixing2-126-135.html work/drafts/parts/tixing2-136-145.part2.html
退出码：有碰撞返回 1，无碰撞返回 0。
"""
import re
import sys

ART_RE = re.compile(r'<article class="q" id="q[0-9A-Za-z_-]+".*?</article>', re.S)


def norm_var(txt):
    t = re.sub(r'<[^>]+>', '', txt)
    t = re.sub(r'\\[a-zA-Z]+', '', t)
    t = re.sub(r'[0-9.]+', '', t)
    t = re.sub(r'[\\${}^_()\[\]，。、；：,.;:!?？\s]', '', t)
    return t


def main(paths):
    seen = {}
    hits = 0
    total = 0
    for p in paths:
        s = open(p, encoding="utf-8").read()
        for i, a in enumerate(ART_RE.findall(s), 1):
            total += 1
            vm = re.search(r'<p><b>变式</b>(.*?)</p>', a, re.S)
            if not vm:
                print("NOVAR %s #%d 缺变式" % (p, i))
                hits += 1
                continue
            qsrc = re.search(r'<span class="qsrc">(.*?)</span>', a)
            qtype = re.search(r'<span class="qtype">(.*?)</span>', a)
            tag = "%s #%d [%s·%s]" % (p.split('/')[-1], i,
                                     qsrc.group(1) if qsrc else "?", qtype.group(1) if qtype else "?")
            k = norm_var(vm.group(1))
            if k in seen:
                print("XVAL %s 与 %s 归一化同构: %s" % (tag, seen[k], k[:46]))
                hits += 1
            else:
                seen[k] = tag
    print("\n跨文件变式查重：比对 %d 张，碰撞 %d 处" % (total, hits))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
