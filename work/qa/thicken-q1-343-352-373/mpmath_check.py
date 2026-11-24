# -*- coding: utf-8 -*-
"""加厚 q343 / q352 / q373 三张相消型卡片前的 mpmath 高精度实算。
口径：mp.dps=50，分别在 x=1e-2、1e-3、1e-4 处取值，与解析极限对照。
q1 为极限定义选择题，不涉及相消型数值极限，故不在本脚本内。
"""
import mpmath as mp

mp.mp.dps = 50

xs = [mp.mpf("1e-2"), mp.mpf("1e-3"), mp.mpf("1e-4")]

# q352: (sin x - x)/x^3 -> -1/6
def f352(x):
    return (mp.sin(x) - x) / x**3

# q373: [ln(1+x) - ln(1-x) - 2x]/x^3 -> 2/3
def f373(x):
    return (mp.log(1 + x) - mp.log(1 - x) - 2 * x) / x**3

# q343: [ln(1+u) - u + u^2/2 - u^3/3]/x^8, u = sin(x^2) -> -1/4
def f343(x):
    u = mp.sin(x**2)
    num = mp.log(1 + u) - u + u**2 / 2 - u**3 / 3
    return num / x**8

for name, f, target in [
    ("q352", f352, mp.mpf("-1") / 6),
    ("q373", f373, mp.mpf("2") / 3),
    ("q343", f343, mp.mpf("-1") / 4),
]:
    print(f"== {name}  target = {mp.nstr(target, 12)}")
    for x in xs:
        v = f(x)
        print(f"   x={mp.nstr(x, 6)}  f(x)={mp.nstr(v, 14)}  diff={mp.nstr(v - target, 6)}")
    print()
