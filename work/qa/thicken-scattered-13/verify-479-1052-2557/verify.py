# -*- coding: utf-8 -*-
"""q479 / q1052 / q2557 三张卡数值校验，mpmath 高精度实算（禁止双精度估）。

口径：
- q479：无穷乘积 ∏(1+x/k^3)，取 x=1；取对数化为 Σ ln(1+1/k^3)，
  与 p-级数 Σ1/k^3（ζ(3)）对照，看部分乘积是否稳定到有限常数。
- q1052：R(x)=[ln(1+x)-x]/x^2，多档 x 向 -1/2 收敛。
- q2557：R(x)=[∫_0^x e^{-t^2}dt]/x，多档 x 向 1 收敛；
  并展开积分核对主部 x - x^3/3。
"""
import mpmath as mp

mp.dps = 50
out = []


def log(line):
    print(line)
    out.append(line)


# ---------- q479：无穷乘积收敛性（x=1） ----------
log("== q479 无穷乘积 ∏(1+1/k^3)，取对数 S_n=Σ ln(1+1/k^3) ==")
for n in (1000, 10000, 100000):
    s = mp.nsum(lambda k: mp.log(1 + 1 / k ** 3), [1, n])
    p = mp.e ** s
    log(f"  n={n:>6}: S_n={mp.nstr(s, 12)}  P_n=exp(S_n)={mp.nstr(p, 12)}")

zeta3 = mp.zeta(3)
zeta6 = mp.zeta(6)
# ln(1+u)=u-u^2/2+u^3/3-...，u=1/k^3
s_approx = zeta3 - zeta6 / 2 + mp.zeta(9) / 3
log(f"  ζ(3)={mp.nstr(zeta3, 12)}（p=3>1，p-级数收敛）")
log(f"  对数和一阶近似 ζ(3)-ζ(6)/2+ζ(9)/3={mp.nstr(s_approx, 12)}，"
    f"对应乘积={mp.nstr(mp.e ** s_approx, 12)}")
log("  结论：部分乘积随 n 增大稳定到有限常数，不趋于 0、1 或 ∞，对应选项 C。")

# ---------- q1052：[ln(1+x)-x]/x^2 ----------
log("")
log("== q1052 R(x)=[ln(1+x)-x]/x^2，目标极限 -1/2 ==")
for x in (mp.mpf("1e-2"), mp.mpf("1e-3"), mp.mpf("1e-4"), mp.mpf("1e-5")):
    r = (mp.log(1 + x) - x) / x ** 2
    log(f"  x={mp.nstr(x, 6)}: R(x)={mp.nstr(r, 12)}")
log(f"  理论值 -1/2 = -0.5；ln(1+x)=x-x^2/2+x^3/3+O(x^4)，一次项相消后主部 -x^2/2。")

# ---------- q2557：[∫_0^x e^{-t^2}dt]/x ----------
log("")
log("== q2557 R(x)=[∫_0^x e^{-t^2}dt]/x，目标极限 1 ==")
for x in (mp.mpf("1e-2"), mp.mpf("1e-3"), mp.mpf("1e-4")):
    integ = mp.quad(lambda t: mp.e ** (-t ** 2), [0, x])
    r = integ / x
    log(f"  x={mp.nstr(x, 6)}: 积分={mp.nstr(integ, 12)}  R(x)={mp.nstr(r, 12)}")
log("  展开：e^{-t^2}=1-t^2+O(t^4)，积分=x-x^3/3+O(x^5)，商=1-x^2/3+O(x^4)→1；")
log("  被积函数在 0 处取值 e^0=1。")

with open(__file__.replace("verify.py", "results.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
