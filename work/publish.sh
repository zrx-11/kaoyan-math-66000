#!/usr/bin/env bash
# 自动发布：闸门 → 构建 → 提交 → 推送。硬缺陷存在则中止，站点不发行脏数据。
set -euo pipefail
# 项目根 = 本脚本所在 work/ 的上级目录（可移植，clone 到任何路径均可运行）
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 work/spotcheck.py > work/spotcheck.log 2>&1 || true

if ! python3 work/gate.py > work/gate.stdout 2>&1; then
  echo "[$(date '+%F %T')] GATE BLOCKED — 存在结构性缺陷，跳过发布" >> work/publish.log
  sed -n '/拦截清单/,$p' work/gate-report.md | head -20 >> work/publish.log
  exit 0
fi

python3 work/build_site.py > work/build.stdout 2>&1
CARDS=$(python3 -c "import json;d=json.load(open('work/gate.json'));print(d['cards'])")
SITE="$ROOT/kaoyan66000"
[ -d "$SITE" ] || SITE="$ROOT"   # 可移植：仓库自身即站点时，SITE 就是 ROOT
cd "$SITE"
if git diff --quiet && git diff --cached --quiet && [ -z "$(git status --porcelain)" ]; then
  echo "[$(date '+%F %T')] no change ($CARDS cards)" >> "$ROOT/work/publish.log"
  exit 0
fi
git add -A
git commit -qm "auto: 累计 ${CARDS} 题 $(date '+%m-%d %H:%M')"
git push -q origin main
echo "[$(date '+%F %T')] published ${CARDS} cards" >> "$ROOT/work/publish.log"
