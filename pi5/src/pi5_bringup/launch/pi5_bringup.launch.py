from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='pi5_heartbeat', executable='heartbeat_node',
             name='heartbeat_node', output='screen',
             parameters=[{'machine_id': 'pi5'}]),
        Node(package='pi5_llm_bridge', executable='llm_bridge',
             name='llm_bridge', output='screen'),
        Node(package='pi5_tts_bridge', executable='tts_bridge',
             name='tts_bridge', output='screen'),
    ])
