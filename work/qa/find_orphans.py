# -*- coding: utf-8 -*-
"""扫描分片里「不属于任何 article」的游离 <p>。

背景：早期脚本拼接事故在 seg-832-838 里留下过 36 条游离 <p>（「在考研中，……」式），
夹在两卡之间、不属于任何 article。build_site.py 只搬 <article>，所以这类垃圾
会一直留在 master 里，任何按题号做的校验都看不见它。

用法：
    python3 work/qa/find_orphans.py                       # 扫全部 work/fragments
    python3 work/qa/find_orphans.py <文件或目录> ...

判定：按 <article 起点切片（不要用行首 </article>，缩进闭合的会漏），
落在任何 article 区间内的 <p> 不算游离。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT = os.path.join(ROOT, "work", "fragments")

ART_START = re.compile(r"<article\b")
P_TAG = re.compile(r"<p\b[^>]*>")


def article_spans(txt):
    spans = []
    for m in ART_START.finditer(txt):
        end = txt.find("</article>", m.start())
        spans.append((m.start(), len(txt) if end == -1 else end + 10))
    return spans


def scan(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    spans = article_spans(txt)
    hits = []
    for m in P_TAG.finditer(txt):
        pos = m.start()
        if any(a <= pos < b for a, b in spans):
            continue
        snippet = re.sub(r"<[^>]+>", "", txt[pos:pos + 300])
        snippet = re.sub(r"\s+", " ", snippet).strip()[:70]
        line = txt.count("\n", 0, pos) + 1
        hits.append((line, snippet))
    return hits, len(spans)


def walk(targets):
    for t in targets:
        if os.path.isdir(t):
            for dirpath, _, names in os.walk(t):
                for n in sorted(names):
                    if n.endswith(".html") and not n.endswith(".bak"):
                        yield os.path.join(dirpath, n)
        elif t.endswith(".html"):
            yield t


def main():
    targets = sys.argv[1:] or [DEFAULT]
    total = 0
    for f in walk(targets):
        hits, n_art = scan(f)
        if hits:
            total += len(hits)
            rel = os.path.relpath(f, ROOT)
            print(f"\n{rel}  (article {n_art} 篇, 游离 <p> {len(hits)} 条)")
            for line, snip in hits[:10]:
                print(f"  行 {line}: {snip}")
            if len(hits) > 10:
                print(f"  …另 {len(hits)-10} 条")
    print(f"\n合计游离 <p>: {total}")
    print("处置：删前留档（cp -p 到 before/），删后复核 article 哈希未变。")


if __name__ == "__main__":
    main()
