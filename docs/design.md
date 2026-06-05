# HiTrinity — 三位一体智能小车系统设计文档

> 版本: v0.1 (规划阶段)
> 关联项目: [HiJetson](https://github.com/ahlijin/HiJetson) — Jetson Orin Nano 端语音+视觉流水线

---

## 1. 设计目标

打造一个**语音交互的自主导航小车**，能在家居环境中执行语音指令（"过来"、"去厨房看看"、"前面有什么"），同时完成：

- 实时目标检测 (YOLO) + 深度感知 (Astra Pro)
- 语音识别 + 大模型应答 + 语音合成 (语音全链路)
- SLAM 自主建图导航
- 户外离线降级运行

---

## 2. 硬件阵容与分工

### 2.1 核心原则

> **什么硬件擅长什么活，就让谁干。**

| 机器 | 核心优势 | 不适合做的 |
|------|---------|-----------|
| Jetson Orin Nano 8GB | CUDA GPU (1024核)，40 TOPS | 大内存任务（仅8GB统一内存） |
| Pi5 8GB | 4×A76 大核，8GB RAM | GPU 加速（VideoCore 对 ML 不可用） |
| Pi3 | 低功耗，GPIO 直连 | 任何计算推理 |

### 2.2 分工矩阵

#### 完整模式 (Pi5 WiFi 在线)

| 模块 | 部署位置 | 资源消耗 | 调度策略 |
|------|---------|----------|---------|
| **YOLOv8n (TensorRT)** | Jetson GPU | ~400MB 常驻 | 30fps，语音交互时降帧腾 GPU |
| **Whisper small** | Jetson GPU | ~1.5GB 脉冲(1~2s) | VAD 触发，GPU 用完即放 |
| **VAD + 音频采集** | Jetson CPU | ~50MB | PulseAudio 常驻 |
| **Fusion Node** | Jetson CPU | ~100MB | 多模态融合 + 模式决策 |
| **ROS2 基础通信** | Jetson CPU | ~100MB | |
| | | | |
| **Cartographer SLAM** | Pi5 CPU (×1核) | ~800MB | 实时 LiDAR 建图定位 |
| **LLM (Qwen2.5-7B Q4)** | Pi5 CPU (×2核) | ~4GB | llama.cpp + Ollama |
| **TTS (Kokoro/Piper)** | Pi5 CPU (×1核) | ~120MB | 离线语音合成 |
| | | | |
| **电机驱动** | Pi3 | <10MB | cmd_vel → PWM |
| **里程计 (odom)** | Pi3 | <10MB | 编码器读数 |
| **LiDAR → scan** | Pi3 | <20MB | 串口 → ROS2 topic |

#### 降级模式 (Pi5 离线, Jetson 全扛)

| 模块 | 切换方式 | 资源消耗 |
|------|---------|---------|
| YOLOv8n | 帧率 30→10fps | ~400MB GPU |
| Whisper small | 保留，触发阈值调高减误唤醒 | 脉冲 ~1.5GB GPU |
| Cartographer SLAM | Pi5 → Jetson CPU 启动 | ~900MB CPU |
| LLM | Qwen2.5-1.5B Q4 (本地 Ollama) | ~1.0GB CPU |
| TTS | Piper TTS 本地 或 简化提示音 | ~80MB CPU |

**降级模式内存预算：**

```
Ubuntu + 桌面 + Hermes          ~2.5GB
YOLOv8n (GPU, 10fps)             ~400MB
Whisper small (GPU, loaded)      ~300MB
Cartographer SLAM (CPU)           ~900MB
Qwen2.5-1.5B Q4 (CPU)           ~1.0GB
Piper TTS (CPU)                   ~80MB
VAD + Fusion + ROS2              ~200MB
────────────────────────────────
基线                              ~5.4GB
Whisper 推理峰值 +0.5GB          ~5.9GB ✅ 余量 ~1GB
```

**关键约束：** 降级模式 LLM 纯 CPU 推理，不 openmp 抢占 GPU，确保 YOLO/Whisper 独占。

---

## 3. 网络拓扑与通信

```
                   室内 (WiFi)                              户外 (无网)
         ┌──────────────────────┐                    ┌─── 小车物理隔离 ───┐
         │      Pi5 (基站)       │                    │                    │
         │  ┌──────────────────┐│                    │  Jetson Orin Nano  │
         │  │ ollama:11434     ││                    │  ┌──────────────┐  │
         │  │ Cartographer     ││  ROS2 / DDS        │  │ 自愈降级      │  │
         │  │ Kokoro TTS       ││◄───────────────────│──┤ FusionNode   │  │
         │  └──────────────────┘│   心跳 1Hz         │  │ 自动切模式    │  │
         └──────────────────────┘                    │  └──────┬───────┘  │
                                                         │      │
                                                    ┌────┘      └────┐
                                                    │ Pi3 (执行层)    │
                                                    │ ┌────────────┐ │
                                                    │ │ 电机驱动    │ │
                                                    │ │ LiDAR 转发  │ │
                                                    │ │ 编码器 odom │ │
                                                    │ └────────────┘ │
                                                    └────────────────┘
```

### 3.1 ROS2 通信

三机通过同一 ROS2 Domain ID (默认或自定义) 组网。Pi5 在家固定，Jetson 随车移动。

**Topic 设计：**

```
# === Jetson 语音流 ===
/voice/audio_raw              - 原始音频
/voice/voice_activity          - VAD 状态
/voice/voice_command           - ASR 识别文本

# === Jetson 视觉流 ===
/vision/detection_result       - YOLO 检测结果
/vision/distance_result        - 深度距离

# === 融合输出 (Jetson) ===
/fusion/result                 - 意图 + 检测 + 距离

# === 模式控制 ===
/system/mode                   - "full" / "degraded"

# === Pi5 基站服务 ===
/pi5/heartbeat                 - 心跳 (1Hz)
/pi5/llm/request               - LLM 请求
/pi5/llm/response              - LLM 回答
/pi5/tts/audio                 - TTS 音频流
/pi5/map_sync                  - 地图同步

# === Pi3 传感器流 ===
/pi3/cmd_vel                   - 速度指令 (发往 Pi3)
/pi3/odom                      - 里程计
/pi3/scan                      - LiDAR 数据
```

### 3.2 Pi5 心跳与模式切换

Pi5 每秒发 `/pi5/heartbeat`。Jetson FusionNode 监听：

- **5秒未收到** → 设置 `/system/mode = "degraded"`
- **重新收到** → 设置 `/system/mode = "full"`

各节点订阅 `/system/mode` 做出相应调整。

---

## 4. 自动降级机制

### 4.1 触发条件

| 事件 | 超时 | 动作 |
|------|------|------|
| Pi5 心跳丢失 | 5s | 标记 degraded |
| Pi5 LLM 请求超时 | 10s | 切换本地 LLM |
| Pi5 地图同步超时 | 30s | 加载本地地图快照 |
| Pi5 恢复心跳 | 连续 3 个心跳 | 切回 full 模式 |

### 4.2 切换时序

```
时间 →
┌─────────────────────────────────────────────────────────┐
│ 模式: FULL                                              │
│ ┌────────┐ ┌────────┐ ┌────────────────────┐            │
│ │Pi5心跳 │ │Pi5心跳 │ │(5s 静默)           │            │
│ └────────┘ └────────┘ └────────────────────┘            │
│                                          ┌─────────────┐│
│                                          │ 模式: DEGRADED │
│                                          │ ┌─────────┐  ││
│                                          │ │YOLO 10fps│  ││
│                                          │ │本地 LLM  │  ││
│                                          │ │CartoSLAM │  ││
│                                          │ │本地 TTS  │  ││
│                                          │ └─────────┘  ││
│                                          └─────────────┘│
└─────────────────────────────────────────────────────────┘
```

### 4.3 SLAM 地图同步

Pi5 每隔 5 秒将 Cartographer 地图序列化为 `.pbstream`，通过 ROS2 topic 发送到 Jetson 保存。户外断联时 Jetson 加载最近的本地地图继续定位。重新联网后将离线期间的变化合并回 Pi5。

---

## 5. GPU 调度策略 (Jetson 侧)

```
空闲期:    YOLO 30fps ──────────────────────────────────────
用户说话:  YOLO → 10fps         Whisper 推理 ═══ 1~2s ═══▶
LLM 推理:  YOLO 15fps          (LLM 在 Pi5/CPU，不抢 GPU)
TTS 播报:  YOLO 30fps          (TTS 在 Pi5/CPU，不抢 GPU)
降级模式:  YOLO 10fps ─── [Whisper 脉冲] ─── [纯 CPU LLM]
```

GPU 同一时刻只为一个脉冲任务服务。YOLO 作为常驻低优先级任务可动态降帧。

---

## 6. 上下文相关的资源分配

| 场景 | YOLO | ASR | LLM | SLAM | TTS |
|------|------|-----|-----|------|-----|
| 待命巡逻 | 30fps | 待触发 | 空闲 | 运行 | 空闲 |
| 用户说"过来" | 30fps→10fps | 正在识别 | 空闲→推理 | 运行 | 空闲→播放 |
| 用户问"前面有什么" | 30fps→10fps | 识别中 | 推理回答 | 运行 | 播放回答 |
| 户外无网 | 10fps | 高阈值 | 1.5B本地 | Jetson本地 | Piper提示音 |
| 充电/空闲 | 5fps省电 | 待触发 | 空闲 | 低功耗模式 | 空闲 |

---

## 7. 规划中的待决事项

- [ ] **SLAM 地图同步格式** — Cartographer pbstream 序列化后的大小和传输方式
- [ ] **Pi3 ROS2 环境** — Pi3 能否跑 ROS2 Humble？（性能够，但需 64-bit OS）
- [ ] **音频回传方式** — Pi5 TTS 生成的 WAV 通过 ROS2 发回 Jetson，还是通过 TCP 流？
- [ ] **降级时 LLM 模型选择** — Qwen2.5-1.5B Q4 实测中文对话效果
- [ ] **开机自启动** — 各机 systemd user service 的编排
- [ ] **Pi5 与 Jetson 的 SSH 密钥配置** — 无密码远程管理
