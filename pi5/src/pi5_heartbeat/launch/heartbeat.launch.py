from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='pi5_heartbeat', executable='heartbeat_node',
             name='heartbeat_node', output='screen',
             parameters=[{'machine_id': 'pi5'}]),
    ])
