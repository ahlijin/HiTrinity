from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg = get_package_share_directory('pi5_llm_bridge')
    cfg = os.path.join(pkg, 'config', 'llm_params.yaml')
    return LaunchDescription([
        Node(package='pi5_llm_bridge', executable='llm_bridge',
             name='llm_bridge', parameters=[cfg], output='screen'),
    ])
