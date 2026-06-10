"""
TTS Bridge — Subscribes to /pi5/tts/text, generates audio via Piper/Kokoro,
publishes /pi5/tts/audio as TtsAudio msg and plays locally.
"""
import rclpy
from rclpy.node import Node
from trinity_msgs.msg import TtsAudio
from std_msgs.msg import String
import subprocess
import tempfile
import os


class TtsBridge(Node):
    def __init__(self):
        super().__init__('tts_bridge')

        self.declare_parameter('engine', 'piper')  # 'piper' or 'kokoro'
        self.declare_parameter('voice', 'zh_CN-huayan-medium')
        self.declare_parameter('sample_rate', 22050)
        self.declare_parameter('play_local', True)

        self.engine = self.get_parameter('engine').value
        self.voice = self.get_parameter('voice').value
        self.sample_rate = self.get_parameter('sample_rate').value
        self.play_local = self.get_parameter('play_local').value

        self.create_subscription(String, '/pi5/tts/text', self._on_text, 10)
        self.audio_pub = self.create_publisher(TtsAudio, '/pi5/tts/audio', 10)

        self.get_logger().info(f'TTS bridge ready (engine={self.engine})')

    def _on_text(self, msg: String):
        text = msg.data
        if not text:
            return

        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                wav_path = f.name

            if self.engine == 'piper':
                proc = subprocess.run(
                    ['piper', '--model', self.voice, '--output_file', wav_path],
                    input=text.encode(), capture_output=True, timeout=30
                )
            else:  # kokoro
                proc = subprocess.run(
                    ['kokoro', '-m', self.voice, '-o', wav_path],
                    input=text.encode(), capture_output=True, timeout=30
                )

            if os.path.exists(wav_path):
                with open(wav_path, 'rb') as f:
                    audio_data = f.read()

                # Publish
                tts_msg = TtsAudio()
                tts_msg.text = text
                tts_msg.sample_rate = self.sample_rate
                tts_msg.channels = 1
                tts_msg.sample_width = 2
                tts_msg.audio_data = list(audio_data)
                self.audio_pub.publish(tts_msg)

                # Play locally
                if self.play_local:
                    subprocess.Popen(['aplay', '-q', wav_path])

                os.unlink(wav_path)
                self.get_logger().info(f'TTS: "{text[:30]}..."')

        except Exception as e:
            self.get_logger().error(f'TTS error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = TtsBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
