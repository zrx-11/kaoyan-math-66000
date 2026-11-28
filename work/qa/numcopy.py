#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把草稿占位 id（qTMP）顺序化成数字 id，仅供 plainlen.py / gate_lite.py 区间筛选用。
用法： python3 work/qa/numcopy.py <in.html> <out.html>
"""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
n = [0]


def rep(m):
    n[0] += 1
    return '<article class="q" id="q%d"' % n[0]


s2 = re.sub(r'<article class="q" id="q[0-9A-Za-z_-]+"', rep, s)
open(dst, "w", encoding="utf-8").write(s2)
print("cards=%d -> %s" % (n[0], dst))
