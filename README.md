# HiTrinity 三位一体智能小车系统

**三机协同 · 语音交互 · 自主导航 · 视觉感知**

HiTrinity 是 HiJetson 的姊妹项目，负责三台设备的编排与协同。

详细设计文档见 [docs/design.md](docs/design.md)。

## 硬件阵容

| 角色 | 设备 | 位置 | 职责 |
|------|------|------|------|
| 主控计算 | Jetson Orin Nano 8GB | 小车上 | GPU：YOLOv8n + Whisper ASR；VAD + 音频 I/O；多模态融合 |
| 基站 | Raspberry Pi 5 8GB | 室内固定 | Cartographer SLAM；LLM 推理 (Qwen2.5)；本地 TTS |
| 执行层 | Raspberry Pi 3 | 小车上 | 电机驱动 (cmd_vel → PWM)；LiDAR 采集转发；编码器里程计 |

## 两套运行模式

| 模式 | 前提 | 能力 |
|------|------|------|
| **完整模式** | Pi5 WiFi 在线 | YOLO 30fps + ASR + SLAM + LLM(7B) + TTS |
| **降级模式** | Pi5 离线 | YOLO 10fps + ASR + CartoSLAM + LLM(1.5B) + Piper TTS |
