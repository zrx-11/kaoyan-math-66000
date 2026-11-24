#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一字数口径工具（唯一权威口径）。

用法：
    python3 work/qa/plainlen.py <分片文件或目录> [起id 止id]

输出：
    每张卡一行：id / 展示题号(qno) / 整卡 plain 字数 / 解析(sol) plain 字数 /
                整卡汉字数 / 解析汉字数 / 行间公式数 / 行内公式数

口径（与 work/gate.py 的 plain() 完全一致，不得另立）：
    去 HTML 标签 -> 去 LaTeX 命令名 \\[a-zA-Z]+ -> 去 \\ $ { } ^ _ -> 去所有空白
    解析段切片：字面量 'block sol' 到 'block pit'

判定阈值（本册口径）：
    解析 300-420（硬上限 420）、整卡 >= 620（gate 硬下限 MIN_TEXT=430，本册用 620 更严）
"""
import glob
import os
import re
import sys

ART_RE = re.compile(r'<article class="q" id="q(\d+)"[^>]*>(.*?)</article>', re.S)
QNO_RE = re.compile(r'class="qno">(.*?)</span>', re.S)
HAN_RE = re.compile(r'[\u4e00-\u9fff]')


def plain(html):
    t = re.sub(r"<[^>]+>", "", html)
    t = re.sub(r"\\[a-zA-Z]+", "", t)
    t = re.sub(r"[\\${}^_]", "", t)
    return re.sub(r"\s+", "", t)


def han(html):
    return len(HAN_RE.findall(plain(html)))


def sol_slice(body):
    st = body.find('block sol')
    en = body.find('block pit')
    if st < 0:
        return ''
    if en <= st:
        en = len(body)
    return body[st:en]


def report(path, lo=None, hi=None):
    if os.path.isdir(path):
        files = sorted(glob.glob(os.path.join(path, '*.html')))
    else:
        files = [path]
    print("id\tqno\tcard_plain\tsol_plain\tcard_han\tsol_han\tdisplay_eq\tinline_eq")
    bad = []
    n = 0
    for f in files:
        s = open(f, encoding='utf-8').read()
        for mid, body in ART_RE.findall(s):
            qid = int(mid)
            if lo is not None and qid < lo:
                continue
            if hi is not None and qid > hi:
                continue
            n += 1
            mq = QNO_RE.search(body)
            qno = re.sub(r'<[^>]+>', '', mq.group(1)).strip() if mq else '?'
            sol = sol_slice(body)
            cp, sp = len(plain(body)), len(plain(sol))
            print("q%d\t%s\t%d\t%d\t%d\t%d\t%d\t%d" % (
                qid, qno, cp, sp, han(body), han(sol),
                body.count('\\['), body.count('\\(')))
            if not (300 <= sp <= 420):
                bad.append("q%d sol=%d 越界(300-420)" % (qid, sp))
            if cp < 620:
                bad.append("q%d card=%d 偏薄(<620)" % (qid, cp))
    print("# cards=%d" % n)
    if bad:
        print("# OUT_OF_RANGE %d:" % len(bad))
        for b in bad:
            print("#   " + b)
        return 1
    print("# ALL_IN_RANGE")
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    p = sys.argv[1]
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else None
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else None
    sys.exit(report(p, lo, hi))
