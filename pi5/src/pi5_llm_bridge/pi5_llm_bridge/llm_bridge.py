"""
LLM Bridge — ROS2 service server that forwards requests to Ollama HTTP API.
Runs on Pi5, serves /pi5/llm/request for Jetson fusion_node.
"""
import rclpy
from rclpy.node import Node
from trinity_msgs.srv import LlmRequest
import urllib.request
import json
import time


class LlmBridge(Node):
    def __init__(self):
        super().__init__('llm_bridge')

        self.declare_parameter('ollama_url', 'http://localhost:11434')
        self.declare_parameter('default_model', 'qwen2.5:7b-instruct-q4_K_M')
        self.declare_parameter('fallback_model', 'qwen2.5:1.5b-instruct-q4_K_M')
        self.declare_parameter('max_tokens', 256)
        self.declare_parameter('temperature', 0.7)

        self.ollama_url = self.get_parameter('ollama_url').value
        self.default_model = self.get_parameter('default_model').value
        self.fallback_model = self.get_parameter('fallback_model').value
        self.max_tokens = self.get_parameter('max_tokens').value
        self.temperature = self.get_parameter('temperature').value

        self.srv = self.create_service(LlmRequest, '/pi5/llm/request', self._handle)
        self.get_logger().info(f'LLM bridge ready (ollama: {self.ollama_url})')

    def _handle(self, request, response):
        t0 = time.time()
        model = self.default_model
        if '1.5b' in request.model.lower():
            model = self.fallback_model

        try:
            payload = json.dumps({
                'model': model,
                'prompt': request.prompt,
                'stream': False,
                'options': {
                    'num_predict': self.max_tokens,
                    'temperature': self.temperature,
                }
            }).encode()

            url = f'{self.ollama_url}/api/generate'
            req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
            timeout = request.timeout if request.timeout > 0 else 30.0
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                result = json.loads(resp.read())
                response.response = result.get('response', '')
                response.latency = time.time() - t0
                response.success = True
        except Exception as e:
            self.get_logger().error(f'LLM error: {e}')
            response.response = ''
            response.latency = time.time() - t0
            response.success = False

        return response


def main(args=None):
    rclpy.init(args=args)
    node = LlmBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
