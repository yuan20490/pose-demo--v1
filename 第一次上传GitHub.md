# 🚀 第一次上传 GitHub（照抄，10 分钟）

## 第 0 步：先把这 5 个文件放到一个文件夹
新建 `pose-demo/`，把下面这些丢进去：
```
demo.py
squat_logic.py
README.md
requirements.txt
.gitignore
assets/  （两张预览图）
```
⚠️ `pose_landmarker_full.task` **不要传**（.gitignore 已排除，29MB 二进制）。

## 第 1 步：注册（2 分钟）
1. github.com → Sign up
2. 用户名起正经的，跟 4 年：`zhangsan-dev` / `zs-code`（别用 `xiaoaishuai520`）
3. 邮箱用 QQ 就行，验证一下
4. 头像传张干净正脸，Bio 填：`大一 | 河南 | 机器视觉方向 | 把 MediaPipe 玩出花`

## 第 2 步：建仓库（1 分钟）
右上角 **+ → New repository**
- Name: `pose-squat-counter`
- **Public**（必须公开，HR 才看得到）
- ✅ Add a README  ← **先别勾**！我们已有 README.md，勾了会冲突
- Create repository

## 第 3 步：装 Git（1 分钟，只做一次）
https://git-scm.com 下载，一路下一步。
终端验证：`git --version` 能出版本号就行。

## 第 4 步：生成 Token（2 分钟，只做一次）
Mac 现在不允许用密码 push。
GitHub 右上角头像 → **Settings** → 最底下 **Developer settings**
→ **Personal access tokens → Tokens (classic)** → **Generate new token (classic)**
- Note 填：`my-mac`
- 过期选 **No expiration**（或 1 年）
- 只勾 ✅ **repo** 那一个大框
- Generate token → **复制那一串 ghp_ 开头的字符，粘到备忘录**（只显示一次！）

## 第 5 步：推送（3 分钟）
```bash
cd ~/Desktop/pose_demo        # ← 换成你的实际路径

git init
git add .
git commit -m "M0+M1+M2: 姿态识别跑通、自定义渲染、状态机深蹲计数(防抖已验证)"

git branch -M main
git remote add origin https://github.com/你的用户名/pose-squat-counter.git
git push -u origin main
```
弹窗要账号密码时：**账号填 GitHub 用户名，密码粘贴那串 ghp_ token**（不是登录密码）。

刷新仓库页面 → 代码上去了 🎉
README 会自动渲染在下方，配色好看，坑点齐全。

## 第 6 步：以后每次改完代码，就这 3 行（背下来）
```bash
git add .
git commit -m "M3: 手腕坐标映射方向键，能玩小恐龙了"
git push
```
**commit 信息格式**：`里程碑号: 干了啥`
半年后 `git log` 就是一份自动生成的成长报告，面试官爱看这个。

## 🎯 本周验收标准
打开你的 GitHub 主页，能看到：
- ✅ 绿格子（contribution 图亮了 1 格）
- ✅ README 渲染正常，"踩过的坑"那节有 7 条
- ✅ `assets/M1_preview.png` 能点开看到金色骨架

**三样齐全 = 本周满分。** 别加戏。

## ❓ 常见翻车
| 报错 | 原因 | 解法 |
|---|---|---|
| `src refspec main does not match any` | 没 commit 就 push | 先跑 `git commit` |
| `remote origin already exists` | 重复 add 了 | `git remote remove origin` 再来 |
| `Authentication failed` | 密码填了登录密码 | 填 **ghp_ token** |
|  push 上去是空仓库 | 在错误目录 git init | `pwd` 确认在 pose_demo 里 |
| README 里图片裂了 | assets 没一起 add | `git add .` 会带上，检查路径大小写 |
