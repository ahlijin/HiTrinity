# Changelog

## v0.2.0 (2026-06-10)

### 代码实现 + 全平台编译通过

- **jetson/** — 完整 ROS2 工作空间
  - `trinity_msgs`: 跨机消息定义（FusionResult, Heartbeat, SystemMode, VoiceCommand, LLMRequest/Response, TtsAudio, MapSync）
  - `fusion_node`: 多模态融合节点 + 模式管理器（心跳监听 /system/mode 切换）
  - `gpu_scheduler`: GPU 动态调度器（full 30fps / degraded 10fps / whisper 10fps / idle 5fps）
  - `trinity_bringup`: jetson 启动编排 + 完整/降级双模式 launch
  - 移植 `navigation/`、`slam/`、`interfaces/`、`ros_robot_controller_msgs/` 等依赖包
- **pi5/** — 基站 ROS2 工作空间
  - `pi5_heartbeat`: 1Hz 心跳发布（/pi5/heartbeat）
  - `pi5_llm_bridge`: Ollama LLM 推理桥接（/pi5/llm/request ↔ /pi5/llm/response）
  - `pi5_tts_bridge`: Piper TTS 音频桥接
  - `pi5_bringup`: Pi5 启动编排
- **pi3/** — 执行层 ROS2 工作空间
  - `bringup`: 启动自检 + 全节点编排
  - `controller`: 电机控制（mecanum）、里程计发布（odom_publisher_node）
  - `peripherals`: LiDAR/IMU/遥控手柄支持
  - `ros_robot_controller`: 底层硬件驱动
  - `calibration`: 角速度/线速度标定
  - `servo_controller`: 舵机控制
  - `jetauto_description`: URDF 模型文件
- 三机统一 `ROS_DOMAIN_ID=42`
- 全部 23 个 ROS2 包在 Jetson Orin Nano (ARM64/aarch64) 编译验证通过

## v0.1.0 (2026-06-05)

### 初始规划

- 项目框架搭建
- `docs/design.md` — 完整三机架构设计文档
  - 硬件分工矩阵
  - 完整/降级双模式切换
  - ROS2 Topic 设计
  - GPU 调度策略
  - SLAM 地图同步
