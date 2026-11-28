import re

def raw_len(html):
    t = re.sub(r"<[^>]+>", "", html)
    return len(re.sub(r"\s+", "", t))

s = open('work/drafts/parts/tixing2-166-175.part5.html', encoding='utf-8').read()
arts = re.findall(r'<article class="q" id="qTMP">.*?</article>', s, re.S)
for i, a in enumerate(arts, 1):
    if '校勘' not in a:
        continue
    m = re.search(r'<div class="block caveat">(.*?)</div>\s*(?=<div class="block)', a, re.S)
    blk = m.group(1) if m else ''
    mp = re.search(r'block-title">校勘</div>\s*<p>(.*?)</p>', a, re.S)
    p = mp.group(1) if mp else ''
    print(i, 'block=', raw_len(blk), 'p=', raw_len(p))
