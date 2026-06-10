from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    fusion_pkg = get_package_share_directory('fusion_node')
    gpu_pkg = get_package_share_directory('gpu_scheduler')

    return LaunchDescription([
        # Jetson nodes
        Node(package='fusion_node', executable='mode_manager',
             name='mode_manager', output='screen'),
        Node(package='gpu_scheduler', executable='gpu_scheduler',
             name='gpu_scheduler', output='screen'),
        Node(package='fusion_node', executable='fusion_node',
             name='fusion_node', output='screen'),
    ])
