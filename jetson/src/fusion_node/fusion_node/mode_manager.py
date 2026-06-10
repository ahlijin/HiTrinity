"""
Mode Manager — Monitors Pi5 heartbeat, publishes /system/mode.
Handles automatic full <-> degraded transitions.
"""
import rclpy
from rclpy.node import Node
from trinity_msgs.msg import Heartbeat, SystemMode
import time


class ModeManager(Node):
    def __init__(self):
        super().__init__('mode_manager')

        self.declare_parameter('heartbeat_timeout', 5.0)
        self.declare_parameter('recovery_count', 3)

        self.heartbeat_timeout = self.get_parameter('heartbeat_timeout').value
        self.recovery_count = self.get_parameter('recovery_count').value

        self.current_mode = 'degraded'
        self.last_heartbeat = 0.0
        self.consecutive_ok = 0

        self.create_subscription(Heartbeat, '/pi5/heartbeat', self._on_heartbeat, 10)
        self.mode_pub = self.create_publisher(SystemMode, '/system/mode', 10)

        # Check timer
        self.create_timer(1.0, self._check_mode)

        # Publish initial degraded mode
        self._publish_mode('degraded')
        self.get_logger().info('Mode manager started (initial: degraded)')

    def _on_heartbeat(self, msg: Heartbeat):
        self.last_heartbeat = time.time()
        if self.current_mode == 'degraded':
            self.consecutive_ok += 1
            if self.consecutive_ok >= self.recovery_count:
                self._publish_mode('full')
        else:
            self.consecutive_ok = 0

    def _check_mode(self):
        if self.current_mode == 'full':
            elapsed = time.time() - self.last_heartbeat
            if elapsed > self.heartbeat_timeout:
                self._publish_mode('degraded')
                self.consecutive_ok = 0

    def _publish_mode(self, mode: str):
        self.current_mode = mode
        msg = SystemMode()
        msg.mode = mode
        msg.timestamp = time.time()
        self.mode_pub.publish(msg)
        self.get_logger().info(f'System mode: {mode}')


def main(args=None):
    rclpy.init(args=args)
    node = ModeManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
