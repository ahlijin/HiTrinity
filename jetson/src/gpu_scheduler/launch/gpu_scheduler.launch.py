from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_dir = get_package_share_directory('gpu_scheduler')
    config = os.path.join(pkg_dir, 'config', 'gpu_params.yaml')
    return LaunchDescription([
        Node(package='gpu_scheduler', executable='gpu_scheduler',
             name='gpu_scheduler', parameters=[config], output='screen'),
    ])
