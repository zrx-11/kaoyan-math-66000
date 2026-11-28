#!/usr/bin/env python3
"""按页序装配 tixing2-176-185.html（part1 五张种子按位插回 part2–part6）"""
import os
import re


def arts(n):
    p = f'work/drafts/parts/tixing2-176-185.part{n}.html'
    if not os.path.exists(p):
        return []
    s = open(p).read()
    return re.findall(r'<article class="q" id="qTMP">.*?</article>', s, flags=re.S)


p1 = arts(1)
p2, p3, p4, p5, p6 = arts(2), arts(3), arts(4), arts(5), arts(6)
# part1 顺序：S1 瑕·8(P176) S2 Γ·1(P177) S3 综合·1(P179) S4 几何·1(P181) S5 物理·1(P183)
order = ([p1[0]] + p2[0:13]
         + p2[13:22] + [p1[1]] + p3[0:3]
         + p3[3:19]
         + p3[19:29] + [p1[2]] + p4[0:4]
         + p4[4:19]
         + p4[19:29] + [p1[3]] + p5[0:3]
         + p5[3:20]
         + p5[20:29] + [p1[4]] + p6[0:4]
         + p6[4:19]
         + p6[19:29] + p6[29:32])
open('work/drafts/parts/tixing2-176-185.html', 'w').write('\n\n'.join(order) + '\n')
print('合并', len(order), '（期望 146）')
