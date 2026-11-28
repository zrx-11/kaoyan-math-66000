#!/usr/bin/env python3
"""数学级变式查重 mvd.py —— 三重比对（全等 + 同构）
1) 变式 ↔ 本段原题(stem)
2) 变式 ↔ 变式
3) 变式 ↔ 参照文件的历史原题
用法：python3 work/qa/mvd.py <本段文件> [参照文件...]   碰撞计入退出码
"""
import re, sys

def articles(s):
    return re.findall(r'<article class="q" id="qTMP">.*?</article>', s, re.S)

def between(s, a, b):
    i = s.find(a)
    if i < 0: return ''
    return s[i+len(a): s.find(b, i)]

def pick(art, cls):
    i = art.find('<div class="%s">' % cls)
    if i < 0: return ''
    return art[i:]

def stem_of(art):
    return between(art, '<div class="stem">', '</div>')

def var_of(art):
    i = art.find('<div class="block var">')
    if i < 0: return ''
    t = art[i:]
    t = re.sub(r'<p class="var-ans">.*?</p>', '', t, flags=re.S)
    t = t.replace('<b>变式</b>', '')
    return t

def field(art, cls):
    m = re.search(r'<span class="%s">(.*?)</span>' % cls, art, re.S)
    return m.group(1).strip() if m else ''

def math_of(txt):
    return re.findall(r'\\\((.+?)\\\)', txt, re.S) + re.findall(r'\\\[(.+?)\\\]', txt, re.S)

FUNC = ['arcsin','arccos','arctan','sinh','cosh','tanh','sin','cos','tan','cot','sec','csc',
        'ln','log','exp','sqrt','max','min','sgn']

def _frac(s):
    for _ in range(10):
        m = re.search(r'\\(?:d|t|c)?frac\s*\{', s)
        if not m: break
        i, j = m.start(), m.end()
        d, k = 0, j-1
        for k in range(j-1, len(s)):
            if s[k] == '{': d += 1
            elif s[k] == '}':
                d -= 1
                if d == 0: break
        num = s[j:k]
        k2 = k+1
        while k2 < len(s) and s[k2] in ' \t': k2 += 1
        if k2 >= len(s) or s[k2] != '{': break
        d, kk = 0, k2
        for kk in range(k2, len(s)):
            if s[kk] == '{': d += 1
            elif s[kk] == '}':
                d -= 1
                if d == 0: break
        den = s[k2+1:kk]
        s = s[:i] + '(' + num + ')/(' + den + ')' + s[kk+1:]
    return s

def norm(s):
    s = _frac(s)
    s = re.sub(r'\\left|\\right|\\big|\\Big|\\bigg|\\Bigg|\\!|\\,|\\;|\\:|\\quad|\\qquad|\\displaystyle|\\limits|\\middle', '', s)
    s = re.sub(r'\\le(?:q|qslant)?|\\leqslant', '<', s)
    s = re.sub(r'\\ge(?:q|qslant)?|\\geqslant', '>', s)
    s = re.sub(r'\\lt\s*(?:\{(\})?)?', '<', s)
    s = re.sub(r'\\gt\s*(?:\{(\})?)?', '>', s)
    s = s.replace('\\cdot', '').replace('\\times', '*').replace('\\div', '/').replace('\\pm', 'P')
    s = re.sub(r'\\(?:mathrm|text|operatorname)\s*\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\s+', '', s)
    s = s.replace('{', '(').replace('}', ')')
    s = s.replace('\\', '')
    return s

def shape(s):
    s = norm(s)
    s = re.sub(r'\d+(?:\.\d+)?', 'N', s)
    # 函数名先换成大写字母占位（不受下面的 [a-z]→V 影响），保留函数身份
    for i, f in enumerate(sorted(FUNC, key=len, reverse=True)):
        s = s.replace(f, 'Q' + chr(ord('A') + i))
    s = re.sub(r'[a-z]', 'V', s)
    s = re.sub(r'(.)\1{3,}', r'\1\1', s)
    return s

def keys(art):
    st = [norm(x) for x in math_of(stem_of(art))]
    va = [norm(x) for x in math_of(var_of(art))]
    st = [x for x in st if len(x) >= 6]
    va = [x for x in va if len(x) >= 6]
    return ('|'.join(st), '|'.join(va), '|'.join(shape(x) for x in st), '|'.join(shape(x) for x in va),
            field(art, 'qtype'), field(art, 'qsrc'))

def ok(x):
    return bool(x) and len(x) >= 6

def main():
    if len(sys.argv) < 2:
        print('用法：python3 work/qa/mvd.py <本段文件> [参照文件...]'); sys.exit(2)
    self_f, refs = sys.argv[1], sys.argv[2:]
    me = [(i+1, keys(a)) for i, a in enumerate(articles(open(self_f).read()))]
    hist = [(f.split('/')[-1], j+1, keys(a)) for f in refs
            for j, a in enumerate(articles(open(f).read()))]
    hits = []
    for idx, (sm, vm, sms, vms, qt, pg) in me:
        # 1) 变式 ↔ 原题（本段）
        for jdx, (sm2, vm2, sms2, vms2, qt2, pg2) in me:
            if idx == jdx: continue
            if ok(vm) and vm == sm2:
                hits.append(('全等·变式撞本段原题', f'#{idx}[{qt}]', f'#{jdx}[{qt2}]'))
            elif ok(vms) and vms == sms2:
                hits.append(('同构·变式撞本段原题', f'#{idx}[{qt}]', f'#{jdx}[{qt2}]'))
        # 3) 变式 ↔ 历史原题
        for fn, jdx, (sm2, vm2, sms2, vms2, qt2, pg2) in hist:
            if ok(vm) and vm == sm2:
                hits.append(('全等·变式撞历史原题', f'#{idx}[{qt}]', f'{fn}#{jdx}[{qt2}]'))
            elif ok(vms) and vms == sms2:
                hits.append(('同构·变式撞历史原题', f'#{idx}[{qt}]', f'{fn}#{jdx}[{qt2}]'))
    # 2) 变式 ↔ 变式（段内两两）
    for idx, jdx in itertools.combinations(range(len(me)), 2):
        (sm, vm, sms, vms, qt, pg), (sm2, vm2, sms2, vms2, qt2, pg2) = me[idx][1], me[jdx][1]
        i1, i2 = me[idx][0], me[jdx][0]
        if ok(vm) and vm == vm2:
            hits.append(('全等·变式撞变式', f'#{i1}[{qt}]', f'#{i2}[{qt2}]'))
        elif ok(vms) and vms == vms2:
            hits.append(('同构·变式撞变式', f'#{i1}[{qt}]', f'#{i2}[{qt2}]'))
    n_card = len(me); n_v = sum(1 for _, k in me if ok(k[1]))
    n_hist = len(hist)
    ex = sum(1 for h in hits if h[0].startswith('全等'))
    sh = sum(1 for h in hits if h[0].startswith('同构'))
    for h in hits[:100]:
        print(' | '.join(h))
    print(f'数学级查重：本段 {n_card} 张（含变式 {n_v} 张）、参照原题 {n_hist} 张；全等碰撞 {ex} 处、同构碰撞 {sh} 处')
    sys.exit(1 if hits else 0)

if __name__ == '__main__':
    import itertools; main()
