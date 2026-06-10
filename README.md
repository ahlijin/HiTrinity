# HiTrinity — 三位一体智能小车系统

**三机协同 · 语音交互 · 自主导航 · 视觉感知**

HiTrinity 整合 HiJetson（语音管线）与 jetson_ws（导航/SLAM）为统一的三机协同系统。

详细设计文档见 [docs/design.md](docs/design.md)。

## 硬件阵容

| 角色 | 设备 | 位置 | 职责 |
|------|------|------|------|
| **主控计算** | Jetson Orin Nano 8GB | 小车上 | GPU：YOLOv8n + Whisper ASR；VAD + 音频 I/O；多模态融合 |
| **基站** | Raspberry Pi 5 8GB | 室内固定 | Cartographer SLAM；LLM 推理 (Qwen2.5)；本地 TTS |
| **执行层** | Raspberry Pi 3 | 小车上 | 电机驱动 (cmd_vel → PWM)；LiDAR 采集转发；编码器里程计 |

## 两套运行模式

| 模式 | 前提 | 能力 |
|------|------|------|
| **完整模式** | Pi5 WiFi 在线 | YOLO 30fps + ASR + SLAM + LLM(7B) + TTS |
| **降级模式** | Pi5 离线 | YOLO 10fps + ASR + CartoSLAM + LLM(1.5B) + Piper TTS |

## 项目结构

```
HiTrinity/
├── README.md
├── docs/design.md         # 完整架构设计
├── jetson/                # ROS2 工作空间（Jetson Orin Nano）
│   └── src/
│       ├── trinity_msgs/          # 跨机自定义消息（已编译）
│       ├── fusion_node/           # 多模态融合 + 模式管理（已编译）
│       ├── gpu_scheduler/         # GPU 调度器（已编译）
│       ├── trinity_bringup/       # 启动文件（已编译）
│       ├── navigation/            # NAV2 导航配置（已编译）
│       ├── slam/                  # SLAM 节点（已编译）
│       └── ...                    # 来自 HiWonder_JetAuto 的遗留包
├── pi5/                   # ROS2 工作空间（Raspberry Pi 5）
│   └── src/
│       ├── pi5_bringup/           # Pi5 启动编排（已编译）
│       ├── pi5_heartbeat/         # 心跳节点（1Hz）（已编译）
│       ├── pi5_llm_bridge/        # LLM 推理桥接（已编译）
│       └── pi5_tts_bridge/        # TTS 音频桥接（已编译）
├── pi3/                   # ROS2 工作空间（Raspberry Pi 3）
│   └── src/
│       ├── bringup/               # Pi3 启动 + 自检（已编译）
│       ├── controller/            # 电机控制 + 里程计（已编译）
│       ├── peripherals/           # LiDAR/IMU/遥控（已编译）
│       ├── ros_robot_controller/  # 底层硬件驱动（已编译）
│       └── ...                    # IMU校准、舵机控制、描述文件等
└── orchestration/         # [规划中] 跨机编排模块
```

## 编译状态

| 工作空间 | 包数 | 状态 | 说明 |
|---------|------|------|------|
| `jetson/` | 9/9 | ✅ | Python + C++ 混合，含 interfaces/ros_robot_controller_msgs |
| `pi5/`   | 4/4 | ✅ | 纯 Python，心跳/LLM/TTS 桥接 |
| `pi3/`   | 10/10 | ✅ | 含 C++ imu_calib，Eigen 编译通过 |

全部已在 Jetson Orin Nano (ARM64/aarch64) 上编译验证，三机共用同一 ROS2 Humble + `ROS_DOMAIN_ID=42`。

## 快速启动

```bash
# Jetson
cd ~/HiTrinity/jetson
source install/setup.bash
ros2 launch trinity_bringup jetson_bringup.launch.py

# Pi5
cd ~/HiTrinity/pi5
source install/setup.bash
ros2 launch pi5_bringup pi5_bringup.launch.py

# Pi3
cd ~/HiTrinity/pi3
source install/setup.bash
ros2 launch bringup pi3_bringup.launch.py
```

ROS_DOMAIN_ID=42 确保三机在同一 DDS 域中通信。
