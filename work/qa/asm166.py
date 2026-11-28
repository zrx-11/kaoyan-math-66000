#!/usr/bin/env python3
"""按页序装配 tixing2-166-175.html（part1 五张种子按位插回 part2–part6）"""
import os
import re


def arts(n):
    p = f'work/drafts/parts/tixing2-166-175.part{n}.html'
    if not os.path.exists(p):
        return []
    s = open(p).read()
    return re.findall(r'<article class="q" id="qTMP">.*?</article>', s, flags=re.S)


p1 = arts(1)
p2, p3, p4, p5, p6 = arts(2), arts(3), arts(4), arts(5), arts(6)
# part1 顺序：S1 变限·9(P166) S2 不等式·1(P167) S3 等式·1(P170) S4 反常·1(P173) S5 瑕·1(P175)
order = ([p1[0]] + p2[0:16]
         + p2[16:21] + [p1[1]] + p3[0:5]
         + p3[5:15] + p3[15:26]
         + p3[26:29] + [p1[2]] + p4[0:5]
         + p4[5:15] + p4[15:25]
         + p4[25:29] + [p1[3]] + p5[0:7]
         + p5[7:23]
         + p5[23:29] + [p1[4]] + p6)
open('work/drafts/parts/tixing2-166-175.html', 'w').write('\n\n'.join(order) + '\n')
print('合并', len(order), '（期望 119）')
