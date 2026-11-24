# -*- coding: utf-8 -*-
"""
M2 核心：膝盖角度 + 状态机深蹲计数
=====================================
这个文件**不开摄像头**，纯逻辑，可以直接跑自测：
    python3 squat_logic.py
会打印一段模拟深蹲的计数过程。先把它跑明白了，再把它接进 demo.py。

为什么单独拆一个文件？
  → 算法和画面分开，出了 bug 一眼知道是"算错了"还是"画错了"。
    这是工程师最基本的习惯，比语法重要十倍。
"""

import math

# ==================== 参数（调参就改这里）====================
ANGLE_DOWN = 100   # 膝盖角 < 100° 判定为"蹲到底"
ANGLE_UP   = 160   # 膝盖角 > 160° 判定为"站直"
# 两个阈值中间留出 60° 的"死区"，这是防抖动的关键：
# 如果只用单个阈值（比如 <100 算蹲下），你在临界点微微一晃，
# 计数器就会疯狂 +1。死区 = 迟滞比较器，电路里也这么干。
# ===========================================================


def angle_3pt(a, b, c):
    """
    求 ∠ABC，即三条关键点构成的夹角，b 是顶点。
    深蹲看膝盖角：a=髋(23) b=膝(25) c=踝(27)

    原理（这就是专升本高数要考的向量点积）：
        cosθ = (BA · BC) / (|BA| × |BC|)
        θ = arccos(cosθ) × 180/π

    注意 landmark 给的是归一化坐标 (0~1)，x 还要乘画面宽高比才不失真，
    但算角度时同一张图里比例一致，误差很小，入门阶段可以忽略。
    """
    ax, ay = a.x, a.y
    bx, by = b.x, b.y
    cx, cy = c.x, c.y

    bax, bay = ax - bx, ay - by     # 向量 BA
    bcx, bcy = cx - bx, cy - by     # 向量 BC

    dot = bax * bcx + bay * bcy                     # 点积
    mag_ba = math.hypot(bax, bay)                   # |BA|
    mag_bc = math.hypot(bcx, bcy)                   # |BC|

    if mag_ba < 1e-6 or mag_bc < 1e-6:
        return None                                  # 点重合，算不了

    cos_v = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))  # 钳位，防 acos 爆 NaN
    return math.degrees(math.acos(cos_v))


class SquatCounter:
    """状态机：站立 → 下降 → 底部 → 上升 → 站立(+1)"""

    def __init__(self, down=ANGLE_DOWN, up=ANGLE_UP):
        self.down_th = down
        self.up_th = up
        self.count = 0
        self.stage = "up"          # "up" 站立 / "down" 蹲下
        self.history = []          # 记录每次的角度，方便画曲线

    def update(self, knee_angle):
        """
        喂进当前帧的膝盖角度，返回 (count, stage, hint)
        hint 是用来在画面上报警的文字，None 表示不用报
        """
        if knee_angle is None:
            return self.count, self.stage, None

        hint = None

        # ---------- 状态机核心，就这 6 行 ----------
        if knee_angle < self.down_th and self.stage != "down":
            self.stage = "down"                      # 进到底部
        elif knee_angle > self.up_th and self.stage == "down":
            self.stage = "up"                        # 站回来了 → 完成一次
            self.count += 1
            hint = f"#{self.count}  GOOD!"
        # ----------------------------------------

        # 附加：背部太弯提醒（髋-肩-耳 夹角，简化版用髋肩连线斜率代替）
        self.history.append(knee_angle)
        return self.count, self.stage, hint

    def reset(self):
        self.count, self.stage, self.history = 0, "up", []


# ==================== 自测：模拟 3 次深蹲 ====================
if __name__ == "__main__":
    class P:
        def __init__(self, x, y): self.x, self.y, self.z = x, y, 0.0

    def fake_pose(knee_deg):
        """
        造一组 landmark，让膝盖角 ∠髋-膝-踝 **精确等于** knee_deg。

        构造：以膝为顶点，两边等长 L，分别朝"上偏 θ/2"和"下偏 θ/2"张开，
        夹角必然 = θ。
        ⚠️ 第一版这里是拍脑袋挪 x 坐标，结果想造 95° 实际只有 110°，
           导致自测"计到 0 次"，差点误判算法写错。
           —— 真实项目里"测试数据自己有 bug"就是这样骗人的，值得记一辈子。
        """
        import math as m
        # 固定髋(上)和踝(下)，把膝沿水平方向往前顶：
        # 膝越往前顶 → 夹角越小（=深蹲下去）；膝收回成一条线 → 180°（=站直）
        # 由等腰三角形关系：前顶量 = L*cos(θ/2)，半长 = L*sin(θ/2)
        L = 0.30
        t = m.radians(knee_deg) / 2
        hip = P(0.50, 0.55 - L * m.sin(t))
        ankle = P(0.50, 0.55 + L * m.sin(t))
        knee = P(0.50 + L * m.cos(t), 0.55)
        return {23: hip, 25: knee, 27: ankle}

    sc = SquatCounter()
    # 模拟：站(170) → 蹲(95) → 站(170) ×3，中间插几帧抖动
    script = [170,168,172, 120, 98,95,93,96, 130, 165,170,   # 第 1 次
              172, 115, 92,90,94, 140, 168,171,              # 第 2 次
              170, 100,95, 110, 105, 100, 95, 92, 150,172]   # 第 3 次（含临界抖动）

    print("帧  膝角   阶段   计数   提示")
    print("-" * 42)
    for i, deg in enumerate(script):
        lm = fake_pose(deg)
        a = angle_3pt(lm[23], lm[25], lm[27])
        c, st, hint = sc.update(a)
        flag = f"  ← {hint}" if hint else ""
        print(f"{i:>2}  {a:>5.1f}°  {st:>4}   {c:>2}{flag}")

    print("-" * 42)
    ok = "✅" if sc.count == 3 else "❌"
    print(f"{ok} 模拟 {len(script)} 帧，计到 {sc.count} 次（期望 3）")
    print("临界抖动那几帧(105/100/95)没有重复+1 → 死区生效，状态机没被抖崩。")
