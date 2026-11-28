#!/usr/bin/env python3
"""按页序装配 tixing2-156-165.html（part1 六张种子按位插回 part2–part7）"""
import re, sys
def arts(n):
    s = open(f'work/drafts/parts/tixing2-156-165.part{n}.html').read()
    return re.findall(r'<article class="q" id="qTMP">.*?</article>', s, flags=re.S)
lists = {n: arts(n) for n in range(1, 8) if __import__('os').path.exists(f'work/drafts/parts/tixing2-156-165.part{n}.html')}
p1 = lists[1]; p2 = lists.get(2, []); p3 = lists.get(3, []); p4 = lists.get(4, [])
p5 = lists.get(5, []); p6 = lists.get(6, []); p7 = lists.get(7, [])
# part1 顺序：S1 分段·1(P156) S2 周期·1(P158) S3 公式·1(P159) S4 乘积·1(P161) S5 换元·1(P163) S6 应用·1(P165)
order = ([p1[0]] + p2[0:14] + p2[14:28] + [p2[28]] + [p1[1]] + p3[0:13] + p3[13:29]
        + [p1[2]] + p4 + [p1[3]] + p5[0:2] + p5[2:19] + p5[19:29]
        + [p1[4]] + p6[0:5] + p6[5:22] + p6[22:29]
        + [p1[5]] + p7)
open('work/drafts/parts/tixing2-156-165.html', 'w').write('\n\n'.join(order) + '\n')
print('合并', len(order))
