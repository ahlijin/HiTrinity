# HiTrinity — 三位一体智能小车系统

## 项目简介
三机协同智能小车系统：Jetson Orin Nano (感知/语音) + Pi5 (LLM/SLAM) + Pi3 (电机控制)。
语音交互 + 自主导航 + 视觉感知 + 大模型应答。

## 硬件阵容
| 角色 | 设备 | 职责 |
|------|------|------|
| **主控计算** | Jetson Orin Nano 8GB | YOLOv8n(30fps) + Whisper ASR + VAD + 多模态融合 |
| **基站** | Raspberry Pi 5 8GB | Cartographer SLAM + LLM (Qwen2.5) + TTS |
| **执行层** | Raspberry Pi 3 | 电机驱动 (cmd_vel→PWM) + LiDAR + 里程计 |

## 两套模式
- **完整模式** (Pi5在线): YOLO 30fps + ASR + SLAM + LLM 7B + TTS
- **降级模式** (Pi5离线): YOLO 10fps + ASR + SLAM + LLM 1.5B + Piper TTS

## 项目结构
```
HiTrinity/
├── docs/design.md               # 完整架构设计
├── jetson/                      # Jetson ROS2 工作空间 (ARM64, 已编译)
│   └── src/
│       ├── trinity_msgs/        # 跨机自定义消息
│       ├── fusion_node/         # 多模态融合 + 模式管理
│       ├── gpu_scheduler/       # GPU 调度器
│       ├── trinity_bringup/     # 启动文件 (launch)
│       ├── navigation/          # NAV2 导航配置
│       ├── slam/                # SLAM 节点
│       ├── jetauto_peripherals/ # Jetson 外设 (键盘/舵机/相机)
│       └── ros_robot_controller_msgs/ # 控制板消息
├── pi5/                         # Pi5 ROS2 工作空间 (已编译)
│   └── src/
│       ├── pi5_bringup/         # Pi5 启动编排
│       ├── pi5_heartbeat/       # 心跳节点 (1Hz)
│       ├── pi5_llm_bridge/      # LLM 推理桥接 (Ollama)
│       └── pi5_tts_bridge/      # TTS 音频桥接
├── pi3/                         # Pi3 ROS2 工作空间 (已编译)
│   └── src/
│       ├── bringup/             # Pi3 启动 + 自检
│       ├── controller/          # 电机控制 + 里程计 (Mecanum)
│       ├── peripherals/         # LiDAR/IMU/手柄/键盘
│       ├── ros_robot_controller/ # 底层硬件驱动
│       ├── sllidar_ros2/        # 激光雷达驱动
│       ├── jetauto_description/ # URDF 模型
│       ├── servo_controller/    # 舵机控制
│       └── calibration/         # 标定
└── orchestration/               # [规划中] 跨机编排
```

## 编码规范
- **语言**: Python 3.10 (大部分节点), C++ (controller, imu_calib, astra_camera)
- **ROS2**: Humble, ROS_DOMAIN_ID=42
- **Python 风格**: PEP 8, 4空格缩进
- **C++ 风格**: Google C++ Style, 2空格缩进
- **ROS2 包**: Python 用 setup.py/setup.cfg, C++ 用 CMakeLists.txt

## 构建与运行
```bash
# 编译前必须 source ROS2 环境
source /opt/ros/humble/setup.bash

# jetson
cd /workspace/HiTrinity/jetson
colcon \
  --log-base /root/build/HiTrinity/jetson/log \
  build \
  --symlink-install \
  --build-base /root/build/HiTrinity/jetson/build \
  --install-base /root/build/HiTrinity/jetson/install \
  --cmake-args "-DCMAKE_C_COMPILER=/usr/bin/gcc" "-DCMAKE_CXX_COMPILER=/usr/bin/g++"

# pi5
cd /workspace/HiTrinity/pi5
colcon \
  --log-base /root/build/HiTrinity/pi5/log \
  build \
  --symlink-install \
  --build-base /root/build/HiTrinity/pi5/build \
  --install-base /root/build/HiTrinity/pi5/install

# pi3
cd /workspace/HiTrinity/pi3
colcon \
  --log-base /root/build/HiTrinity/pi3/log \
  build \
  --symlink-install \
  --build-base /root/build/HiTrinity/pi3/build \
  --install-base /root/build/HiTrinity/pi3/install \
  --cmake-args "-DCMAKE_C_COMPILER=/usr/bin/gcc" "-DCMAKE_CXX_COMPILER=/usr/bin/g++"
# 注: --cmake-args 是 jetson/pi3 需要（有 C++ 包），pi5 纯 Python 可省略
```

## 部署到目标设备
```bash
# Jetson
scp -r /root/build/HiTrinity/jetson/install nvidia@<jetson-ip>:/home/nvidia/HiTrinity/jetson/

# Pi5
scp -r /root/build/HiTrinity/pi5/install pi@<pi5-ip>:/home/pi/HiTrinity/pi5/

# Pi3
scp -r /root/build/HiTrinity/pi3/install pi@<pi3-ip>:/home/pi/HiTrinity/pi3/
```

## 在三机上分别运行
```bash
# Jetson:
cd ~/HiTrinity/jetson && source install/setup.bash
ros2 launch trinity_bringup jetson_bringup.launch.py

# Pi5:
cd ~/HiTrinity/pi5 && source install/setup.bash
ros2 launch pi5_bringup pi5_bringup.launch.py

# Pi3:
cd ~/HiTrinity/pi3 && source install/setup.bash
ros2 launch bringup pi3_bringup.launch.py
```

## 关键消息类型
- `trinity_msgs/VoiceCommand` — 语音指令
- `trinity_msgs/FusionResult` — 多模态融合结果
- `trinity_msgs/SystemMode` — 系统模式切换 (full/degraded)
- `trinity_msgs/LlmResponse` — LLM 回复
- `trinity_msgs/TtsAudio` — TTS 音频
- `trinity_msgs/DetectionResult` — 检测结果
- `trinity_msgs/Heartbeat` — 心跳 (1Hz)
- `trinity_msgs/ObjectInfo` — 目标信息
- `ros_robot_controller_msgs/*` — 控制板状态/指令

## 关键配置
- 融合参数: `jetson/src/fusion_node/config/fusion_params.yaml`
- SLAM 配置: `jetson/src/slam/config/slam.yaml`
- 启动参数: `jetson/src/trinity_bringup/config/trinity_params.yaml`
- ROS_DOMAIN_ID=42 保证三机 DDS 通信

## 注意事项
- Jetson 上 YOLO + Whisper 共享 GPU，语音交互时 YOLO 降帧
- 降级模式 LLM 纯 CPU 推理，不抢占 GPU
- 所有包已在 Jetson Orin Nano (ARM64/aarch64) 上编译验证

## 每日收尾流程
每天工作结束时执行：
```bash
# 1. 查看当天 git 变更
cd /workspace/HiTrinity
git diff --stat

# 2. 确定新版本号 (当前最大版本 + 0.0.1)
#    查看当前版本: ls Changelog/ | sort -V | tail -1

# 3. 更新 Changelog/0.x.x.md
#    格式: "# Changelog / 更新日志\n\n## 版本号 (YYYY-MM-DD)" → 新增 → 改进 → 文件变更 → 验证

# 4. 提交推送
git add -A
git commit -m "chore: release 0.3.0"
git push
```
