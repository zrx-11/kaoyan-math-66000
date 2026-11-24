# -*- coding: utf-8 -*-
"""取接下来可派的生产单元（派活的唯一入口）。

用法：
    python3 work/plan/next_batch.py 4              # 接下来 4 个单元
    python3 work/plan/next_batch.py 4 --vol 2      # 只取第 2 册
    python3 work/plan/next_batch.py 4 --topic 3    # 只取某册某专题（需配 --vol）

输出每个单元：册 / 专题 tNN / 页段 / 目标分片目录 / 页图命令 / 全局起始题号。
**全局起始题号**来自现有卡片的最大 id + 1，因为 id 必须全库唯一且递增；
而 qno（卡面上「第 N 题」）是专题内编号，从 1 开始。
"""
import argparse
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAN = os.path.join(ROOT, "work", "plan")
FRAG = os.path.join(ROOT, "work", "fragments")
WORK = os.path.join(ROOT, "work")

ID_RE = re.compile(r'<article class="q" id="q(\d+)"')


def max_id():
    m = 0
    for f in glob.glob(os.path.join(FRAG, "**", "*.html"), recursive=True):
        txt = open(f, encoding="utf-8", errors="replace").read()
        for hit in ID_RE.findall(txt):
            v = int(hit)
            if v > m:
                m = v
    return m


def pdf_path():
    p = os.environ.get("PDF_PATH")
    if p and os.path.exists(p):
        return p
    for f in glob.glob(os.path.join(ROOT, "*.pdf")):
        return f
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int, nargs="?", default=4)
    ap.add_argument("--vol", type=int)
    ap.add_argument("--topic", type=int)
    a = ap.parse_args()

    waves = json.load(open(os.path.join(PLAN, "waves.json"), encoding="utf-8"))
    topics = json.load(open(os.path.join(PLAN, "topics.json"), encoding="utf-8"))["volumes"]
    pending = [u for u in waves["units"] if u["status"] == "pending"]
    if a.vol:
        pending = [u for u in pending if u["vol"] == a.vol]
    if a.topic:
        pending = [u for u in pending if u["topic"] == a.topic]
    picks = pending[: a.n]

    start_id = max_id() + 1
    pdf = pdf_path()
    print(f"全局下一可用题号 id: q{start_id}   （现有最大 id = {start_id-1}）")
    print(f"PDF: {pdf or '未找到 —— 请 export PDF_PATH=<路径>'}")
    print(f"待生产单元总数: {len(pending)}\n")

    for u in picks:
        slug, t = u["slug"], u["topic"]
        name = (topics.get(slug, {}).get("topics") or [{}] * t)[t - 1].get("name", u["topic_name"])
        lo, hi = u["pages"]
        fdir = os.path.join(FRAG, slug, f"t{t:02d}")
        pdir = os.path.join(WORK, "pages", slug)
        lec = os.path.join(WORK, "content", "lectures", slug, f"t{t:02d}.html")
        print(f"── {u['id']}  第{u['vol']}册 / t{t:02d}《{name}》  P{lo}–{hi}")
        print(f"   目标分片: work/fragments/{slug}/t{t:02d}/seg-{lo}-{hi}.html")
        print(f"   起始 id: q{start_id} （qno 从第 1 题起）")
        print(f"   讲解页:   {'已存在' if os.path.exists(lec) else '❌ 缺失 → 先跑 work/plan/scaffold_topic.py ' + f'{slug} {t}'}")
        if pdf:
            print(f"   页图:     mkdir -p {os.path.relpath(pdir, ROOT)} && pdftoppm -png -r 150 -gray "
                  f"-f {lo} -l {hi} \"{pdf}\" {os.path.relpath(pdir, ROOT)}/p")
            print(f"             （产出 p-{lo:05d}.png…，实际命名以 ls 为准）")
        print("")

    print("派活提醒：单元之间不要共用文件；同一单元的多片必须按题号块合并，禁止整文件重建。")


if __name__ == "__main__":
    main()
