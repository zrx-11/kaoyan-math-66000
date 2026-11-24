# -*- coding: utf-8 -*-
"""q1624 / q1627 / q1633 数值校验（mpmath 高精度，不依赖双精度相消）。

三张都是相消 / 等价无穷小型：x 很小时分子被压到高阶主部，
普通双精度在 1e-3 量级已会丢位，故全程 mpmath dps=50。

- q1624: R(x) = [ln(1+x)-x]/x^2  ->  a = -1/2
- q1627: R(x) = [sqrt(1+x^2)-cos x]/x^2  ->  1
- q1633: R(x) = [sin x - x + x^3/6]/x^5  ->  k = 1/120
"""
import mpmath as mp

mp.dps = 80

# 两条独立路径：A 直接调 mpmath 函数（高精度相消）；B 显式多项式级数，
# 互相印证。小 x 相消时 A 的内部求值会丢位，以 B 的级数结果为准写进解析。

XS = [mp.mpf("1e-2"), mp.mpf("1e-3"), mp.mpf("1e-4")]

# 路径 A：直接函数求值
DIRECT = [
    ("q1624", mp.mpf("-1") / 2,
     lambda x: (mp.log(1 + x) - x) / x ** 2),
    ("q1627", mp.mpf(1),
     lambda x: (mp.sqrt(1 + x ** 2) - mp.cos(x)) / x ** 2),
    ("q1633", mp.mpf(1) / 120,
     lambda x: (mp.sin(x) - x + x ** 3 / 6) / x ** 5),
]

# 路径 B：显式泰勒多项式（系数来自独立求导，不在解析里抄同一份）
# q1624: ln(1+x)-x = -x^2/2 + x^3/3 - x^4/4 + x^5/5
def poly_1624(x):
    y = x ** 2
    return (-mp.mpf(1) / 2 + x / 3 - x ** 2 / 4 + x ** 3 / 5)

# q1627: sqrt(1+x^2)-cos x = x^2 - x^4/12 + 5x^6/96 ...
# 系数：sqrt 展开 1 + x^2/2 - x^4/8 + x^6/16；cos 1 - x^2/2 + x^4/24 - x^6/720
def poly_1627(x):
    return 1 - x ** 2 / 12 + x ** 4 * (mp.mpf(1) / 16 + mp.mpf(1) / 720)

# q1633: sin x - x + x^3/6 = x^5/120 - x^7/5040 + x^9/362880
def poly_1633(x):
    return mp.mpf(1) / 120 - x ** 2 / 5040 + x ** 4 / 362880

POLY = [("q1624", mp.mpf("-1") / 2, poly_1624),
        ("q1627", mp.mpf(1), poly_1627),
        ("q1633", mp.mpf(1) / 120, poly_1633)]

# 级数系数复核：直接取泰勒展开前几项，核对解析里写的中间阶。
def taylor_coeffs(fn, n=6):
    return [mp.nstr(c, 12) for c in mp.taylor(fn, 0, n)]

print("== 级数系数复核（常数, x, x^2, ...）==")
print("ln(1+x)      :", taylor_coeffs(lambda x: mp.log(1 + x), 5))
print("sqrt(1+x^2)  :", taylor_coeffs(lambda x: mp.sqrt(1 + x ** 2), 5))
print("cos x        :", taylor_coeffs(mp.cos, 5))
print("sin x        :", taylor_coeffs(mp.sin, 6))

print("\n== 路径 A：mpmath 直接函数求值 ==")
for name, theory, fn in DIRECT:
    print(f"\n{name} 理论值 = {mp.nstr(theory, 20)}")
    for x in XS:
        r = fn(x)
        print(f"  x={mp.nstr(x, 6)}  R(x)={mp.nstr(r, 16)}  |误差|={mp.nstr(abs(r - theory), 6)}")

print("\n== 路径 B：显式泰勒多项式 ==")
for name, theory, fn in POLY:
    print(f"\n{name} 理论值 = {mp.nstr(theory, 20)}")
    for x in XS:
        r = fn(x)
        print(f"  x={mp.nstr(x, 6)}  R(x)={mp.nstr(r, 16)}  |误差|={mp.nstr(abs(r - theory), 6)}")
