# -*- coding: utf-8 -*-
"""站点构建：分册 → 专题 → 分页。专题从《…》标题解析。"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = f"{ROOT}/kaoyan66000"
if not os.path.isdir(SITE):  # 可移植：仓库自身即站点时，SITE 就是 ROOT
    SITE = ROOT
FRAG = f"{ROOT}/work/fragments"
LECT = f"{ROOT}/work/content/lectures"
WORK = f"{ROOT}/work"

EXTRA_FRAG = {(2, 1): [f"{ROOT}/work/fragments/jixian", f"{ROOT}/work/fragments/jixian/parts"]}

ART_RE = re.compile(r'<article class="q" id="q(\d+)".*?</article>', re.S)
TOPIC_RE = re.compile(r"《([^》]{2,30})》\s*(?:(\d{2,5})\s*题)?")

MATHJAX = """<script>
MathJax = {tex:{inlineMath:[['\\\\(','\\\\)'],['$','$']],displayMath:[['\\\\[','\\\\]']]},options:{skipHtmlTags:['script','noscript','style','textarea','pre','code']}};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>"""

SLUG = {
    1: "01-tixing-6000", 2: "02-gaoshu-15000", 3: "03-xiandai-6600", 4: "04-weilai-3000",
    5: "05-liming-2000", 6: "06-gaoshu-2600", 7: "07-xiandai-1200", 8: "08-gailv-950",
    9: "09-gaoshu-9000", 10: "10-xiandai-2500", 11: "11-gailv-2900", 12: "12-kaoti-3030",
    13: "13-kaoti-2310", 14: "14-kaoti-2450", 15: "15-kaoti-2500", 16: "16-kaoti-1650",
}

SHORT = {
    1: "题型篇 6000", 2: "高等数学习题集 15000", 3: "线性代数 6600", 4: "题型篇 未来初现 3000",
    5: "题型篇 黎明开启 2000", 6: "高等数学 2600 典型题", 7: "线性代数 1200 典型题",
    8: "概率论 950 典型题", 9: "高等数学 9000 题", 10: "线性代数 2500 题",
    11: "概率论与数理统计 2900 题", 12: "考研数学 3030（带解析）", 13: "考研数学 2310（带解析）",
    14: "考研数学 2450（带解析）", 15: "考研数学 2500（带解析）", 16: "考研数学 1650（带解析）",
}


def head(title, root):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{root}assets/site.css">
{MATHJAX}
</head>
<body>
<div class="topbar"><div class="topbar-inner">
  <span class="topbar-title"><a href="{root}index.html">考研数学 66000 · 逐题精解</a></span>
  <span class="topbar-nav"><a href="{root}index.html">总览</a><a href="{root}knowledge/index.html">知识地图</a><a href="{root}progress.html">进度</a></span>
</div></div>
<div class="wrap">
"""


FOOT = """<div class="foot"><span>{left}</span><span>{right}</span></div>
</div>
</body>
</html>
"""


def parse_topics(v):
    """抽专题。

    优先读冻结表 work/plan/topics.json（专题编号一旦分配不得变，否则 tNN 目录错位）；
    表里没有这册时才回退到标题解析（下面那段）。
    """
    tf = os.path.join(WORK, "plan", "topics.json")
    if os.path.exists(tf):
        try:
            data = json.load(open(tf, encoding="utf-8"))
            vv = (data.get("volumes") or {}).get(SLUG.get(v["idx"], f"{v['idx']:02d}"))
            if vv:
                return [{"name": t["name"], "page": t["page"], "count": t.get("count")}
                        for t in vv["topics"]]
        except Exception:
            pass
    return _parse_topics_by_title(v)


def _parse_topics_by_title(v):
    def clean(n):
        n = re.sub(r"[（(]\s*(副本|已自动恢复|修复的)\s*[)）]", "", n)
        n = re.sub(r"\s*[-–]\s*副本\s*(?:[（(]\s*\d+\s*[)）])?", "", n)
        n = re.sub(r"[（(]\s*\d+\s*[)）]", "", n)
        n = re.sub(r"\s*(副本|已自动恢复|修复的)\s*$", "", n)
        return n.strip(" -_·")

    def dedupe(items):
        seen, out = set(), []
        for t in items:
            key = re.sub(r"\s+", "", t["name"])
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(t)
        return out

    named = []
    for s in v["sections"]:
        title = s["title"]
        ms = re.findall(r"《([^《》]{2,40})》", title)
        if not ms:
            continue
        name = ms[-1].strip()
        pos = title.rfind(name) + len(name)
        m = re.search(r"(\d{2,5})\s*题", title[pos:])
        named.append({"name": name, "page": s["page"],
                      "count": int(m.group(1)) if m else None})
    named = dedupe(named)

    lvl2 = []
    for s in v["sections"]:
        if s["level"] != 2:
            continue
        name = clean(re.sub(r"^[\d.、\s]+", "", s["title"]))
        if len(name) < 4:
            continue
        m = re.search(r"(\d{2,5})\s*题", s["title"])
        lvl2.append({"name": name, "page": s["page"],
                     "count": int(m.group(1)) if m else None})

    # 同名加序：Ⅰ Ⅱ Ⅲ → （二）（三）
    counts, out = {}, []
    for t in lvl2:
        k = re.sub(r"\s+", "", t["name"])
        counts[k] = counts.get(k, 0) + 1
        out.append(dict(t, name=t["name"] if counts[k] == 1 else f"{t['name']}（{counts[k]}）"))
    lvl2 = out

    if len(named) >= 2:
        return named
    if len(lvl2) >= 2:
        return lvl2
    return named or lvl2


def load_cards(frag_dir):
    import json as _json
    q = set()
    for name in ("quarantine.json", "fixlist.json"):
        try:
            q |= set(_json.load(open(f"{ROOT}/work/{name}", encoding="utf-8")))
        except Exception:
            pass
    cards, files = {}, sorted(glob.glob(os.path.join(frag_dir, "*.html")))
    for f in files:
        html = open(f, encoding="utf-8").read()
        for m in ART_RE.finditer(html):
            n=int(m.group(1))
            if n in q: continue
            if n in cards and len(m.group(0)) <= len(cards[n]): continue
            cards[n] = m.group(0)
    return cards, files


def build_topic(vol_slug, tidx, t, cards, lecture):
    tslug = f"t{tidx:02d}"
    tdir = os.path.join(SITE, "volumes", vol_slug, tslug)
    os.makedirs(tdir, exist_ok=True)
    nums = sorted(cards)
    parts = []
    chunk = 100
    for i in range(0, len(nums), chunk):
        cn = nums[i : i + chunk]
        no = i // chunk + 1
        lo, hi = cn[0], cn[-1]
        body = "\n\n".join(cards[n] for n in cn)
        # 题号展示以卡片 qno 为准（多册/多专题时全局 id 与册内编号不同）
        def _disp(html, fallback):
            m2 = re.search(r'class="qno">第\s*(\d+)\s*题', html)
            return int(m2.group(1)) if m2 else fallback
        dlo, dhi = _disp(cards[cn[0]], lo), _disp(cards[cn[-1]], hi)
        nav = []
        if no > 1:
            nav.append(f'<a href="part-{no-1:02d}.html">← 上一分页</a>')
        nav.append('<a href="index.html">目录</a>')
        if no * chunk < len(nums):
            nav.append(f'<a href="part-{no+1:02d}.html">下一分页 →</a>')
        h = head(f"《{t['name']}》 · 第 {dlo}–{dhi} 题", "../../")
        h += f"""<header class="pagehead">
  <div class="kicker">{vol_slug} · 专题 {tidx:02d}</div>
  <h1>第 {dlo} – {dhi} 题</h1>
  <p class="sub">{" ".join(nav)}</p>
</header>
"""
        h += body + FOOT.format(left="逐题精解 · MathJax 渲染", right=f"第 {dlo}–{dhi} 题")
        open(os.path.join(tdir, f"part-{no:02d}.html"), "w", encoding="utf-8").write(h)
        parts.append({"no": no, "lo": dlo, "hi": dhi, "n": len(cn)})

    h = head(f"《{t['name']}》 · 目录", "../../")
    total = t.get("count")
    pct = round(len(cards) / total * 100, 1) if total else 0
    h += f"""<header class="pagehead">
  <div class="kicker">专题 {tidx:02d} · P{t['page']} 起</div>
  <h1>《{t['name']}》{f' {total} 题' if total else ''}</h1>
  <p class="sub">已上线 {len(cards)} 题{f'（{pct}%）' if total else ''} · 每题含完整推导、易错点、考向与变式</p>
</header>
"""
    if lecture:
        h += lecture
    h += '<div class="toc"><h3>分页目录</h3><ul>'
    for p in parts:
        h += f'<li><a href="part-{p["no"]:02d}.html">第 {p["lo"]}–{p["hi"]} 题</a>　<span class="meta">{p["n"]} 题</span></li>'
    h += "</ul></div>"
    if not parts:
        h += '<p class="sub">该专题尚未开始生产题目卡片，先提供知识讲解。</p>'
    h += FOOT.format(left="每页 100 题", right=f"共 {len(cards)} 题")
    open(os.path.join(tdir, "index.html"), "w", encoding="utf-8").write(h)
    return len(parts), len(cards)


def build_volume(meta, topics, root="../"):
    slug = meta["slug"]
    vdir = os.path.join(SITE, "volumes", slug)
    os.makedirs(vdir, exist_ok=True)
    h = head(f"{meta['short']} · 目录", root)
    live = sum(1 for t in topics if t.get("done"))
    h += f"""<header class="pagehead">
  <div class="kicker">第 {meta['idx']} 册 · P{meta['pages_range']}</div>
  <h1>{meta['short']}</h1>
  <p class="sub">共 {meta['pages']} 页 · {len(topics)} 个专题 · {live} 个专题已上线</p>
</header>
"""
    h += '<div class="toc"><h3>专题列表</h3><ul>'
    for t in topics:
        if t.get("done"):
            h += f'<li><a href="t{t["i"]:02d}/index.html">《{t["name"]}》</a>　<span class="meta">{t["done"]} 题已上线</span></li>'
        else:
            h += f'<li><span class="muted">《{t["name"]}》</span>　<span class="meta">P{t["page"]} · 待启动</span></li>'
    h += "</ul></div>"
    h += FOOT.format(left="按专题顺序推进", right="")
    open(os.path.join(vdir, "index.html"), "w", encoding="utf-8").write(h)


def build_index(metas, progress):
    h = head("考研数学 66000 · 逐题精解", "")
    h += """<header class="pagehead">
  <div class="kicker">冯建轩《考研数学66000》· 全书逐题精解</div>
  <h1>考研数学 66000 逐题精解</h1>
  <p class="sub">16 个分册、约 6.4 万题。每题给出完整推导、易错点、考向分析与变式训练；按专题分页，可持续扩充。</p>
</header>
"""
    h += '<div class="grid">'
    for m in metas:
        done = progress.get(m["slug"], 0)
        total = m["q_total"] or 0
        bar = f'<div class="c-bar"><span style="width:{min(100, round(done/total*100)) if total else 0}%"></span></div>'
        h += f"""<a class="card{" done" if done else ""}" href="volumes/{m['slug']}/index.html">
      <span class="c-no">第 {m['idx']} 册 · {m['pages']} 页</span>
      <span class="c-title">{m['short']}</span>
      <span class="c-meta">{total or "题量待统计"} 题 · 已上线 {done} 题</span>
      {bar}
    </a>"""
    h += "</div>" + FOOT.format(left="逐册推进，先上线部分专题", right="公式渲染 MathJax 3")
    open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(h)


def build_progress(rows, grand):
    h = head("进度 · 考研数学66000", "")
    h += """<header class="pagehead"><div class="kicker">生产进度</div><h1>逐题精解完成情况</h1>
<p class="sub">按专题统计已上线题量与覆盖情况。</p></header>"""
    h += f'<div class="lecture"><h2>全书 {grand["done"]} / {grand["total"]} 题</h2><p>覆盖率 {round(grand["done"]/grand["total"]*100,2)}%。逐题精解为人工逐页读题撰写，按批次推进。</p></div>'
    h += '<div class="toc"><h3>已上线专题</h3><ul>'
    for r in rows:
        h += f'<li><a href="../volumes/{r["slug"]}/t{r["i"]:02d}/index.html">《{r["name"]}》</a>　<span class="meta">{r["done"]} / {r["total"]} 题</span></li>'
    h += "</ul></div>" + FOOT.format(left="随内容更新自动刷新", right="")
    open(os.path.join(SITE, "progress.html"), "w", encoding="utf-8").write(h)


def main():
    os.makedirs(SITE, exist_ok=True)
    vols = json.load(open(f"{WORK}/manifest/volumes.json", encoding="utf-8"))["volumes"]
    inv = {v["idx"]: v for v in json.load(open(f"{WORK}/manifest/inventory.json", encoding="utf-8"))}

    metas, all_topics = [], {}
    for v in vols:
        m = {
            "idx": v["idx"], "title": v["title"], "short": SHORT.get(v["idx"], v["title"]),
            "slug": SLUG.get(v["idx"], f"{v['idx']:02d}"), "pages": v["pages"],
            "pages_range": f'{v["start"]}–{v["end"]}', "sections": v["sections"],
            "q_total": (inv.get(v["idx"], {}) or {}).get("q_max") or 0,
        }
        metas.append(m)
        all_topics[v["idx"]] = parse_topics(v)

    progress, rows, grand = {}, [], {"done": 0, "total": 0}
    for m in metas:
        topics = []
        for i, t in enumerate(all_topics[m["idx"]], 1):
            # 内容目录：fragments/<slug>/tNN、lectures/<slug>/tNN.html
            fdir = os.path.join(FRAG, m["slug"], f"t{i:02d}")
            cards, _ = load_cards(fdir) if os.path.isdir(fdir) else ({}, [])
            # 兼容旧路径（子智能体写出的分片）
            for alt in EXTRA_FRAG.get((m["idx"], i), []):
                if os.path.isdir(alt):
                    c2, _ = load_cards(alt)
                    cards.update(c2)
            lfile = os.path.join(LECT, m["slug"], f"t{i:02d}.html")
            lecture = open(lfile, encoding="utf-8").read() if os.path.exists(lfile) else ""
            tinfo = {"i": i, "name": t["name"], "page": t["page"], "count": t["count"], "done": 0}
            if cards or lecture:
                _, n = build_topic(m["slug"], i, t, cards, lecture)
                tinfo["done"] = n
                if n:
                    rows.append({"slug": m["slug"], "i": i, "name": t["name"], "done": n, "total": t["count"] or n})
                    grand["done"] += n
                    grand["total"] += t["count"] or n
            topics.append(tinfo)
        progress[m["slug"]] = sum(x["done"] for x in topics)
        build_volume(m, topics)

    build_index(metas, progress)
    build_progress(rows, grand)

    kdir = os.path.join(SITE, "knowledge")
    os.makedirs(kdir, exist_ok=True)
    h = head("知识地图 · 考研数学66000", "../")
    h += """<header class="pagehead"><div class="kicker">知识地图</div><h1>分册 · 专题 · 页码</h1>
<p class="sub">按 PDF 原始页码定位每个专题，便于按知识点选题训练。已完成的《极限》另有按解题手法归并的<a href="jixian-types.html">题型知识树</a>（题目 → 方法主线 → 已实测错法）。</p></header>"""
    for m in metas:
        h += f'<div class="grouphead"><h2>第 {m["idx"]} 册 · {m["short"]}</h2><div class="meta">P{m["pages_range"]} · {m["pages"]} 页</div></div>'
        ts = all_topics[m["idx"]]
        if ts:
            h += '<div class="toc"><ul>'
            for i, t in enumerate(ts, 1):
                cnt = f' {t["count"]} 题' if t["count"] else ""
                h += f'<li>《{t["name"]}》{cnt}　<span class="meta">P{t["page"]}</span></li>'
            h += "</ul></div>"
    h += FOOT.format(left="页码为 PDF 原始页码", right="")
    open(os.path.join(kdir, "index.html"), "w", encoding="utf-8").write(h)

    import subprocess, sys as _sys
    subprocess.run([_sys.executable, f"{WORK}/build_knowledge.py"], check=True)

    json.dump({"metas": metas, "progress": progress, "rows": rows, "grand": grand},
              open(f"{SITE}/data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("grand", grand, "topics with content:", len(rows))


if __name__ == "__main__":
    main()
