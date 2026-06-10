"""
GPU Scheduler — Dynamically adjusts YOLO frame rate based on system mode
and whether Whisper is actively processing. Publishes target FPS.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String, Bool


class GpuScheduler(Node):
    def __init__(self):
        super().__init__('gpu_scheduler')

        self.declare_parameter('yolo_fps_full', 30)
        self.declare_parameter('yolo_fps_degraded', 10)
        self.declare_parameter('yolo_fps_whisper_active', 10)
        self.declare_parameter('yolo_fps_idle', 5)

        self.fps_full = self.get_parameter('yolo_fps_full').value
        self.fps_degraded = self.get_parameter('yolo_fps_degraded').value
        self.fps_whisper = self.get_parameter('yolo_fps_whisper_active').value
        self.fps_idle = self.get_parameter('yolo_fps_idle').value

        self.current_mode = 'degraded'
        self.whisper_active = False
        self.voice_active = False

        self.create_subscription(String, '/system/mode', self._on_mode, 10)
        self.create_subscription(Bool, '/gpu/whisper_active', self._on_whisper, 10)
        self.create_subscription(Bool, '/voice/voice_activity', self._on_voice, 10)

        self.fps_pub = self.create_publisher(Float32, '/gpu/yolo_target_fps', 10)
        self.create_timer(0.5, self._update_fps)

        self.get_logger().info('GPU scheduler started')

    def _on_mode(self, msg):
        self.current_mode = msg.mode

    def _on_whisper(self, msg):
        self.whisper_active = msg.data

    def _on_voice(self, msg):
        self.voice_active = msg.data

    def _update_fps(self):
        if self.whisper_active:
            fps = self.fps_whisper
        elif self.current_mode == 'degraded':
            fps = self.fps_degraded
        elif self.voice_active:
            fps = self.fps_whisper
        else:
            fps = self.fps_full

        msg = Float32()
        msg.data = float(fps)
        self.fps_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = GpuScheduler()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
