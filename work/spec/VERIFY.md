# 核验手册（额度友好版）

## 一条命令看现状
```bash
cd /home/user/Doubao/chats/38454435152889602
python3 work/gate.py        # 结构闸门，看 cards / quarantine 比例
python3 work/audit.py       # 可疑卡：页码错位、解析雷同
python3 work/spotcheck.py --round N   # 出第 N 轮看板
```

## 核单题的固定动作（不要省）
1. 查页：`work/manifest/jixian_map.json` 里 q→page，打开 `work/pages/jixian/p00NNN.png`
2. 比题干：数字、符号、上下标、选项、趋近方向，逐字对
3. 比答案：书答案 vs 卡片答案栏；不一致时卡片必须有校勘块
4. 复算解析：按卡片给的展开式重算一遍，看能不能得到答案栏的值
5. 验变式：变式题自己解一遍，答案对不对
6. 写台账：`work/checks.csv` 追加 `q,page,verdict,note,time`

## verdict 口径
- `pass` 四项全对
- `fixed` 我改掉并已复算
- `fail` 有实质错误 → 自动进 `work/fixlist.json`，站点立即下线
- `skip` 书印问题（题面与答案矛盾/漏印），已写可见校勘块

## 回站
```bash
python3 work/spotcheck.py   # 刷新 fixlist
bash work/publish.sh        # 构建并推送
```

## 额度控制
- 一次只核 50–100 题，核完即停，不要顺手扩范围
- 只核「可疑清单」而不全量核，成本可降到 1/5
- 生产（新写卡）成本约为核验的 2–3 倍，额度紧张时只核不产
