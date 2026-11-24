# -*- coding: utf-8 -*-
"""为新专题生成讲解页骨架（缺了它，build_site 不会在站点上挂出该专题目录页）。

用法：
    python3 work/plan/scaffold_topic.py 02-gaoshu-15000        # 该册所有缺讲解页的专题
    python3 work/plan/scaffold_topic.py 02-gaoshu-15000 3      # 只做 t03
    python3 work/plan/scaffold_topic.py --all                  # 全部册

已存在的讲解页不会被覆盖（避免冲掉已经写好的正文）。
骨架只占位，真正的知识讲解由生产该专题时补写。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.path.join(ROOT, "work")
PLAN = os.path.join(WORK, "plan")
LECT = os.path.join(WORK, "content", "lectures")

TEMPLATE = """<section class="lecture">
  <h2>《{name}》正在生产</h2>
  <p>本专题位于第 {vol} 册 P{lo}–{hi}，共约 {pages} 页。题目卡片正在按页段推进，
  当前上线 {n} 题；知识讲解与题型归并待本专题建卡完成后统一补写。</p>
  <p>如本页长期停在「正在生产」，说明该专题尚未排入生产队列；计划见
  <code>work/plan/waves.md</code>，下一个可派单元用
  <code>python3 work/plan/next_batch.py</code> 查询。</p>
</section>
"""


def count_cards(slug, t):
    import glob
    import re
    d = os.path.join(WORK, "fragments", slug, f"t{t:02d}")
    if not os.path.isdir(d):
        return 0
    n = 0
    for f in glob.glob(os.path.join(d, "*.html")):
        n += len(re.findall(r'<article class="q" id="q\d+"', open(f, encoding="utf-8", errors="replace").read()))
    return n


def main():
    args = [a for a in sys.argv[1:]]
    topics = json.load(open(os.path.join(PLAN, "topics.json"), encoding="utf-8"))["volumes"]
    if not args:
        print(__doc__)
        sys.exit(1)

    if args[0] == "--all":
        targets = [(slug, t["t"]) for slug, vv in topics.items() for t in vv["topics"]]
    else:
        slug = args[0]
        if slug not in topics:
            print(f"没有这一册：{slug}。现有：{', '.join(sorted(topics))}")
            sys.exit(1)
        if len(args) > 1:
            targets = [(slug, int(args[1]))]
        else:
            targets = [(slug, t["t"]) for t in topics[slug]["topics"]]

    made = skipped = 0
    for slug, tno in targets:
        vv = topics[slug]
        tp = next((x for x in vv["topics"] if x["t"] == tno), None)
        if not tp:
            continue
        f = os.path.join(LECT, slug, f"t{tno:02d}.html")
        if os.path.exists(f):
            skipped += 1
            continue
        os.makedirs(os.path.dirname(f), exist_ok=True)
        html = TEMPLATE.format(name=tp["name"], vol=vv["idx"], lo=tp["page"],
                               hi=tp["page_end"], pages=tp["page_end"] - tp["page"] + 1,
                               n=count_cards(slug, tno))
        open(f, "w", encoding="utf-8").write(html)
        made += 1
        print("created", os.path.relpath(f, ROOT))

    print(f"\n新建 {made} 个，已存在跳过 {skipped} 个")
    print("下一步：python3 work/build_site.py   # 让新专题出现在站点目录")


if __name__ == "__main__":
    main()
