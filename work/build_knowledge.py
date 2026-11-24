# -*- coding: utf-8 -*-
"""从已建好的题卡生成《极限》题型知识树页面（按册分区）。

输入：work/fragments/02-gaoshu-15000/<t01|t02>/seg-*.html（同题号多分片取最长者）
输出：kaoyan66000/knowledge/jixian-types.html
      work/content/summary/jixian-types.json

分区原则：每册有独立的片段目录、关键词表、站点分页目录与 URL 前缀。
t01 卡只走 t01 规则，t02 卡只走 t02 规则，两套关键词互不匹配，
避免加厚卡片时跨册命中漂移。某册规则表为空时整册不纳入输出，
空规则产物与改造前基线逐字节一致。
"""
import glob
import html
import os
import re
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "kaoyan66000")
if not os.path.isdir(SITE):  # 可移植：仓库自身即站点时，SITE 就是 ROOT
    SITE = ROOT
OUT = os.path.join(SITE, "knowledge", "jixian-types.html")
DATA = os.path.join(ROOT, "work/content/summary/jixian-types.json")

ART = re.compile(r'<article class="q" id="q(\d+)">(.*?)</article>', re.S)
QTYPE = re.compile(r'<span class="qtype">(.*?)</span>', re.S)
TREND = re.compile(r'<div class="block trend"><div class="block-title">考向</div>(.*?)</div>', re.S)
CAV = 'block caveat'
TAG = re.compile(r'<[^>]+>')


def plain(s):
    return html.unescape(TAG.sub(" ", s)).replace("\\\\", "\\")


def load(frag):
    best = {}
    for f in glob.glob(os.path.join(frag, "seg-*.html")):
        t = open(f, encoding="utf-8").read()
        for q, body in ART.findall(t):
            q = int(q)
            if q not in best or len(body) > len(best[q][1]):
                m = QTYPE.search(body)
                tr = TREND.search(body)
                best[q] = (plain(m.group(1)).strip() if m else "", body,
                           plain(tr.group(1)).strip() if tr else "")
    return {q: {"qtype": v[0], "trend": v[2], "caveat": CAV in v[1], "len": len(v[1])}
            for q, v in best.items()}


# 第一册题型 → 知识板块。按 (关键词, 板块) 顺序匹配，先命中者优先。
# 注意：本表只服务 t01 卡片，一个字都不要为 t02 改动（防跨册漂移）。
RULES = [
    ("特殊函数与积分", ["erfc", "Si(", "Ci(", "Ei(", "Li(", "erfi", "伽马", "\\Gamma", "Γ", "菲涅尔", "Fresnel", "狄利克雷", "高斯积分"]),
    ("定积分定义", ["定积分定义", "黎曼和", "n 项和", "n项和", "积分和", "分割求和"]),
    ("递推数列", ["递推", "迭代", "压缩映射", "单调有界", "不动点", "数列{a_n}", "数列 {a_n}", "递推式"]),
    ("变上限积分", ["变上限", "变限积分", "变限", "被积函数", "积分上限"]),
    ("幂指与 e 型", ["1^\\infty", "1∞", "1^\\\\infty", "幂指", "0^0", "\\infty^0", "∞^0", "1^{\\infty}"]),
    ("泰勒展开", ["泰勒", "Taylor", "麦克劳林", "展开", "余项", "高阶项", "佩亚诺", "反三角", "复合函数", "经典题"]),
    ("无穷小比较", ["无穷小的阶", "阶的", "最高阶", "最低阶", "同阶", "等价无穷小", "比较无穷小", "几阶", "比阶", "阶数", "无穷小", "主部", "有界量"]),
    ("洛必达与未定式", ["洛必达", "未定式", "0/0", "∞/∞", "\\infty/\\infty", "0\\cdot\\infty", "∞-∞", "\\infty-\\infty"]),
    ("夹逼准则", ["夹逼", "两边夹", "放缩", "夹挤"]),
    ("数列极限计算", ["数列", "连乘", "连乘积", "阶乘", "n!", "n 次方", "n次方", "幂指比", "求和", "部分和", "无穷乘积", "欧拉常数"]),
    ("由极限反求参数", ["反求", "求常数", "确定常数", "求 a", "求 \\(a", "参数", "求参数", "含参"]),
    ("指数差与提公因子", ["指数差", "提公因子", "同底", "指数式比阶", "e tan x", "e^{\\tan", "e^{\\sin"]),
    ("对数型", ["对数", "ln(", "\\ln", "log"]),
    ("振荡与积分极限", ["振荡", "震荡", "Riemann", "端点渐近", "权函数"]),
    ("工具型：极值与不等式", ["最小值", "最大值", "单调", "极值", "不等式"]),
    ("导数定义与高阶导数", ["导数定义", "高阶导数", "周期函数"]),
    ("根式与有理化", ["根式", "有理化", "分母有理化", "开方", "√", "\\sqrt"]),
    ("有理函数与无穷远", ["有理函数", "x\\to\\infty", "x→∞", "无穷远", "多项式比", "幂积比", "对数比"]),
    ("左右极限与存在性", ["左右极限", "单侧", "左极限", "右极限", "双侧", "不存在", "跳跃"]),
    ("取整与分段函数", ["取整", "[x]", "分段函数", "绝对值", "sgn", "符号函数", "min", "max"]),
    ("证明与存在性", ["证明", "存在性", "唯一性", "零点定理", "介值"]),
    ("原题面缺失", ["公式丢失", "无法还原", "原题"]),
]

# 第二册《n 项和极限》题型 → 知识板块（v2，200 张口径）。关键词取自题卡
# qtype 完整短语；裸词「连乘」「二重」「等差和」「含参」会被考向散文串族，
# 不作判据。顺序按「最具体 → 最泛」：硬判据族在前，归一黎曼和兜底。
RULES_T02 = [
    ("根号失配发散", ["因子对账", "发散判定"]),
    ("括号层级歧义可定值", ["漏一对外层括号"]),
    ("端点无定义但可定值", ["首项", "ln k=0"]),
    ("多印外层 1/n", ["题面系数与答案矛盾", "题面多印外层", "多印一层"]),
    ("1∞ 幂指", ["裂项求和", "1^∞", "1 ∞", "对数展开到 1/n²"]),
    ("连乘不开方", ["无外层开方", "取对数转等差和"]),
    ("连乘开 n 次方", ["连乘取对数", "连乘开 n 次方", "高次指数项", "斯特林", "望远镜"]),
    ("二重黎曼和", ["二重黎曼和", "二重可分离", "二重可加"]),
    ("三重黎曼和", ["三重黎曼和", "三重可分离", "三重不可分离"]),
    ("含参黎曼和", ["含参指数型", "含参正弦型", "含参余弦型", "含参分式型", "含参幂次型", "含参对数型", "含参根式型", "含参 t", "含参 i, t"]),
    ("调和 / 对数调和和", ["对数调和和", "幂指加权调和和", "欧拉常数"]),
    ("调和内层小量压阶趋零", ["调和因子相消", "调和对数阶", "内层二阶小量", "泰勒一阶抵消", "三阶小量"]),
    ("归一黎曼和（单重）", ["黎曼和", "定积分定义", "归一"]),
]

# 按册分区配置：每册独立片段目录、规则表、站点分页目录、URL 前缀与首题题号。
# part_base 用于把题号换算成站点分页号：part = (q - part_base) // 100 + 1。
VOLUMES = [
    {
        "key": "t01",
        "label": "第一册 · 函数与极限",
        "frag": os.path.join(ROOT, "work/fragments/02-gaoshu-15000/t01"),
        "site_dir": os.path.join(SITE, "volumes/02-gaoshu-15000/t01"),
        "url_prefix": "../volumes/02-gaoshu-15000/t01",
        "rules": RULES,
        "part_base": 1,
    },
    {
        "key": "t02",
        "label": "第二册 · n 项和极限",
        "frag": os.path.join(ROOT, "work/fragments/02-gaoshu-15000/t02"),
        "site_dir": os.path.join(SITE, "volumes/02-gaoshu-15000/t02"),
        "url_prefix": "../volumes/02-gaoshu-15000/t02",
        "rules": RULES_T02,
        "part_base": 2651,
    },
]


def bucket(card, rules):
    text = card["qtype"] + " " + card["trend"]
    for name, keys in rules:
        for k in keys:
            if k in text:
                return name
    return "其他"


def part_url(q, vol):
    no = (q - vol["part_base"]) // 100 + 1
    return f"{vol['url_prefix']}/part-{no:02d}.html#q{q}"


SECTION_TEXT = json.load(open(os.path.join(ROOT, "work/content/summary/sections.json"), encoding="utf-8"))


def published(vol):
    """已上线题号：以该册站点分页为准，避免把生产中未发布的卡算进来。"""
    ids = set()
    for f in glob.glob(os.path.join(vol["site_dir"], "part-*.html")):
        ids |= {int(x) for x in re.findall(r'<article class="q" id="q(\d+)">', open(f, encoding="utf-8").read())}
    return ids


def collect(vol):
    cards = load(vol["frag"])
    pub = published(vol)
    if pub:
        cards = {q: c for q, c in cards.items() if q in pub}
    groups = {}
    for q, c in cards.items():
        groups.setdefault(bucket(c, vol["rules"]), []).append(q)
    for v in groups.values():
        v.sort()
    order = [n for n, _ in vol["rules"] if n in groups] + (["其他"] if "其他" in groups else [])
    cav = sum(1 for c in cards.values() if c["caveat"])
    return {"vol": vol, "cards": cards, "groups": groups, "order": order, "cav": cav}


def _group_block(vol, groups, order, anchor_prefix):
    """渲染一组板块（grouphead + lecture + qlist）。anchor_prefix 用于跨册锚点去重。"""
    h = []
    for n in order:
        qs = groups[n]
        s = SECTION_TEXT.get(n, {})
        anchor = f"{anchor_prefix}{n}" if anchor_prefix else n
        h.append(f'<div class="grouphead" id="{anchor}"><h2>{n} <span class="meta">{len(qs)} 题</span></h2></div>')
        h.append('<div class="lecture">')
        if s.get("line"):
            h.append(f'<p><b>方法主线</b>：{s["line"]}</p>')
        if s.get("pit"):
            h.append(f'<p><b>已实测的错法</b>：{s["pit"]}</p>')
        if s.get("check"):
            h.append(f'<p><b>自查口径</b>：{s["check"]}</p>')
        h.append("</div>")
        links = " ".join(f'<a href="{part_url(q, vol)}">{q}</a>' for q in qs)
        h.append(f'<div class="qlist">{links}</div>')
    return h


def _render_single(p):
    """单册渲染：与改造前基线逐字节一致（仅 t01 一册激活时走这条路）。"""
    vol, cards, groups, order, cav = p["vol"], p["cards"], p["groups"], p["order"], p["cav"]
    h = []
    h.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>《极限》题型知识树 · 考研数学66000</title>
<link rel="stylesheet" href="../assets/site.css">
<script>
MathJax = {tex:{inlineMath:[['\\\\(','\\\\)'],['$','$']],displayMath:[['\\\\[','\\\\]']]},options:{skipHtmlTags:['script','noscript','style','textarea','pre','code']}};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
<div class="topbar"><div class="topbar-inner">
  <span class="topbar-title"><a href="../index.html">考研数学 66000 · 逐题精解</a></span>
  <span class="topbar-nav"><a href="../index.html">总览</a><a href="index.html">知识地图</a><a href="../progress.html">进度</a></span>
</div></div>
<div class="wrap">
""")
    h.append(f"""<header class="pagehead"><div class="kicker">题型知识树 · 《极限》</div>
<h1>{len(cards)} 题归为 {len(order)} 类</h1>
<p class="sub">按解题手法分类，不按书的页码顺序。每类给出方法主线、已实测的错法、以及该类的全部题号（点开即到原卡）。统计：{cav} 张卡带可见校勘块（占 {cav*100/len(cards):.1f}%），说明原书答案在这一分册里的错率不是零头。</p></header>""")
    h.append('<div class="toc"><ul>')
    for n in order:
        h.append(f'<li><a href="#{n}">{n}</a> <span class="meta">{len(groups[n])} 题</span></li>')
    h.append("</ul></div>")

    h += _group_block(vol, groups, order, "")

    h.append('<div class="foot"><span>分类由题卡自带的题型标签归并，可人工调整</span><span>共 %d 题</span></div>' % len(cards))
    h.append("</div></body></html>")
    return h, {n: groups[n] for n in order}, {vol["key"]: {"cards": len(cards), "groups": {n: len(groups[n]) for n in order}, "caveat": cav}}


def _render_multi(per):
    """多册渲染：t01 板块在前，其后追加各册分组；锚点按册加前缀避免重名。"""
    total_cards = sum(len(p["cards"]) for p in per)
    total_groups = sum(len(p["order"]) for p in per)
    total_cav = sum(p["cav"] for p in per)
    h = []
    h.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>《极限》题型知识树 · 考研数学66000</title>
<link rel="stylesheet" href="../assets/site.css">
<script>
MathJax = {tex:{inlineMath:[['\\\\(','\\\\)'],['$','$']],displayMath:[['\\\\[','\\\\]']]},options:{skipHtmlTags:['script','noscript','style','textarea','pre','code']}};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
<div class="topbar"><div class="topbar-inner">
  <span class="topbar-title"><a href="../index.html">考研数学 66000 · 逐题精解</a></span>
  <span class="topbar-nav"><a href="../index.html">总览</a><a href="index.html">知识地图</a><a href="../progress.html">进度</a></span>
</div></div>
<div class="wrap">
""")
    h.append(f"""<header class="pagehead"><div class="kicker">题型知识树 · 《极限》</div>
<h1>{total_cards} 题归为 {total_groups} 类</h1>
<p class="sub">按解题手法分类，不按书的页码顺序。每类给出方法主线、已实测的错法、以及该类的全部题号（点开即到原卡）。统计：{total_cav} 张卡带可见校勘块（占 {total_cav*100/total_cards:.1f}%），说明原书答案在这一分册里的错率不是零头。</p></header>""")
    h.append('<div class="toc"><ul>')
    for p in per:
        vol = p["vol"]
        h.append(f'<li><b>{vol["label"]}</b></li>')
        for n in p["order"]:
            anchor = f"{vol['key']}-{n}"
            h.append(f'<li><a href="#{anchor}">{n}</a> <span class="meta">{len(p["groups"][n])} 题</span></li>')
    h.append("</ul></div>")

    for i, p in enumerate(per):
        vol = p["vol"]
        if i > 0:
            h.append(f'<div class="grouphead" id="{vol["key"]}"><h2>{vol["label"]}</h2></div>')
        h += _group_block(vol, p["groups"], p["order"], f"{vol['key']}-")

    h.append('<div class="foot"><span>分类由题卡自带的题型标签归并，可人工调整</span><span>共 %d 题</span></div>' % total_cards)
    h.append("</div></body></html>")
    data = {p["vol"]["key"]: {n: p["groups"][n] for n in p["order"]} for p in per}
    stats = {p["vol"]["key"]: {"cards": len(p["cards"]), "groups": {n: len(p["groups"][n]) for n in p["order"]}, "caveat": p["cav"]} for p in per}
    return h, data, stats


def build():
    # 规则表为空的册整册跳过：尚未归类的题不进产物，保证空规则时输出与基线逐字节一致。
    active = [v for v in VOLUMES if v["rules"]]
    per = [collect(v) for v in active]

    if len(per) == 1:
        h, data, stats = _render_single(per[0])
    else:
        h, data, stats = _render_multi(per)

    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(h))
    for key, st in stats.items():
        print(key, "cards", st["cards"], "groups", st["groups"], "caveat", st["caveat"])


if __name__ == "__main__":
    build()
