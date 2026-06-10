from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='pi5_tts_bridge', executable='tts_bridge',
             name='tts_bridge', output='screen',
             parameters=[{'engine': 'piper', 'voice': 'zh_CN-huayan-medium', 'play_local': True}]),
    ])
