# -*- coding: utf-8 -*-
# AI 深蹲计数器 M1版 — 自定义渲染 (新版 MediaPipe Tasks API)

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import drawing_utils, drawing_styles
import time
import os

# 1. 指定模型路径
MODEL_PATH = "pose_landmarker_full.task"

# 2. 新版 API 加载模型
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1,
    min_pose_detection_confidence=0.5
)
detector = vision.PoseLandmarker.create_from_options(options)

# 3. 画线样式（金色骨架、加粗、隐藏关节点）
golden_style = drawing_utils.DrawingSpec(color=(0, 215, 255), thickness=4)  # 金色(BGR)
hidden_style = drawing_utils.DrawingSpec(color=(0, 0, 0), thickness=0, circle_radius=0)  # 隐藏关节点

# 4. 打开摄像头
cap = cv2.VideoCapture(0)
print("摄像头已开启，按 q 退出")

counter = 0
stage = None

while True:
    ok, frame = cap.read()
    if not ok:
        break
        
    # 转换颜色空间
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # 获取时间戳
    timestamp_ms = int(time.time() * 1000)
    
    # 5. 检测姿势（新版 API 用 detect_for_video）
    result = detector.detect_for_video(mp_image, timestamp_ms)
    
    # 6. 画骨架（新版 API 用 vision.PoseLandmarksConnections.POSE_LANDMARKS 替代旧的 mp_pose.POSE_CONNECTIONS）
    if result.pose_landmarks:
        for pose_landmarks in result.pose_landmarks:
            drawing_utils.draw_landmarks(
                image=frame,
                landmark_list=pose_landmarks,
                connections=vision.PoseLandmarksConnections.POSE_LANDMARKS,
                landmark_drawing_spec=hidden_style,  # 隐藏关节
                connection_drawing_spec=golden_style   # 金色线条
            )
            
            # （可选）这里可以加你的深蹲角度计算逻辑
            # counter, stage = calculate_squat(pose_landmarks, counter, stage)
            
    # 7. 左上角显示文字
    cv2.putText(frame, "POSE OK - 检测到 1 人", (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 215, 255), 2, cv2.LINE_AA)
    
    # 显示窗口（改成你自己的签名可以把下面的 "YourName" 换掉）
    cv2.setWindowTitle("Pose Demo", "Pose Demo - YourName")
    cv2.imshow("Pose Demo", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


