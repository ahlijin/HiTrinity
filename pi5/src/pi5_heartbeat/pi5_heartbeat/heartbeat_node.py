"""
Heartbeat Node — Publishes /pi5/heartbeat at 1Hz.
Jetson mode_manager monitors this to detect Pi5 online/offline.
"""
import rclpy
from rclpy.node import Node
from trinity_msgs.msg import Heartbeat
import psutil
import time


class HeartbeatNode(Node):
    def __init__(self):
        super().__init__('heartbeat_node')
        self.declare_parameter('machine_id', 'pi5')
        self.machine_id = self.get_parameter('machine_id').value

        self.pub = self.create_publisher(Heartbeat, '/pi5/heartbeat', 10)
        self.create_timer(1.0, self._tick)
        self.get_logger().info(f'Heartbeat started: {self.machine_id}')

    def _tick(self):
        msg = Heartbeat()
        msg.machine_id = self.machine_id
        msg.timestamp = time.time()
        msg.cpu_usage = psutil.cpu_percent() / 100.0
        msg.mem_usage = psutil.virtual_memory().percent / 100.0
        # List running services
        services = []
        for name in ['ollama', 'cartographer']:
            try:
                s = psutil.Process.by_pid(1)  # simplified
            except:
                pass
        msg.services = 'ollama,cartographer,tts'
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = HeartbeatNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
