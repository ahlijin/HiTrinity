"""
HiTrinity Jetson bringup — launches all Jetson-side nodes:
  - Mode manager (heartbeat monitor)
  - GPU scheduler (YOLO FPS control)
  - Fusion node (multi-modal fusion)
  - Voice pipeline (from HiJetson, if available)
"""
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    fusion_pkg = get_package_share_directory('fusion_node')
    gpu_pkg = get_package_share_directory('gpu_scheduler')
    fusion_cfg = os.path.join(fusion_pkg, 'config', 'fusion_params.yaml')
    gpu_cfg = os.path.join(gpu_pkg, 'config', 'gpu_params.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('voice', default_value='false',
                              description='Include voice pipeline'),
        DeclareLaunchArgument('slam', default_value='false',
                              description='Include SLAM'),

        # Mode manager (always)
        Node(package='fusion_node', executable='mode_manager',
             name='mode_manager', parameters=[fusion_cfg], output='screen'),

        # GPU scheduler (always)
        Node(package='gpu_scheduler', executable='gpu_scheduler',
             name='gpu_scheduler', parameters=[gpu_cfg], output='screen'),

        # Fusion node (always)
        Node(package='fusion_node', executable='fusion_node',
             name='fusion_node', parameters=[fusion_cfg], output='screen'),
    ])
