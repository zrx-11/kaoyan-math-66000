# 考研数学 66000 · 逐题精解

冯建轩《考研数学66000》全书逐题精解的**可编辑 HTML 站点**。每题包含：题干（LaTeX）、答案、完整推导、易错点、考向分析、变式训练。

## 目录结构

```
index.html                      # 总览：16 个分册与完成度
progress.html                   # 生产进度
knowledge/index.html            # 知识地图：分册 → 专题 → 页码
assets/site.css                 # 全站样式（改这里统一换风格）
volumes/
  02-gaoshu-15000/              # 第 2 册：高等数学习题集 15000 题
    index.html                  # 册内专题列表
    t01/                        # 专题 01：《极限》2650 题
      index.html                # 专题首页（知识讲解 + 分页目录）
      part-01.html              # 第 1–100 题
      part-02.html              # 第 101–200 题 …
  ...
```

## 怎么编辑

站点是纯静态 HTML，没有构建依赖，改完直接刷新即可。

- **改单题**：在对应 `part-XX.html` 里找到 `<article class="q" id="q123">`，五个板块（`stem` / `answer` / `sol` / `pit` / `trend` / `var`）都可以直接改。
- **改样式**：`assets/site.css` 顶部有配色变量，改 `--accent` 就能换主色。
- **公式**：`\( ... \)` 行内，`\[ ... \]` 行间，由 MathJax 3 渲染（CDN 加载）。
- **新增题目**：复制一张 `<article>` 卡片，改 `id="qN"` 与内容；`id` 必须唯一且等于题号。

## 生产管线（如需继续扩充）

1. 页面图像：`work/pages/jixian/p00590.png …`（PDF 按 150dpi 灰度渲染，视觉读题，文本层会丢 π、∞、∫ 等符号，不可用）。
2. 生产规范：`work/spec/PIPELINE.md`（卡片结构、深度要求、质量红线）。
3. 样板：`work/templates/gold-1-6.html`（第 1–6 题，作为风格基准）。
4. 分片产出：`work/fragments/jixian/seg-<起页>-<止页>.html`，只含 `<article>` 卡片。
5. 合并建站：`python3 work/build_site.py`，按题号排序、去重、每 100 题一页，自动生成目录与进度。

## 进度

- 第 2 册 专题《极限》2650 题：进行中（见 `progress.html`）
- 其余 15 册：待启动

## 说明

内容为学习整理的二次创作（解析、考向、变式为原创），题干与答案引自原书，仅供个人学习使用。
