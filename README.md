# 🏋️ AI 深蹲计数器 · Pose Demo

> 专科大一学生的第一个机器视觉项目。
> 从"摄像头能画出骨架"一路做到"自动数深蹲 + 姿势纠错"，全程踩坑实录。

![demo](./assets/demo.gif)

> _占位：用 QuickTime 录 10 秒 → 转 GIF 丢进 `assets/` 即可。没有 GIF 之前，先把 `M1_preview.png` 放这儿。_

---

## ✨ 当前进度

| 里程碑 | 内容 | 状态 |
|---|---|---|
| **M0** | 摄像头实时姿态估计（33 关键点） | ✅ 完成 |
| **M1** | 自定义渲染：金色骨架 / 隐藏关节点 / 人数提示条 / 水印 | ✅ 完成 |
| **M2** | 膝盖角度算法 + 状态机深蹲计数 + 防抖死区 | ✅ 逻辑完成，待接摄像头 |
| M3 | 体感控制（手腕坐标 → 键盘事件，玩 Chrome 小恐龙） | ⏳ 计划中 |
| M4 | Streamlit GUI + CSV 导出 + PyInstaller 打包 exe | ⏳ 计划中 |
| M5 | 树莓派 4B 部署，INT8 量化 | ⏳ 计划中 |
| M6 | 切工业视觉支线：OpenCV 缺陷检测 + Halcon + C# 界面 | ⏳ 大二下 |

---

## 🛠️ 技术栈

- **MediaPipe Tasks API** 1.2.x（`pose_landmarker_full.task`）
- **OpenCV** 4.9+
- **Python** 3.11 / 3.12
- 向量点积求夹角 + **迟滞状态机**（hysteresis state machine）防抖

---

## 🚀 跑起来

```bash
# 1. 建环境（强烈建议，别污染系统 Python）
python3 -m venv mp_env
source mp_env/bin/activate        # Windows: mp_env\Scripts\activate

# 2. 装依赖
pip install mediapipe opencv-python numpy

# 3. 下模型（约 29MB），放到本目录，和 demo.py 做邻居
curl -L -o pose_landmarker_full.task \
  https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task

# 4a. 没摄像头 / 想先验证画图逻辑 → 自测模式，不用模型也能跑
SELFTEST=1 python3 demo.py

# 4b. 正常跑（会生成 M1_preview.png 两张自测图）
python3 demo.py

# 4c. 只测计数算法，不开摄像头
python3 squat_logic.py
```

按 **`q`** 退出。

> **macOS 特别提示**：第一次跑会弹"终端想要使用摄像头"，必须点允许。
> 之前点错过的话：系统设置 → 隐私与安全性 → 摄像头 → 把 Terminal / VS Code 打开。

---

## 🐛 踩过的坑（这一节才是精华）

> 面试官 100% 会翻这里。能写出踩坑记录 = 真的自己做过 = 不是抄的 tutorial。

### 坑 1 · `ModuleNotFoundError: No module named 'mediapipe.framework'`
**现象**：照着 CSDN 上的老教程写 `from mediapipe.framework.formats import landmark_pb2`，直接崩。
**根因**：MediaPipe **1.2.x 把 `mediapipe.framework` 整个删了**。网上 90% 的教程还是 0.10 时代的写法。
**解法**：新版 `drawing_utils.draw_landmarks()` **直接吃 `result.pose_landmarks[0]` 这个原生 list**，
**根本不需要** `landmark_pb2` 手动构造 `NormalizedLandmarkList`。删掉那三行，世界清净。
> 💡 教训：AI 库版本迭代极快，**先 `pip show mediapipe` 看版本，再决定信哪篇教程**。

### 坑 2 · `AttributeError: type object 'PoseLandmarker' has no attribute 'POSE_CONNECTIONS'`
**根因**：`POSE_CONNECTIONS` 是**旧版 Solutions API**（`mp.solutions.pose`）的东西，Tasks API 里没有。
**解法**：
```python
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarksConnections
connections = PoseLandmarksConnections.POSE_LANDMARKS   # 35 条连线
```

### 坑 3 · `TypeError: list.append() takes exactly one argument (3 given)`
**我写的代码**：`proto.append(landmark.x, landmark.y, landmark.z)`
**根因**：`list.append()` 只吃**一个**参数。想塞三个得用 `append((x,y,z))` 或 `extend()`。
**更大的教训**：这一行其实**根本不该存在**——见坑 1，新版压根不用手动构造。
> 💡 当你发现自己在给一个"不该存在的步骤"修 bug，说明方向错了，退回去重想，别硬修。

### 坑 4 · 代码改了，运行结果纹丝不动
**现象**：编辑器里明明是新代码，终端报错行号还是旧的。
**根因**：VS Code 标题栏显示 `● 已编辑` —— **忘了 Cmd+S**。
**解法**：跑之前瞄一眼标题栏，红点在就先存。
> 💡 这是新手第一大时间黑洞。我在这上面卡了 20 分钟才反应过来。

### 坑 5 · `cat > demo.py` 之后 VS Code 弹"文件已在磁盘上被修改"
**根因**：终端和编辑器同时改同一个文件，VS Code 怕覆盖你的改动。
**解法**：点 **"仍要保存"（Overwrite）**，以编辑器里的为准。以后**二选一**：要么在终端写，要么在编辑器写，别两头改。

### 坑 6 · `FileNotFoundError: Unable to open file at pose_landmarker_full.task`
**现象**：一堆 C++ 栈帧刷屏，看不出人话。
**解法**：现在 `demo.py` 里加了 `build_detector()` 懒加载，模型缺失时只打印 4 行人话 + 下载链接。
> 💡 **自己写的报错信息质量，就是工程水平的照妖镜。** 别让用户（包括三个月后的你自己）去读 C++ 栈。

### 坑 7 · 🎁 附加赠品：测试数据自己有 bug
写 `squat_logic.py` 自测时，模拟 29 帧深蹲**计到 0 次**，我第一反应是"状态机写错了"。
查了半小时才发现：**是我的假数据生成器几何构造错了**——髋/膝/踝三点共线，
不管输入 95° 还是 170°，`angle_3pt()` 算出来恒为 180.0°，所以永远进不了 `down` 状态。
算法没问题，**是自测脚本在骗我**。
> 💡 这条最值钱：**"结果不对"时，先怀疑测试数据，再怀疑算法。**
> 顺序反了，你会把一个对的算法改错。

---

## 🧠 核心算法：为什么要两个阈值

```python
ANGLE_DOWN = 100   # < 100°  → 蹲到底
ANGLE_UP   = 160   # > 160°  → 站直
```

只用一个阈值（比如 `<100` 就算蹲下）会怎样？
你在 98°~102° 之间微微一晃，计数器就 `+1 +1 +1` 疯狂跳。

两个阈值中间留出 **60° 死区** = 电路里的**迟滞比较器（hysteresis）**：
进了 `down` 状态，必须一路回到 160° 以上才允许下次计数。

自测脚本第 20-26 帧专门造了这段抖动：
```
20  100.0°    up    2
21   95.0°  down    2     ← 进 down
22  110.0°  down    2     ← 晃回去，不加
23  105.0°  down    2     ← 再晃，不加
24  100.0°  down    2     ← 还晃，不加
25   95.0°  down    2
26   92.0°  down    2
28  172.0°    up    3     ← 真站直了，才 +1 ✅
```
**这 7 帧抖动，一次误计数都没有。** 面试官问"你怎么处理抖动"，就指这 7 行。

角度公式就是专升本高数的向量点积，学完立刻用上的感觉很爽：
```
cosθ = (BA · BC) / (|BA| × |BC|)      θ = arccos(cosθ)
```

---

## 📁 项目结构

```
pose-demo/
├── demo.py              # M0+M1：摄像头 + 姿态检测 + 自定义渲染
├── squat_logic.py       # M2：角度算法 + 状态机（可独立自测，不开摄像头）
├── requirements.txt
├── pose_landmarker_full.task   # ← 自己下，不进 git（见 .gitignore）
├── assets/
│   ├── demo.gif
│   ├── M1_preview.png          # SELFTEST=1 生成的自测图
│   └── M1_preview_nobody.png
├── README.md
└── .gitignore
```

**为什么把算法单独拆一个文件？**
算法和画面分开，出 bug 一眼知道是"算错了"还是"画错了"。
这习惯比任何语法都值钱。

---

## 📈 下一步 & 已知局限

**现在的短板（面试要能自己说出来，别等对方戳）**：
- 只测**左腿**（landmark 23/25/27），右腿没做，侧向站立会漏检
- 没有 **置信度过滤**，`visibility < 0.5` 的点也硬算，遮挡时角度会跳
- 单阈值对**高个子/矮个子**不自适应，标准是写死的 100°/160°
- 30 FPS 下逐帧算，没做**滑动窗口平滑**，边缘帧会抖

**M3 要做的**：
- [ ] 双腿取置信度高的一侧
- [ ] `visibility` 门限 + 5 帧滑动平均
- [ ] 按用户身高自适应阈值（第一次站立 3 秒标定基准角）
- [ ] 手腕 X 坐标 → `pyautogui` 键盘事件 → 玩 Chrome 小恐龙 🦖

---

## 👨‍🎓 关于我

大一 · 专科 · 软件技术 · 河南
方向：**机器视觉应用工程师**（Python + OpenCV → Halcon → 工业现场）
目标：专升本上岸公办本科 → 深圳/苏州/杭州的视觉公司

这个项目是我 2026 年 11 月一个晚上从"6 个报错排到摄像头亮起来"开始的。
`git log` 里每一行 commit 都是真时间戳，欢迎翻。

---

## 📄 License

MIT —— 随便抄，但抄的时候记得把"踩过的坑"那节也抄走，那才是这仓库最值钱的部分。
