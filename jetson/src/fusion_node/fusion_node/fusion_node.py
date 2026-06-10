"""
Fusion Node — Multi-modal fusion for HiTrinity.
Subscribes to voice commands + vision detection, produces FusionResult.
Publishes /pi5/llm/request to Pi5 for LLM inference in full mode.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from trinity_msgs.msg import (
    VoiceCommand, DetectionResult, FusionResult,
    ObjectInfo, SystemMode, LlmResponse
)
from trinity_msgs.srv import LlmRequest
from std_msgs.msg import Header


class FusionNode(Node):
    def __init__(self):
        super().__init__('fusion_node')

        # Parameters
        self.declare_parameter('llm_enabled', True)
        self.declare_parameter('llm_timeout', 10.0)
        self.declare_parameter('describe_objects', True)

        self.llm_enabled = self.get_parameter('llm_enabled').value
        self.llm_timeout = self.get_parameter('llm_timeout').value

        # State
        self.current_mode = 'full'
        self.last_voice = None
        self.last_detections = None
        self.pending_llm = False

        # QoS
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5
        )

        # Subscribers
        self.create_subscription(VoiceCommand, '/voice/voice_command', self._on_voice, qos)
        self.create_subscription(DetectionResult, '/vision/detection_result', self._on_vision, qos)
        self.create_subscription(SystemMode, '/system/mode', self._on_mode, 10)

        # Publishers
        self.fusion_pub = self.create_publisher(FusionResult, '/fusion/result', 10)

        # LLM client (Pi5 service)
        self.llm_client = self.create_client(LlmRequest, '/pi5/llm/request')

        self.get_logger().info('Fusion node started')

    def _on_mode(self, msg: SystemMode):
        self.current_mode = msg.mode
        self.get_logger().info(f'Mode changed to: {msg.mode}')

    def _on_voice(self, msg: VoiceCommand):
        self.last_voice = msg
        self.get_logger().info(f'Voice: "{msg.raw_text}" intent={msg.intent}')

        # Build fusion result
        result = FusionResult()
        result.header = Header()
        result.header.stamp = self.get_clock().now().to_msg()
        result.intent = msg.intent
        result.mode = self.current_mode

        # Attach latest detections
        if self.last_detections:
            result.objects = self.last_detections.objects
            if result.objects:
                result.distance = min(o.distance for o in result.objects if o.distance > 0)

        # Generate description
        if self.current_mode == 'full' and self.llm_enabled:
            self._request_llm(result, msg)
        else:
            result.description = self._simple_description(msg, result)
            self.fusion_pub.publish(result)

    def _on_vision(self, msg: DetectionResult):
        self.last_detections = msg

    def _request_llm(self, result: FusionResult, voice: VoiceCommand):
        if not self.llm_client.service_is_ready():
            result.description = self._simple_description(voice, result)
            self.fusion_pub.publish(result)
            return

        req = LlmRequest.Request()
        objs = ", ".join(f"{o.class_name}({o.distance:.1f}m)" for o in result.objects)
        req.prompt = f"用户说: \"{voice.raw_text}\"\n检测到: {objs or '无物体'}\n请用简短中文回答。"
        req.model = "qwen2.5-7b"
        req.timeout = self.llm_timeout

        future = self.llm_client.call_async(req)
        future.add_done_callback(lambda f: self._on_llm_response(f, result))

    def _on_llm_response(self, future, result: FusionResult):
        try:
            resp = future.result()
            if resp.success:
                result.description = resp.text
            else:
                result.description = self._simple_description(None, result)
        except Exception as e:
            self.get_logger().warn(f'LLM call failed: {e}')
            result.description = self._simple_description(None, result)
        self.fusion_pub.publish(result)

    def _simple_description(self, voice, result):
        parts = []
        if voice and voice.raw_text:
            parts.append(f'语音: "{voice.raw_text}"')
        if result.objects:
            for obj in result.objects[:3]:
                d = f'{obj.distance:.1f}m' if obj.distance > 0 else ''
                parts.append(f'{obj.class_name} {d}')
        return '; '.join(parts) if parts else '无输入'


def main(args=None):
    rclpy.init(args=args)
    node = FusionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
